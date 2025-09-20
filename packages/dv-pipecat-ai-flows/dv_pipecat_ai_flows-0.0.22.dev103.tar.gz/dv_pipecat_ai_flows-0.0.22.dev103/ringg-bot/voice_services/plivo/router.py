import urllib.parse
from urllib.parse import parse_qs

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from loguru import logger
from starlette.responses import HTMLResponse, PlainTextResponse

from voice_services.plivo.plivo_service import PlivoService

router = APIRouter(prefix="/plivo", tags=["plivo"])


@router.post("/inbound_hangup")
async def inbound_plivo_hangup_callback(request: Request, plivo_service: PlivoService = Depends()):
    try:
        request_body = await request.body()
        body_str = request_body.decode("utf-8")
        parsed_params = parse_qs(body_str)
        call_sid = parsed_params.get("CallUUID", [None])[0]
        call_status = parsed_params.get("CallStatus", [None])[0]
        call_sub_status = parsed_params.get("HangupCauseName", [None])[0]

        if call_sub_status and "XML" in call_sub_status:
            call_sub_status = "Normal Hangup"

        await plivo_service.handle_inbound_hangup(call_sid, call_status, call_sub_status)

    except HTTPException as e:
        logger.error(
            f"HTTPException occurred in inbound_plivo_hangup_callback: {e}", call_id=call_sid
        )
        raise e
    except Exception as e:
        logger.error(f"Exception occurred in inbound_plivo_hangup_callback: {e}", call_id=call_sid)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/capture_extention")
@router.post("/capture_extention")
async def capture_extention(request: Request, plivo_service: PlivoService = Depends()):
    query_params = dict(request.query_params)
    logger.info(f"capture_extention query_params: {query_params}")

    response_xml = await plivo_service.generate_capture_extension_xml(query_params)
    return HTMLResponse(response_xml, media_type="application/xml")


@router.post("/inbound_call")
async def make_plivo_inbound_call(request: Request, plivo_service: PlivoService = Depends()):
    try:
        request_body = await request.body()
        body_str = request_body.decode("utf-8")
        parsed_params = parse_qs(body_str)

        from_number = parsed_params.get("From", [None])[0]
        to_number = parsed_params.get("To", [None])[0]
        call_sid = parsed_params.get("CallUUID", [None])[0]
        client = parsed_params.get("client", [None])[0]
        digits = parsed_params.get("Digits", [None])[0]

        response_xml = await plivo_service.handle_inbound_call(
            from_number=from_number,
            to_number=to_number,
            call_sid=call_sid,
            client=client,
            digits=digits,
        )

        return HTMLResponse(response_xml, media_type="application/xml")

    except HTTPException as e:
        logger.exception(f"HTTPException occurred in make_inbound_call", call_id=call_sid)
        raise e
    except Exception as e:
        logger.exception(f"Exception occurred in make_inbound_call", call_id=call_sid)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/call")
async def make_call(request: Request, plivo_service: PlivoService = Depends()):
    try:
        call_details = await request.json()
        call_id = call_details.get("call_id")
        # logger.info(f"make_call request body:{call_details}", call_id=call_id)

        await plivo_service.make_outbound_call(call_details)

    except HTTPException as e:
        logger.error(f"HTTPException occurred in make_call: {e}", call_id=call_id)
        raise e
    except Exception as e:
        logger.error(f"Unexpected exception occurred in make_call: {e}", call_id=call_id)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/start_call")
async def start_call(request: Request, plivo_service: PlivoService = Depends()):
    request_body = await request.body()
    query_params = dict(request.query_params)
    callback_call_id: str = query_params.get("callback_call_id", None)
    max_call_length: int = query_params.get("max_call_length", None)
    telephony_source: str = query_params.get("telephony_source", "plivo")

    if telephony_source != "plivo":
        raise HTTPException(status_code=400, detail="Invalid telephony source for Plivo endpoint")

    formatted_xml = await plivo_service.generate_start_call_xml(
        callback_call_id=callback_call_id,
        max_call_length=max_call_length,
        record_locally=query_params.get("record", "False").lower() == "true",
    )

    return HTMLResponse(formatted_xml, media_type="application/xml")


@router.post("/ring_call")
async def ring_call(request: Request, plivo_service: PlivoService = Depends()):
    request_body = await request.body()
    update_call_status_url: str = request.query_params.get("update_call_status_url", None)
    callback_call_id: str = request.query_params.get("callback_call_id", None)

    logger.info(f"Ring Request body: {request_body}", call_id=callback_call_id)
    parsed_body = parse_qs(request_body.decode())
    call_uuid = parsed_body.get("CallUUID", [None])[0]

    await plivo_service.handle_ring_callback(callback_call_id, call_uuid, update_call_status_url)

    return PlainTextResponse("", status_code=200)


@router.get("/transfer_xml")
async def plivo_transfer_xml(target: str = Query(...), plivo_service: PlivoService = Depends()):
    """Generates Plivo XML to dial a number or SIP endpoint for call transfer."""
    xml_content = plivo_service.generate_transfer_xml(target)
    return HTMLResponse(xml_content.strip(), media_type="application/xml")


@router.post("/hangup_callback")
async def plivo_hangup_callback(
    request: Request,
    update_call_status_url: str = Query(None),
    callback_call_id: str = Query(None),
    plivo_service: PlivoService = Depends(),
):
    request_body = await request.body()
    logger.info(
        f"Plivo hangup callback request body for call_id: {callback_call_id} is {request_body}",
        call_id=callback_call_id,
    )

    parsed_body = parse_qs(request_body.decode())
    call_uuid = parsed_body.get("CallUUID", [None])[0]
    call_status = parsed_body.get("CallStatus", [None])[0]
    call_sub_status = parsed_body.get("HangupCauseName", [None])[0]

    if call_sub_status and "XML" in call_sub_status:
        call_sub_status = "Normal Hangup"

    await plivo_service.handle_hangup_callback(
        callback_call_id=callback_call_id,
        call_uuid=call_uuid,
        call_status=call_status,
        call_sub_status=call_sub_status,
        update_call_status_url=update_call_status_url,
    )

    return PlainTextResponse("", status_code=200)
