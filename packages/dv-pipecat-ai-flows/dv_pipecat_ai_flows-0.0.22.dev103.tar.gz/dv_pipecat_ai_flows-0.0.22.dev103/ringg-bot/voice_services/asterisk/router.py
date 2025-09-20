import traceback
from fastapi import APIRouter, Depends, HTTPException, Request
from loguru import logger

from voice_services.asterisk.asterisk_service import AsteriskService
from server import verify_x_api_key_header

router = APIRouter(prefix="/asterisk", tags=["asterisk"])


@router.post("/call", dependencies=[Depends(verify_x_api_key_header)])
async def make_asterisk_call(request: Request, asterisk_service: AsteriskService = Depends()):
    """Initiate an Asterisk ARI outbound call."""
    try:
        call_details = await request.json()
        print(f"Asterisk make_call request body: {call_details}")
        call_id = call_details.get("call_id")

        result = await asterisk_service.make_outbound_call(call_details)
        return result

    except HTTPException as e:
        logger.error(f"HTTPException in make_asterisk_call: {e}", call_id=call_id)
        raise e
    except Exception as e:
        print(traceback.format_exc())
        logger.error(f"Unexpected exception in make_asterisk_call: {e}", call_id=call_id)
        raise HTTPException(status_code=500, detail="Internal Server Error")
