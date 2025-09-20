import urllib.parse
from typing import Dict, Optional

from env_config import api_config
from fastapi import HTTPException
from loguru import logger
from utils.generic_functions.common import call_config_validator
from utils.generate_config import generate_runtime_config_object
from utils.http_client import create_http_client_session

from voice_services.common import get_websocket_connections, set_runtime_config


class ConvoxService:
    def __init__(self):
        self.ngrok_url = api_config.NGROK_URL
        self.calling_backend_url = api_config.CALLING_BACKEND_URL

    async def make_outbound_call(self, call_details: Dict):
        """Make an outbound ConVox call."""
        callback_call_id = call_details.get("call_id")
        parsed_config = generate_runtime_config_object(call_details)
        call_config_validator(parsed_config.call_config)

        convox_api_url = api_config.CONVOX_API_URL
        convox_api_key = api_config.CONVOX_API_KEY

        max_call_length = call_details.get("call_config").get("max_call_length", 240)
        encoded_call_id = urllib.parse.quote(callback_call_id)

        update_call_status_url = call_details.get("update_call_status_url")

        await set_runtime_config(callback_call_id, call_details)

        wss_ngrok_url = self.ngrok_url.replace("https:", "wss:") + "/pc/v1/ws"
        wss_ngrok_url += f"?callback_call_id={encoded_call_id}"

        convox_payload = {
            "from": call_details.get("from"),
            "to": call_details.get("recipient_phone_number"),
            "webhook_url": wss_ngrok_url,
            "max_duration": max_call_length,
            "callback_url": f"{self.ngrok_url}/pc/v1/convox/callback?callback_call_id={encoded_call_id}",
        }

        if update_call_status_url:
            encoded_update_call_status_url = urllib.parse.quote(update_call_status_url)
            convox_payload["status_callback"] = (
                f"{self.ngrok_url}/pc/v1/convox/status?update_call_status_url={encoded_update_call_status_url}&callback_call_id={encoded_call_id}"
            )

        headers = {"Authorization": f"Bearer {convox_api_key}", "Content-Type": "application/json"}

        async with create_http_client_session() as session:
            async with session.post(
                convox_api_url, json=convox_payload, headers=headers
            ) as response:
                if response.status == 200:
                    response_data = await response.json()
                    call_sid = response_data.get("call_id")
                    logger.info(
                        f"ConVox call initiated successfully. Call ID: {call_sid}",
                        call_id=callback_call_id,
                    )
                    return {"status": "success", "call_id": call_sid}
                else:
                    error_message = await response.text()
                    logger.error(
                        f"Error initiating ConVox call: {error_message}", call_id=callback_call_id
                    )
                    raise HTTPException(status_code=response.status, detail=error_message)

    async def handle_callback(self, request_body: Dict, callback_call_id: str):
        """Handle ConVox call status callbacks"""
        call_status = request_body.get("status")
        call_id = request_body.get("call_id", callback_call_id)

        if call_status in ["completed", "failed", "no-answer", "busy"]:
            websocket_connections = get_websocket_connections()
            if callback_call_id in websocket_connections:
                websocket = websocket_connections[callback_call_id]
                await websocket.close()
                del websocket_connections[callback_call_id]
                logger.info(f"ConVox WebSocket connection closed for {callback_call_id}")

        return {"status": "success"}

    async def handle_status_callback(
        self, request_body: Dict, callback_call_id: str, update_call_status_url: Optional[str]
    ):
        """Handle ConVox call status updates."""
        call_status = request_body.get("status")
        call_id = request_body.get("call_id", callback_call_id)

        if update_call_status_url:
            url = update_call_status_url.format(callback_call_id)

            status_payload = {
                "call_id": callback_call_id,
                "status": call_status,
                "call_provider": "convox",
                "call_provider_call_id": call_id,
            }

            async with create_http_client_session() as session:
                async with session.patch(url, json=status_payload) as response:
                    if response.status == 200:
                        response_json = await response.json()
                        logger.info(
                            f"ConVox status update successful: {response_json}",
                            call_id=callback_call_id,
                        )
                    else:
                        response_text = await response.text()
                        logger.error(
                            f"ConVox status update failed: {response_text}",
                            call_id=callback_call_id,
                        )

        return {"status": "success"}
