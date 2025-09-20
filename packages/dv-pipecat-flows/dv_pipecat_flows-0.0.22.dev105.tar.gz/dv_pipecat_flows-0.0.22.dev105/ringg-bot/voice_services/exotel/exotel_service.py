import urllib.parse
import time
from typing import Dict, Optional

import aiohttp
from env_config import api_config
from fastapi import HTTPException
from loguru import logger
from starlette.websockets import WebSocketState
from utils.generic_functions.common import call_config_validator
from utils.generate_config import generate_runtime_config_object
from utils.http_client import create_http_client_session

from voice_services.common import get_websocket_connections, set_runtime_config


class ExotelService:
    def __init__(self):
        self.ngrok_url = api_config.NGROK_URL
        self.calling_backend_url = api_config.CALLING_BACKEND_URL

    async def make_outbound_call(self, call_details: Dict):
        """Make an outbound Exotel call."""
        callback_call_id = call_details.get("call_id")
        parsed_config = generate_runtime_config_object(call_details)
        call_config_validator(parsed_config.call_config)

        exotel_sid = api_config.EXOTEL_SID
        exotel_api_key = api_config.EXOTEL_API_KEY
        exotel_api_token = api_config.EXOTEL_API_TOKEN
        exotel_region = getattr(api_config, "EXOTEL_REGION", "api.exotel.com")
        app_id = api_config.APP_ID

        exotel_api_url = f"https://{exotel_api_key}:{exotel_api_token}@{exotel_region}/v1/Accounts/{exotel_sid}/Calls/connect.json"
        exotel_flow_url = f"http://my.exotel.com/{exotel_sid}/exoml/start_voice/{app_id}"

        time_limit = call_details.get("call_config").get("time_limit", "180")
        encoded_call_id = urllib.parse.quote(callback_call_id)

        update_call_status_url = call_details.get("update_call_status_url")
        encoded_update_call_status_url = urllib.parse.quote(update_call_status_url)

        payload = {
            "From": call_details.get("recipient_phone_number"),
            "CallerId": call_details.get("from"),
            "Url": exotel_flow_url,
            "TimeLimit": time_limit,
            "StatusCallback": f"{self.ngrok_url}/pc/v1/exotel/callback?update_call_status_url={encoded_update_call_status_url}&callback_call_id={encoded_call_id}",
            "CustomField": callback_call_id,
        }

        await set_runtime_config(callback_call_id, call_details)
        logger.info(f"Exotel api url {exotel_api_url}", call_id=callback_call_id)

        async with create_http_client_session() as session:
            async with session.post(exotel_api_url, data=payload) as response:
                if response.status == 200:
                    response_json = await response.json()
                    logger.info(f"Exotel API response: {response_json}")
                    call_sid = response_json["Call"]["Sid"]
                    logger.info(
                        f"Exotel call initiated successfully. Call SID: {call_sid}",
                        call_id=callback_call_id,
                    )
                    return {"status": "success", "call_sid": call_sid}
                else:
                    error_message = await response.text()
                    logger.error(f"Error initiating Exotel call: {error_message}")
                    raise HTTPException(status_code=response.status, detail=error_message)

    async def handle_inbound_call(
        self,
        call_sid: str,
        call_from: str,
        call_to: str,
        client: str,
        language: str,
        digits: Optional[str],
    ):
        """Handle inbound Exotel call."""
        url = f"{self.calling_backend_url}/calling/inbound"
        url = url + f"?client={client}&language={language}&digits={digits}"

        async with create_http_client_session() as session:
            async with session.post(
                url,
                json={"from_number": call_from, "to_number": call_to, "call_sid": call_sid},
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
                        logger.warning(
                            f"Returning Exotel Hangup XML due to 4xx from backend: {cre.status}",
                            call_id=call_sid,
                        )
                        return None
                    else:
                        raise

        parsed_config = generate_runtime_config_object(call_details)
        call_config_validator(parsed_config.call_config)
        encoded_call_sid = urllib.parse.quote(call_sid)

        await set_runtime_config(call_sid, call_details)

        wss_ngrok_url = f"{self.ngrok_url}/pc/v1/ws"
        wss_ngrok_url = wss_ngrok_url.replace("https:", "wss:")
        wss_ngrok_url += f"?callback_call_id={encoded_call_sid}"

        logger.info(f"Encoded wss_ngrok_url: {wss_ngrok_url}", call_id=call_sid)

        return {"url": wss_ngrok_url}

    async def handle_callback(
        self,
        request_form,
        request_query,
        update_call_status_url: Optional[str],
        callback_call_id: str,
    ):
        start_time = time.time()  # Track API start time
        # add any post call hangup processing
        call_sid = request_form.get("CallSid")  # Extract call SID from form data

        try:
            if update_call_status_url:
                url = update_call_status_url.format(callback_call_id)
                call_status = request_form.get("Status")
                logger.info(
                    f"Status update payload: url {url}; callback_call_id {callback_call_id}, {call_status}, {call_sid}"
                )
                async with create_http_client_session() as session:
                    async with session.patch(
                        url,
                        json={
                            "call_id": callback_call_id,
                            "status": call_status,
                            "call_provider": "exotel",
                            "call_provider_call_id": call_sid,
                        },
                    ) as response:
                        logger.info(
                            "Got response for exotel_hangup_callback to backend",
                            call_id=callback_call_id,
                        )
                        if response.status == 200:
                            response_json = await response.json()
                            res_message = response_json.get("message", "no message found")
                        else:
                            response_text = await response.text()
                            res_message = f"{response_text}"
                        res_message = res_message.replace("{", "").replace("}", "")

                        # Log API completion time for first callback path
                        completion_time = time.time() - start_time
                        logger.info(
                            f"Exotel hangup callback completed - call_sid={call_sid}, completion_time={completion_time:.3f}s, response_status={response.status}, response={res_message}, callback_call_id={callback_call_id}",
                        )

            elif request_query.get("Direction") == "incoming":
                url = f"{self.calling_backend_url}/calling/inbound/status"
                logger.info(f"Request query for exotel inbound: {dict(request_query)}")
                call_status = request_query.get("Stream[Status]")

                if call_status:
                    recording_url = request_query.get("Stream[RecordingUrl]") or request_query.get(
                        "RecordingUrl"
                    )
                    duration = request_query.get("Stream[Duration]") or request_query.get(
                        "DialCallDuration"
                    )
                    call_sid = request_query.get("CallSid")

                    async with create_http_client_session() as session:
                        async with session.patch(
                            url,
                            json={
                                "call_sid": call_sid,
                                "status": call_status,
                                "call_provider": "exotel",
                                "recording_url": recording_url,
                                "duration": duration,
                            },
                        ) as response:
                            logger.info(
                                "Got response for exotel_hangup_callback to backend",
                                call_id=call_sid,
                            )
                            if response.status == 200:
                                response_json = await response.json()
                                res_message = response_json.get("message", "no message found")
                            else:
                                response_text = await response.text()
                                res_message = f"{response_text}"
                            res_message = res_message.replace("{", "").replace("}", "")

                            # Log API completion time for incoming status callback
                            completion_time = time.time() - start_time
                            logger.info(
                                f"Exotel inbound status callback completed - call_sid={call_sid}, completion_time={completion_time:.3f}s, response_status={response.status}, response={res_message}, callback_call_id={callback_call_id}"
                            )

        except Exception as e:
            # Log API completion time even for failures
            completion_time = time.time() - start_time
            logger.error(
                f"Exotel hangup callback failed - call_sid={call_sid}, callback_call_id={callback_call_id}, completion_time={completion_time:.3f}s, error={e}"
            )
            logger.exception(f"Error in hangup callback {callback_call_id}: {e}")
        try:
            if callback_call_id:
                websocket = get_websocket_connections().get(callback_call_id)
                if websocket and websocket.application_state != WebSocketState.DISCONNECTED:
                    await websocket.close()
                    logger.info(
                        f"WebSocket connection closed for callback_call_id: {callback_call_id}"
                    )
                    del get_websocket_connections()[callback_call_id]
        except Exception as e:
            logger.warning("Websocket might be already closed", call_id=callback_call_id)

        # Log final completion time if not logged earlier (for successful cases without specific callbacks)
        if "completion_time" not in locals():
            completion_time = time.time() - start_time
            logger.info(
                f"Exotel callback completed - call_sid={call_sid}, callback_call_id={callback_call_id}, completion_time={completion_time:.3f}s"
            )
