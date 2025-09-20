import asyncio
import os
import re
import traceback
import urllib.parse
from typing import Dict, Optional

import aiohttp
from env_config import api_config
from fastapi import HTTPException
from loguru import logger
from starlette.websockets import WebSocketState
from voice_services.common import (
    delete_call_config,
    get_redis_client,
    get_websocket_connections,
    set_runtime_config,
)
from utils.generic_functions.common import call_config_validator
from utils.generate_config import generate_runtime_config_object
from utils.http_client import create_http_client_session
from utils.plivo_async_client import AsyncPlivoAPIError, create_plivo_call
from utils.rate_limiter import (
    CircuitBreakerError,
    RetryWithExponentialBackoff,
    with_plivo_rate_limiting_and_circuit_breaker,
)
from utils.transcript import get_transcript_url


class PlivoService:  # noqa: D101
    def __init__(self):  # noqa: D107
        self.ngrok_url = api_config.NGROK_URL
        self.calling_backend_url = api_config.CALLING_BACKEND_URL

    async def handle_inbound_hangup(self, call_sid: str, call_status: str, call_sub_status: str):
        """Handle inbound Plivo hangup callback."""
        await delete_call_config(call_sid)
        transcript = get_transcript_url(call_sid)

        url = f"{self.calling_backend_url}/calling/inbound/status"
        logger.info(
            f"Status update payload: url {url}; callback_call_id {call_sid}, {call_status}",
            call_id=call_sid,
        )

        async with create_http_client_session() as session:
            async with session.patch(
                url,
                json={
                    "call_sid": call_sid,
                    "status": call_status,
                    "sub_status": call_sub_status,
                    "call_provider": "plivo",
                    "transcript": transcript,
                },
            ) as response:
                logger.info("Got response for plivo_hangup_callback to backend", call_id=call_sid)
                if response.status == 200:
                    response_json = await response.json()
                    res_message = response_json.get("message", "no message found")
                else:
                    response_text = await response.text()
                    res_message = f"{response_text}"
                res_message = res_message.replace("{", "").replace("}", "")
                logger.info(
                    f"Hangup callback Response status: {response.status}, Response body {res_message}",
                    call_id=call_sid,
                )

    async def generate_capture_extension_xml(self, query_params: Dict) -> str:
        """Generate XML for capturing extension digits."""
        url_string = f"{self.ngrok_url}/pc/v1/inbound_call"

        params = []
        for key, value in query_params.items():
            params.append(f"{key}={value}")

        if params:
            url_string += "?" + "&".join(params)

        response_str = f"""
        <Response>
            <GetDigits action="{url_string}" method="POST" numDigits="4">
            </GetDigits>
        </Response>
        """
        return response_str

    async def handle_inbound_call(
        self,
        from_number: str,
        to_number: str,
        call_sid: str,
        client: Optional[str] = None,
        digits: Optional[str] = None,
    ) -> str:
        """Handle inbound Plivo call and return appropriate XML response."""
        url = f"{self.calling_backend_url}/calling/inbound"

        params = []
        if digits is not None:
            params.append(f"digits={digits}")
        if client is not None:
            params.append(f"client={client}")

        if params:
            url = f"{url}?{'&'.join(params)}"

        logger.info(
            f"Data received: from_number={from_number}, to_number={to_number}, call_sid={call_sid}, url= {url}, digits= {digits}",
            call_id=call_sid,
        )

        async with create_http_client_session() as session:
            async with session.post(
                url,
                json={"from_number": from_number, "to_number": to_number, "call_sid": call_sid},
            ) as response:
                try:
                    response.raise_for_status()
                    call_details = await response.json()
                    logger.info(
                        "Ringing callback Response status: {}, Response body: {}",
                        response.status,
                        call_details,
                        call_id=call_sid,
                    )
                except aiohttp.ClientResponseError as cre:
                    if 400 <= cre.status < 500:
                        with open("templates/plivo-hangup.xml") as f:
                            hangup_xml = f.read()
                        logger.warning(
                            f"Returning Plivo Hangup XML due to 4xx from backend: {cre.status}",
                            call_id=call_sid,
                        )
                        return hangup_xml
                    else:
                        raise

        parsed_config = generate_runtime_config_object(call_details)
        call_config_validator(parsed_config.call_config)
        max_call_length = parsed_config.call_config.max_call_length
        encoded_call_sid = urllib.parse.quote(call_sid)

        await set_runtime_config(call_sid, call_details)

        wss_ngrok_url = self.ngrok_url.replace("https:", "wss:") + "/pc/v1/ws"
        if not max_call_length:
            max_call_length = 240

        wss_ngrok_url += f"?callback_call_id={encoded_call_sid}"

        logger.info(f"Encoded wss_ngrok_url: {wss_ngrok_url}", call_id=call_sid)

        record_locally = parsed_config.call_config.record_locally
        record_session = "false" if record_locally else "true"

        with open("templates/plivo-stream.xml") as f:
            formated_xml = f.read().format(
                ngrok_url=wss_ngrok_url,
                max_call_length=max_call_length,
                record_session=record_session,
            )

        return formated_xml

    async def make_outbound_call(self, call_details: Dict):
        """Make an outbound Plivo call."""
        call_id = call_details.get("call_id")
        parsed_config = generate_runtime_config_object(call_details)
        call_config_validator(parsed_config.call_config)

        update_call_status_url = call_details.get("update_call_status_url")
        max_call_length = parsed_config.call_config.max_call_length
        encoded_call_id = urllib.parse.quote(call_id)
        record = parsed_config.call_config.record_locally

        if update_call_status_url:
            encoded_update_call_status_url = urllib.parse.quote(update_call_status_url)
            await set_runtime_config(call_id, call_details)
            answer_url = f"{self.ngrok_url}/pc/v1/plivo/start_call?callback_call_id={encoded_call_id}&max_call_length={max_call_length}&record={record}&telephony_source=plivo"
            hangup_url = f"{self.ngrok_url}/pc/v1/plivo/hangup_callback?update_call_status_url={encoded_update_call_status_url}&callback_call_id={encoded_call_id}"
            ring_url = f"{self.ngrok_url}/pc/v1/plivo/ring_call?update_call_status_url={encoded_update_call_status_url}&callback_call_id={encoded_call_id}"
        else:
            await set_runtime_config(call_id, call_details)
            answer_url = f"{self.ngrok_url}/pc/v1/plivo/start_call?callback_call_id={encoded_call_id}&record={record}&telephony_source=plivo"
            hangup_url = (
                f"{self.ngrok_url}/pc/v1/plivo/hangup_callback?callback_call_id={encoded_call_id}"
            )
            ring_url = f"{self.ngrok_url}/pc/v1/plivo/ring_call?callback_call_id={encoded_call_id}"

        retry_handler = RetryWithExponentialBackoff(
            max_attempts=api_config.TELEPHONY_RETRY_MAX_ATTEMPTS,
            initial_delay=api_config.TELEPHONY_RETRY_INITIAL_DELAY,
            max_delay=api_config.TELEPHONY_RETRY_MAX_DELAY,
            exponential_base=api_config.TELEPHONY_RETRY_EXPONENTIAL_BASE,
        )

        async def make_plivo_call():
            return await create_plivo_call(
                auth_id=api_config.PLIVO_AUTH_ID,
                auth_token=api_config.PLIVO_AUTH_TOKEN,
                from_=call_details.get("from"),
                to_=call_details.get("recipient_phone_number"),
                answer_url=answer_url,
                hangup_url=hangup_url,
                ring_url=ring_url,
                answer_method="POST",
            )

        try:
            plivo_response = await retry_handler.execute(
                lambda: with_plivo_rate_limiting_and_circuit_breaker(make_plivo_call()),
                retryable_exceptions=(AsyncPlivoAPIError),
            )

            logger.info(
                f"Plivo call initiated successfully to {call_details.get('recipient_phone_number')}",
                call_id=call_id,
            )
        except CircuitBreakerError:
            logger.error(f"Circuit breaker open - Plivo API unavailable", call_id=call_id)
            raise HTTPException(status_code=503, detail="Telephony service temporarily unavailable")
        except AsyncPlivoAPIError as e:
            logger.error(f"Plivo API error in make_call: {e}", call_id=call_id)
            # Map Plivo API errors to appropriate HTTP status codes
            if e.status_code >= 500:
                # Handle timeout errors specially to indicate potential success
                if hasattr(e, "error_code") and e.error_code in ["TIMEOUT", "RESPONSE_TIMEOUT"]:
                    logger.warning(
                        f"Call may have succeeded despite timeout error", call_id=call_id
                    )
                    # Return 202 (Accepted) to indicate the request was processed but outcome is uncertain
                    raise HTTPException(
                        status_code=202, detail="Call initiated - outcome uncertain due to timeout"
                    )
                # Map other Plivo API errors to appropriate HTTP status codes
            elif e.status_code >= 500:
                raise HTTPException(status_code=503, detail="Telephony service error")
            elif e.status_code == 429:
                raise HTTPException(
                    status_code=429, detail="Rate limit exceeded, please retry later"
                )
            elif e.status_code >= 400:
                raise HTTPException(status_code=400, detail=f"Invalid request: {e.message}")
            else:
                raise HTTPException(status_code=500, detail="Telephony service error")
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.error(f"Network/timeout error in make_call: {e}", call_id=call_id)
            raise HTTPException(status_code=503, detail="Telephony service timeout")
        except Exception as e:
            logger.error(f"Unexpected exception occurred in make_call: {e}", call_id=call_id)
            raise HTTPException(status_code=500, detail="Internal Server Error")

    async def generate_start_call_xml(
        self, callback_call_id: str, max_call_length: Optional[int], record_locally: bool = False
    ) -> str:
        """Generate XML for starting a Plivo call."""
        wss_ngrok_url = self.ngrok_url.replace("https:", "wss:") + "/pc/v1/ws"
        if not max_call_length:
            max_call_length = 240

        encoded_call_id = urllib.parse.quote(callback_call_id)
        wss_ngrok_url += f"?callback_call_id={encoded_call_id}&amp;telephony_source=plivo"

        record_session = "false" if record_locally else "true"

        templates_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates"
        )
        template_path = os.path.join(templates_dir, "plivo-stream.xml")
        with open(template_path) as f:
            template_content = f.read()

        logger.info(f"encoded wss_ngrok_url: {wss_ngrok_url}", call_id=callback_call_id)

        if record_session == "false":
            template_content = re.sub(r"\s*<Record.*?/>\s*", "\n    ", template_content)

        formatted_xml = template_content.format(
            ngrok_url=wss_ngrok_url,
            max_call_length=max_call_length,
            record_session=record_session,
            callback_call_id=callback_call_id,
            telephony_source="plivo",
        )

        return formatted_xml

    async def handle_ring_callback(
        self, callback_call_id: str, call_uuid: str, update_call_status_url: Optional[str]
    ):
        """Handle Plivo ring callback."""
        logger.info(f"Ringing: Call UUID: {call_uuid}", call_id=callback_call_id)

        if update_call_status_url:
            logger.info(
                f"Update call status URL: {update_call_status_url}", call_id=callback_call_id
            )
            url = update_call_status_url.format(callback_call_id)

            async with create_http_client_session() as session:
                async with session.patch(
                    url,
                    json={
                        "call_id": callback_call_id,
                        "status": "ringing",
                        "call_provider": "plivo",
                        "call_provider_call_id": call_uuid,
                    },
                ) as response:
                    if response.status == 200:
                        response_json = await response.json()
                        res_message = response_json.get("message", "no message found")
                    else:
                        response_text = await response.text()
                        res_message = f"{response_text}"
                    res_message = res_message.replace("{", "").replace("}", "")
                    logger.info(
                        f"Ringing callback Response status: {response.status}, Response body: {res_message}",
                        call_id=callback_call_id,
                    )

    def generate_transfer_xml(self, target: str) -> str:
        """Generate Plivo XML for call transfer."""
        logger.info(f"Generating transfer XML for target: {target}")

        if re.match(r"^sip:.*@.*", target):
            xml_content = f"""
                <Response>
                    <Dial>
                        <Sip>{target}</Sip>
                    </Dial>
                </Response>"""
        else:
            xml_content = f"""
                <Response>
                    <Dial>
                        <Number>{target}</Number>
                    </Dial>
                </Response>"""

        logger.debug(f"Generated XML: {xml_content}")
        return xml_content

    async def handle_hangup_callback(
        self,
        callback_call_id: str,
        call_uuid: str,
        call_status: str,
        call_sub_status: str,
        update_call_status_url: Optional[str],
    ):
        """Handle Plivo hangup callback."""
        try:
            if update_call_status_url:
                url = update_call_status_url.format(callback_call_id)
                logger.info(
                    "Status update payload: url {}, callback_call_id {}, call_status {}, call_uuid {}",
                    str(url),
                    str(callback_call_id),
                    str(call_status),
                    str(call_uuid),
                    call_id=callback_call_id,
                )

                async with create_http_client_session() as session:
                    async with session.patch(
                        url,
                        json={
                            "call_id": callback_call_id,
                            "status": call_status,
                            "sub_status": call_sub_status,
                            "call_provider": "plivo",
                            "call_provider_call_id": call_uuid,
                        },
                    ) as response:
                        response.raise_for_status()
                        if response.status == 200:
                            response_json = await response.json()
                            res_message = response_json.get("message", "no message found")
                        else:
                            response_text = await response.text()
                            res_message = f"{response_text}"
                        res_message = res_message.replace("{", "").replace("}", "")

        except Exception as e:
            logger.exception(f"Error in hangup callback: {e}", call_id=callback_call_id)

        try:
            websocket_connections = get_websocket_connections()
            if callback_call_id:
                websocket = websocket_connections.get(callback_call_id)
                if websocket and websocket.application_state != WebSocketState.DISCONNECTED:
                    await websocket.close()
                    logger.info(
                        f"WebSocket connection closed for callback_call_id: {callback_call_id}",
                        call_id=callback_call_id,
                    )
        except Exception as e:
            logger.warning("Websocket might be already closed", call_id=callback_call_id)
