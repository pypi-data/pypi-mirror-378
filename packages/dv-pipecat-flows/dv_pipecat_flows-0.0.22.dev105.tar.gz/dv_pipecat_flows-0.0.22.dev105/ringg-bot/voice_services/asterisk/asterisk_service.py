"""Asterisk ARI service for handling outbound calls."""

from fastapi import HTTPException
from loguru import logger

from utils.asterisk_ari_client import create_asterisk_call, AsyncAsteriskARIError
from utils.generic_functions.common import call_config_validator
from voice_services.common import set_runtime_config
from utils.rate_limiter import RetryWithExponentialBackoff, CircuitBreakerError
from env_config import api_config
import traceback


class AsteriskService:
    """Service class for handling Asterisk ARI operations."""

    async def make_outbound_call(self, call_details: dict) -> dict:
        """Initiate an Asterisk ARI outbound call."""
        try:
            print(f"Asterisk make_call request body: {call_details}")
            call_id = call_details.get("call_id")

            # Validate call configuration
            call_config_validator(call_details.get("call_config"))

            # Extract call details
            to_number = call_details.get("recipient_phone_number")
            from_number = call_details.get("from")
            from_name = call_details.get("from_name", "Default")  # Optional display name
            endpoint = call_details.get("endpoint", "default_trunk")  # SIP trunk/endpoint
            max_call_length = call_details.get("call_config").get("max_call_length", 240)

            # Prepare ARI variables
            codec = "pcmu"

            variables = {
                "X_TENANT": call_details.get("tenant", "default"),
                "X_CODEC": codec,
                "X_SR": str(call_details.get("sample_rate", 8000)),
                "X_FROM_E164": from_number,
                "X_FROM_NAME": from_name or "",
                "CALLERID(num)": from_number,
                "X_CALL_ID": call_id,
            }

            # Add caller name if provided
            if from_name:
                variables["CALLERID(name)"] = from_name

            # Build caller ID for ARI
            caller_id = from_number if not from_name else f"{from_name} <{from_number}>"

            # Handle E.164 format for tabby endpoints (remove + prefix)
            formatted_number = to_number
            if "tabby" in endpoint.lower() and to_number.startswith("+"):
                formatted_number = to_number[1:]

            # Build dial URI - assuming PJSIP/{number}@{endpoint} format
            dial_uri = f"PJSIP/{formatted_number}@{endpoint}"

            # Debug logging
            logger.debug("Prepared ARI variables: {}", variables, call_id=call_id)
            logger.debug(
                f"ARI call params - endpoint: {dial_uri}, app: {api_config.ASTERISK_ARI_APP}, caller_id: {caller_id}, app_args: {call_id}",
                call_id=call_id,
            )

            # Set call config in Redis with codec information
            call_config = call_details.get("call_config", {})
            call_config["codec"] = codec
            await set_runtime_config(call_id, call_config)

            # Initialize retry mechanism with configured parameters
            retry_handler = RetryWithExponentialBackoff(
                max_attempts=1,
                initial_delay=api_config.TELEPHONY_RETRY_INITIAL_DELAY,
                max_delay=api_config.TELEPHONY_RETRY_MAX_DELAY,
                exponential_base=api_config.TELEPHONY_RETRY_EXPONENTIAL_BASE,
            )

            # Async Asterisk ARI call
            async def make_ari_call():
                return await create_asterisk_call(
                    ari_url=api_config.ASTERISK_ARI_URL,
                    username=api_config.ASTERISK_ARI_USER,
                    password=api_config.ASTERISK_ARI_PASS,
                    endpoint=dial_uri,
                    app=api_config.ASTERISK_ARI_APP,
                    caller_id=caller_id,
                    variables=variables,
                    app_args=call_id,  # Pass call_id as app argument
                    timeout=max_call_length,
                )

            # Execute with retry logic
            asterisk_response = await retry_handler.execute(
                make_ari_call,
                retryable_exceptions=(AsyncAsteriskARIError,),
            )

            logger.info(
                f"Asterisk ARI call originated successfully to {to_number} (Channel: {asterisk_response.get('channel_id')})",
                call_id=call_id,
            )

            return {"status": "success", "channel_id": asterisk_response.get("channel_id")}

        except HTTPException as e:
            logger.error(f"HTTPException in make_asterisk_call: {e}", call_id=call_id)
            raise e
        except CircuitBreakerError:
            logger.error(f"Circuit breaker open - Asterisk ARI unavailable", call_id=call_id)
            raise HTTPException(status_code=503, detail="Asterisk service temporarily unavailable")
        except AsyncAsteriskARIError as e:
            logger.error(f"Asterisk ARI error in make_asterisk_call: {e}", call_id=call_id)

            # Handle timeout errors specially
            if hasattr(e, "error_code") and e.error_code in ["TIMEOUT", "CLIENT_ERROR"]:
                logger.warning(f"Call may have succeeded despite timeout error", call_id=call_id)
                raise HTTPException(
                    status_code=202, detail="Call initiated - outcome uncertain due to timeout"
                )

            # Map ARI errors to appropriate HTTP status codes
            if e.status_code >= 500:
                raise HTTPException(status_code=503, detail="Asterisk service error")
            elif e.status_code == 429:
                raise HTTPException(
                    status_code=429, detail="Rate limit exceeded, please retry later"
                )
            elif e.status_code >= 400:
                raise HTTPException(status_code=400, detail=f"Invalid request: {e.message}")
            else:
                raise HTTPException(status_code=500, detail="Asterisk service error")
        except Exception as e:
            print(traceback.format_exc())
            logger.error(f"Unexpected exception in make_asterisk_call: {e}", call_id=call_id)
            raise HTTPException(status_code=500, detail="Internal Server Error")
