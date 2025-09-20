from fastapi import APIRouter, Query, WebSocket
from loguru import logger
from starlette.websockets import WebSocketDisconnect

from websocket.websocket_service import WebSocketService

router = APIRouter(tags=["websocket"])


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket, callback_call_id: str = Query(None), websocket_service=None
):
    """Unified WebSocket endpoint for all telephony providers"""
    if websocket_service is None:
        websocket_service = WebSocketService()

    await websocket.accept()

    try:
        await websocket_service.handle_connection(websocket, callback_call_id)
    except WebSocketDisconnect as e:
        if e.code == 1000:
            logger.info("WebSocket closed normally", call_id=callback_call_id)
        else:
            logger.warning("WebSocket closed abnormally: {}", str(e), call_id=callback_call_id)
    except Exception as e:
        logger.exception(
            "Unhandled error in websocket_endpoint: {}", str(e), call_id=callback_call_id
        )
    finally:
        await websocket_service.cleanup_connection(callback_call_id)


@router.websocket("/ext/ws")
async def external_websocket_endpoint(
    websocket: WebSocket,
    telephony: str = Query(None),
    agent_id: str = Query(None),
    websocket_service=None
):
    """WebSocket endpoint for external clients with Ringg AI WebSocket API support"""
    if websocket_service is None:
        websocket_service = WebSocketService()

    # Check for required parameters for custom telephony
    if telephony == "custom" and not agent_id:
        logger.error("agent_id is required for custom telephony")
        await websocket.close(code=1008, reason="agent_id parameter is required")
        return

    await websocket.accept()
    logger.info(f"External WebSocket connection accepted - telephony: {telephony}, agent_id: {agent_id}")
    call_id = None

    try:
        call_id = await websocket_service.handle_external_connection(websocket, telephony, agent_id)
    except Exception as e:
        logger.error(f"Error in external WebSocket connection: {str(e)}", flush=True, call_id=call_id)
        await websocket.close()
    finally:
        if call_id:
            await websocket_service.cleanup_connection(call_id)
            logger.info(f"Removed external connection {call_id} from tracking.", call_id=call_id)


@router.websocket("/exotel/ws")
async def exotel_websocket_endpoint(
    websocket: WebSocket,
    callback_call_id: str = Query(None, alias="CustomField"),
    websocket_service=None,
):
    """WebSocket endpoint for Exotel"""
    if websocket_service is None:
        websocket_service = WebSocketService()

    await websocket.accept()
    logger.info(f"Exotel WebSocket connection accepted for {callback_call_id}")

    try:
        await websocket_service.handle_exotel_connection(websocket, callback_call_id)
    except WebSocketDisconnect as e:
        if e.code == 1000:
            logger.info("WebSocket closed normally", call_id=callback_call_id)
        else:
            logger.warning("WebSocket closed abnormally: {}", str(e), call_id=callback_call_id)
    except Exception as e:
        logger.exception(
            "Unhandled error in exotel_websocket_endpoint: {}", str(e), call_id=callback_call_id
        )
    finally:
        await websocket_service.cleanup_connection(callback_call_id)


@router.websocket("/convox/ws")
async def convox_websocket_endpoint(websocket: WebSocket, websocket_service=None):
    """ConVox WebSocket endpoint for real-time audio streaming."""
    if websocket_service is None:
        websocket_service = WebSocketService()

    await websocket.accept()
    logger.info(f"ConVox WebSocket connection accepted")

    final_call_id = None

    try:
        final_call_id = await websocket_service.handle_convox_connection(websocket)
    except WebSocketDisconnect as e:
        if e.code == 1000:
            logger.info("ConVox WebSocket closed normally", call_id=final_call_id or "unknown")
        else:
            logger.warning(
                f"ConVox WebSocket closed abnormally: {e}", call_id=final_call_id or "unknown"
            )
    except Exception as e:
        logger.exception(
            f"Error in ConVox WebSocket endpoint: {e}", call_id=final_call_id or "unknown"
        )
    finally:
        if final_call_id:
            await websocket_service.cleanup_connection(final_call_id)
            logger.info(
                f"ConVox cleanup completed for call_id: {final_call_id}", call_id=final_call_id
            )


@router.websocket("/asterisk/ws")
async def asterisk_websocket_endpoint(
    websocket: WebSocket,
    call_id: str = Query(...),
    encoding: str = Query("pcmu"),  # "pcmu" or "pcm16"
    tenant: str = Query("default"),
    provider: str = Query(None),  # Ubona provider
    ubona_did: str = Query(None),  # Ubona DID
    ubona_cli: str = Query(None),  # Ubona CLI
    websocket_service=None,
):
    """WebSocket endpoint for Asterisk calls"""
    if websocket_service is None:
        websocket_service = WebSocketService()

    await websocket.accept()
    logger.info(f"Asterisk WebSocket connection accepted for call_id: {call_id}")

    final_call_id = None

    try:
        final_call_id = await websocket_service.handle_asterisk_connection(
            websocket=websocket,
            call_id=call_id,
            encoding=encoding,
            tenant=tenant,
            provider=provider,
            ubona_did=ubona_did,
            ubona_cli=ubona_cli,
        )
    except Exception as e:
        logger.exception(
            "Unhandled error in asterisk websocket endpoint: {}", str(e), call_id=call_id
        )
    finally:
        if final_call_id:
            await websocket_service.cleanup_connection(final_call_id)
            logger.info(
                f"Asterisk cleanup completed for call_id: {final_call_id}", call_id=final_call_id
            )
