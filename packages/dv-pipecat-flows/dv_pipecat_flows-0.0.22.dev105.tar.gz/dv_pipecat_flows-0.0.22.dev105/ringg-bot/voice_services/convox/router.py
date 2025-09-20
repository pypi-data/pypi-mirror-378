import urllib.parse

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from loguru import logger

from voice_services.convox.convox_service import ConvoxService

router = APIRouter(prefix="/convox", tags=["convox"])


@router.post("/call")
async def make_convox_call(request: Request, convox_service: ConvoxService = Depends()):
    """Initiate a ConVox call."""
    try:
        call_details = await request.json()
        print(f"ConVox make_call request body: {call_details}")
        callback_call_id = call_details.get("call_id")
        
        result = await convox_service.make_outbound_call(call_details)
        return result
        
    except HTTPException as e:
        logger.error(f"HTTPException in make_convox_call: {e}", call_id=callback_call_id)
        raise e
    except Exception as e:
        logger.error(f"Exception in make_convox_call: {e}", call_id=callback_call_id)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/callback")
async def convox_callback(
    request: Request,
    callback_call_id: str = Query(None),
    convox_service: ConvoxService = Depends()
):
    """Handle ConVox call status callbacks."""
    try:
        logger.info(f"ConVox callback for call_id: {callback_call_id}")
        request_body = await request.json()
        logger.info(f"ConVox callback for call_id: {callback_call_id}, body: {request_body}")
        
        result = await convox_service.handle_callback(request_body, callback_call_id)
        return result
        
    except Exception as e:
        logger.error(f"Error in ConVox callback: {e}", call_id=callback_call_id)
        return {"status": "error", "message": str(e)}


@router.post("/status")
async def convox_status_callback(
    request: Request,
    update_call_status_url: str = Query(None),
    callback_call_id: str = Query(None),
    convox_service: ConvoxService = Depends()
):
    """Handle ConVox call status updates."""
    try:
        request_body = await request.json()
        logger.info(f"ConVox status callback for call_id: {callback_call_id}, body: {request_body}")
        
        result = await convox_service.handle_status_callback(
            request_body, callback_call_id, update_call_status_url
        )
        return result
        
    except Exception as e:
        logger.error(f"Error in ConVox status callback: {e}", call_id=callback_call_id)
        return {"status": "error", "message": str(e)}