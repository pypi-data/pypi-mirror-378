"""Flow-native dtmf_output tool implementation."""

from pipecat_flows import FlowManager
from pipecat_flows.types import FlowResult
import aiohttp
from env_config import api_config
from utils.plivo_utils import create_plivo_basic_auth_header


async def dtmf_output(flow_manager: FlowManager, digits: str) -> FlowResult:
    """
    Sends DTMF tones (digits 0-9, *, #) during the current call. Useful for interacting with IVR systems or entering codes.

    Args:
        digits: The sequence of DTMF digits to send (e.g., '123#'). Allowed characters: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, *, #.

    Returns:
        FlowResult indicating success or failure
    """
    s = flow_manager.state
    logger = s.get("bot_logger")
    provider = s.get("telephony_provider")
    call_id = s.get("call_id")
    monitor = s.get("function_call_monitor", [])

    if logger:
        logger.info(f"Sending DTMF digits: {digits}")
    monitor.append(f"DTMF digits sent: {digits}")

    # Validate digits
    allowed_chars = set("0123456789*#")
    if not set(digits).issubset(allowed_chars):
        if logger:
            logger.error(f"Invalid DTMF digits: {digits}")
        return ({"status": "error", "error": "Invalid DTMF digits"}, None)

    if provider == "plivo":
        # Use Plivo API to send DTMF
        auth_id = api_config.PLIVO_AUTH_ID
        auth_token = api_config.PLIVO_AUTH_TOKEN
        if not all([auth_id, auth_token]):
            if logger:
                logger.error("Plivo credentials not configured")
            return ({"status": "error", "error": "DTMF failed due to configuration issue"}, None)

        url = f"https://api.plivo.com/v1/Account/{auth_id}/Call/{call_id}/DTMF/"
        headers = create_plivo_basic_auth_header(auth_id, auth_token)

        if not headers:
            if logger:
                logger.error("Failed to create Plivo auth headers")
            return ({"status": "error", "error": "DTMF failed due to configuration issue"}, None)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json={"digits": digits}, headers=headers) as resp:
                    if resp.status == 202:
                        if logger:
                            logger.info("DTMF sent via Plivo API")
                        return ({"status": "success", "data": {"sent": digits}}, None)
                    else:
                        if logger:
                            response_text = await resp.text()
                            logger.error(f"Plivo DTMF failed: {resp.status} - {response_text}")
                        return ({"status": "error", "error": "Unable to send DTMF tones"}, None)
        except Exception as e:
            if logger:
                logger.exception(f"Error sending Plivo DTMF: {e}")
            return ({"status": "error", "error": "Unable to send DTMF tones"}, None)
    elif provider == "exotel":
        # Placeholder for Exotel implementation
        if logger:
            logger.warning("DTMF output for Exotel is not yet implemented")
        return ({"status": "skipped", "data": {"message": "DTMF not supported for Exotel"}}, None)
    else:
        if logger:
            logger.warning(f"DTMF output not supported for provider: {provider}")
        return ({"status": "error", "error": f"DTMF not supported for {provider}"}, None)
