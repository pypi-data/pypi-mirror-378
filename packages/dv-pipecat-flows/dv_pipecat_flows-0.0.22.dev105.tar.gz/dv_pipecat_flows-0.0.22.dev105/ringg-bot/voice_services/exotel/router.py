import traceback
import urllib.parse

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from loguru import logger
from starlette.responses import PlainTextResponse

from voice_services.exotel.exotel_service import ExotelService

router = APIRouter(prefix="/exotel", tags=["exotel"])


@router.post("/call")
async def make_exotel_call(request: Request, exotel_service: ExotelService = Depends()):
    try:
        call_details = await request.json()
        print(f"make_call request body:{call_details}")
        callback_call_id = call_details.get("call_id")

        result = await exotel_service.make_outbound_call(call_details)
        return result

    except HTTPException as e:
        logger.exception("Exception occurred in make_call", call_id=callback_call_id)
        raise e
    except Exception as e:
        logger.exception("Exception occurred in make_call", call_id=callback_call_id)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/inbound")
async def exotel_inbound_call(request: Request, exotel_service: ExotelService = Depends()):
    try:
        request_query = request.query_params
        call_sid = request_query.get("CallSid")
        call_from = request_query.get("CallFrom")
        call_to = request_query.get("CallTo")
        client = request_query.get("client")
        language = request_query.get("language")
        digits = request_query.get("digits")

        if digits is not None:
            digits = digits.replace('"', "").strip()

        result = await exotel_service.handle_inbound_call(
            call_sid=call_sid,
            call_from=call_from,
            call_to=call_to,
            client=client,
            language=language,
            digits=digits,
        )

        return result

    except Exception as e:
        traceback_str = traceback.format_exc()
        logger.exception(f"Error in exotel_inbound_call: {e} \n with traceback: {traceback_str}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/callback")
@router.get("/callback")
async def exotel_hangup_callback(
    request: Request,
    update_call_status_url: str = Query(None),
    callback_call_id: str = Query(None),
    exotel_service: ExotelService = Depends(),
):
    request_form = await request.form()
    request_query = request.query_params
    logger.info(f"Exotel callback request body for call_id: {callback_call_id} is {request_form}")
    logger.info(
        f"Query params: {request.query_params} \n {update_call_status_url} \n {callback_call_id}"
    )

    await exotel_service.handle_callback(
        request_form=request_form,
        request_query=request_query,
        update_call_status_url=update_call_status_url,
        callback_call_id=callback_call_id,
    )

    return PlainTextResponse("", status_code=200)
