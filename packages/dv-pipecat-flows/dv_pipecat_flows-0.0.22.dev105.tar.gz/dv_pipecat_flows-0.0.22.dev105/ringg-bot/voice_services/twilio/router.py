import urllib.parse
from urllib.parse import parse_qs

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from loguru import logger
from starlette.responses import PlainTextResponse

from voice_services.twilio.twilio_service import TwilioService

router = APIRouter(prefix="/twilio", tags=["twilio"])


@router.post("/call")
async def make_call_via_twilio(request: Request, twilio_service: TwilioService = Depends()):
    try:
        call_details = await request.json()
        print(f"make_call request body:{call_details}")
        call_id = call_details.get("call_id")
        
        await twilio_service.make_outbound_call(call_details)
        
    except HTTPException as e:
        logger.error(f"HTTPException occurred in make_call_via_twilio: {e}", call_id=call_id)
        raise e
    except Exception as e:
        logger.error(f"Unexpected exception occurred in make_call_via_twilio: {e}", call_id=call_id)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/call_status")
async def twilio_call_status(request: Request, twilio_service: TwilioService = Depends()):
    request_body = await request.body()
    request_params = parse_qs(request_body.decode())
    update_call_status_url: str = request.query_params.get("update_call_status_url", None)
    callback_call_id: str = request.query_params.get("callback_call_id", None)
    
    call_sid = request_params.get("CallSid", [None])[0]
    call_status = request_params.get("CallStatus", [None])[0]
    call_ended = False
    
    if call_status in ["completed", "failed", "no-answer"]:
        call_ended = True
    
    await twilio_service.handle_call_status(
        callback_call_id=callback_call_id,
        call_sid=call_sid,
        call_status=call_status,
        call_ended=call_ended,
        update_call_status_url=update_call_status_url
    )
    
    return PlainTextResponse("", status_code=200)