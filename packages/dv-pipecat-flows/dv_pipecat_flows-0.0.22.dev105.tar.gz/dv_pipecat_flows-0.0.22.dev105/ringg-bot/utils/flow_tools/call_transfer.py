"""Flow-native call_transfer tool implementation."""

import urllib.parse
from pipecat_flows import FlowManager
from pipecat_flows.types import FlowResult
import aiohttp
from env_config import api_config
from utils.http_client import create_http_client_session
from utils.plivo_utils import create_plivo_basic_auth_header


async def call_transfer(flow_manager: FlowManager, target: str) -> FlowResult:
    """
    Transfers the current call to a specified PSTN number or SIP endpoint.

    Args:
        target: The destination PSTN number (e.g., '+15551234567') or SIP URI (e.g., 'sip:user@example.com') to transfer the call to.

    Returns:
        FlowResult indicating transfer success or failure
    """
    s = flow_manager.state
    logger = s.get("bot_logger")
    provider = s.get("telephony_provider")
    call_id = s.get("call_id")
    monitor = s.get("function_call_monitor", [])

    monitor.append("call_transfer_called")

    if logger:
        logger.info(f"Attempting to transfer call to {target}")

    if provider == "plivo":
        try:
            auth_id = api_config.PLIVO_AUTH_ID
            auth_token = api_config.PLIVO_AUTH_TOKEN
            ngrok_url = api_config.NGROK_URL

            if not all([auth_id, auth_token, ngrok_url]):
                if logger:
                    logger.error("Plivo credentials or NGROK URL not configured")
                return (
                    {"status": "error", "error": "Transfer failed due to configuration issue"},
                    None,
                )

            # Construct the aleg_url pointing to the XML endpoint
            encoded_target = urllib.parse.quote(target)
            # Using /pc/v1 prefix as established in server.py
            aleg_url = f"{ngrok_url}/pc/v1/plivo/transfer_xml?target={encoded_target}"

            # Plivo API endpoint for transferring a call
            url = f"https://api.plivo.com/v1/Account/{auth_id}/Call/{call_id}/"
            headers = create_plivo_basic_auth_header(auth_id, auth_token)

            if not headers:
                if logger:
                    logger.error("Failed to create Plivo auth headers")
                return (
                    {"status": "error", "error": "Transfer failed due to configuration issue"},
                    None,
                )

            # Payload for call transfer
            payload = {
                "legs": "aleg",
                "aleg_url": aleg_url,
                "aleg_method": "GET",  # Using GET for simplicity for the XML endpoint
            }

            if logger:
                logger.info(f"Calling Plivo Transfer API: {url} with payload: {payload}")

            async with create_http_client_session() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    response_text = await response.text()
                    
                    if 200 <= response.status < 300:
                        if logger:
                            logger.info(
                                f"Plivo transfer API call successful (Status: {response.status}). Response: {response_text}"
                            )
                        
                        monitor.append("call_transfer_called")
                        
                        # Get websocket client from state and close it
                        websocket_client = s.get("websocket_client")
                        if websocket_client:
                            await websocket_client.close()
                        
                        return ({"status": "success", "data": {"transferred_to": target}}, None)
                    else:
                        if logger:
                            logger.error(f"Plivo transfer API call failed (Status: {response.status}). Response: {response_text}")
                        return ({"status": "error", "error": "Unable to transfer call"}, None)

        except Exception as e:
            if logger:
                logger.exception(e)
            return ({"status": "error", "error": "Unable to transfer call"}, None)

    elif provider == "twilio":
        message = "Call transfer for Twilio is not yet implemented"
        if logger:
            logger.warning(message)
        return ({"status": "error", "error": "Transfer not available for this provider"}, None)

    elif provider == "exotel":
        message = "Call transfer for Exotel is not yet implemented"
        if logger:
            logger.warning(message)
        return ({"status": "skipped", "error": message}, None)

    else:
        message = f"Call transfer not supported for telephony provider: {provider}"
        if logger:
            logger.warning(message)
        return ({"status": "skipped", "error": "Call Transfer failed due to technical issues"}, None)
