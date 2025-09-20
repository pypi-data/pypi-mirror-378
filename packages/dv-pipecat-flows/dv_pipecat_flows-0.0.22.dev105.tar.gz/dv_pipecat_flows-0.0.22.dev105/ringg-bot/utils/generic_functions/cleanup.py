import asyncio
import json
from typing import Any, Dict, List, Literal, Optional

import aiohttp
from env_config import api_config
from pydantic import BaseModel

from pipecat.frames.frames import CancelFrame
from utils.metrics_collector import get_metrics_collector, clear_metrics_collector

from ..call_status import update_call_status
from ..transcript import (
    TranscriptHandler,
    store_transcript,
)  # noqa: D100
from voice_services.webcall.webcall_params import WebCallParams
from utils.constants import MONITOR_VOICEMAIL_DETECTED


class CallCompletionRequest(BaseModel):
    call_id: str  # Can be UUID or call_sid
    call_sid: str  # Add this field for telephony provider's call ID
    status: Literal["completed"]
    call_duration: float
    transcript: str  # Stringified JSON array of transcript objects
    functions_called: Optional[List[str]] = None
    voicemail_detected: Optional[bool] = False
    metrics: Optional[Dict[str, Any]] = None


async def fetch_column_value(table_name: str, primary_id: str, column_name: list[str], logger):
    logger.info(f"Fetching column value for call {primary_id} from table {table_name}")
    url = f"{api_config.CALLING_BACKEND_URL}/external_hook/fetch_column_value"
    payload = {"table_name": table_name, "column_info": {"id": primary_id, "values": column_name}}
    headers = {
        "X-API-KEY": api_config.CALLING_BACKEND_API_KEY,
        "Content-Type": "application/json",
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status != 200:
                    logger.error(
                        "Failed API call. Status: {}, Response: {}",
                        response.status,
                        await response.text(),
                    )
                    return {}
                response_data = await response.json()
                return response_data
    except Exception as e:
        logger.exception(f"Error in fetch_column_value: {str(e)}")
        return {}


async def update_db(table_name: str, primary_id: str, column_values: dict[str, Any], logger):
    url = f"{api_config.CALLING_BACKEND_URL}/external_hook/update_db"

    payload = {
        "table_name": table_name,
        "update_info": [{"id": primary_id, "values": column_values}],
    }

    headers = {
        "X-API-KEY": api_config.CALLING_BACKEND_API_KEY,
        "Content-Type": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                return True
            else:
                logger.error(f"{primary_id} Failed to update db: {response.text}")
                return False


async def call_completion(
    call_id: str,
    call_sid: str,
    call_duration: float,
    transcript: str,
    functions_called: Optional[List[str]] = None,
    voicemail_detected: Optional[bool] = False,
    metrics: Optional[Dict[str, Any]] = None,
    logger=None,
):
    """Send call completion data to the new /call_completion endpoint."""
    url = f"{api_config.CALLING_BACKEND_URL}/external_hook/call_completion"

    payload = CallCompletionRequest(
        call_id=call_id,
        call_sid=call_sid,  # Pass the call_sid
        status="completed",
        call_duration=call_duration,
        transcript=transcript,
        functions_called=functions_called,
        voicemail_detected=voicemail_detected,
        metrics=metrics,
    )

    headers = {
        "X-API-KEY": api_config.CALLING_BACKEND_API_KEY,
        "Content-Type": "application/json",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload.model_dump(), headers=headers) as response:
                if response.status == 200:
                    if logger:
                        logger.info(f"Call completion data sent successfully for {call_id}")
                    return True
                else:
                    error_msg = f"Failed to send call completion data for {call_id}. Status: {response.status}, Response: {await response.text()}"
                    if logger:
                        logger.error(error_msg)
                    else:
                        print(f"ERROR: {error_msg}")
                    return False
    except Exception as e:
        error_msg = f"Error in call_completion: {str(e)}"
        if logger:
            logger.exception(error_msg)
        else:
            print(f"ERROR: {error_msg}")
        return False


async def cleanup_connection(
    callback_call_id,
    call_id,
    context_aggregator,
    transcript_handler: TranscriptHandler,
    task,
    task_references,
    function_call_monitor,
    logger,
    record_locally=False,
    telephony_provider=None,
    call_duration=None,
    webcall_params: Optional[WebCallParams] = None,
):
    # await task.queue_frame(CancelFrame())
    logger.info(f"Performing connection cleanup for {callback_call_id}", call_id=callback_call_id)

    # Task cancellation with timeout to prevent hanging on ElevenLabs WebSocket close issues
    try:
        await asyncio.wait_for(task.cancel(), timeout=60.0)
        logger.debug(
            f"Task cancelled successfully for {callback_call_id}", call_id=callback_call_id
        )
    except asyncio.TimeoutError:
        logger.warning(
            f"Task cancellation timed out after 10s for {callback_call_id}. "
            "This may be due to WebSocket close frame issues (ElevenLabs TTS). Proceeding with cleanup.",
            call_id=callback_call_id,
        )
    except Exception as e:
        logger.error(
            f"Error during task cancellation for {callback_call_id}: {e}. Proceeding with cleanup.",
            call_id=callback_call_id,
        )

    # Prepare transcript history
    if transcript_handler.messages:
        history = [
            {"role": msg.role, "content": msg.content} for msg in transcript_handler.messages
        ]
    else:
        history = context_aggregator.assistant().context.get_messages_for_persistent_storage()

    # Task 1: Store transcript first
    transcript_stored = await store_transcript(callback_call_id, history, record_locally)

    # Task 2: Send call completion data
    async def send_call_completion():
        voicemail_detected = False
        if function_call_monitor:
            # Check if voicemail was detected
            voicemail_detected = MONITOR_VOICEMAIL_DETECTED in function_call_monitor
            if voicemail_detected:
                logger.info("voicemail was detected during the call")

        functions_called_list = list(function_call_monitor) if function_call_monitor else []

        metrics_data = None
        metrics_collector = get_metrics_collector()
        if metrics_collector:
            try:
                metrics_data = metrics_collector.get_aggregated_metrics()
                logger.info(f"Collected metrics data: {metrics_data}")
            except Exception as e:
                logger.error(f"Failed to collect metrics for call {callback_call_id}: {e}")
            finally:
                clear_metrics_collector()

        logger.info(f"Functions called: {functions_called_list}")

        success = await call_completion(
            call_id=callback_call_id,  # Our internal call ID
            call_sid=call_id,  # Telephony provider's call ID
            call_duration=call_duration or 0.0,
            transcript=json.dumps(transcript_stored) if transcript_stored else "[]",
            functions_called=functions_called_list,
            voicemail_detected=voicemail_detected,
            metrics=metrics_data,
            logger=logger,
        )
        return success

    await send_call_completion()
    logger.debug(
        f"Stored transcript with length: {len(history)}, success: {True if transcript_stored else False}",
        call_id=callback_call_id,
    )

    # Cancel remaining tasks (not parallelizable due to dependency on task_references list)
    for t in task_references:
        logger.debug("Cancelling new bot tasks", call_id=callback_call_id)
        t.cancel()
    task_references.clear()

    # Handle Daily room cleanup for webcalls
    if telephony_provider == "daily" and webcall_params and webcall_params.room_name:
        try:
            # Import locally to avoid circular import
            from voice_services.webcall.webcall_service import WebCallService

            webcall_service = WebCallService()
            success = await webcall_service.delete_room(webcall_params.room_name)
            if success:
                logger.info(
                    f"Daily room deleted successfully: {webcall_params.room_name}",
                    call_id=callback_call_id,
                )
            else:
                logger.warning(
                    f"Failed to delete Daily room: {webcall_params.room_name}",
                    call_id=callback_call_id,
                )
        except Exception as e:
            logger.error(
                f"Error deleting Daily room {webcall_params.room_name}: {e}",
                call_id=callback_call_id,
            )

    if telephony_provider == "convox":
        try:
            await update_call_status(callback_call_id, "completed", telephony_provider)
        except Exception as e:
            logger.error(
                f"Failed to update call status for {callback_call_id}: {e}",
                call_id=callback_call_id,
            )
