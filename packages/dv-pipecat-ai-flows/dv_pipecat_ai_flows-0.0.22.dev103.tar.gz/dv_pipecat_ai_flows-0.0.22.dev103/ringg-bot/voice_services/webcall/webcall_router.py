import asyncio
import uuid
from typing import Dict

from fastapi import APIRouter, HTTPException
from loguru import logger
from starlette.responses import HTMLResponse, RedirectResponse

from voice_services.webcall.webcall_service import WebCallService
from voice_services.common import get_redis_client, set_runtime_config
from bot_with_flows import run_bot

router = APIRouter(prefix="/webcall", tags=["webcall"])
webcall_service = WebCallService()


@router.post("/start")
async def start_webcall(call_details: Dict):
    """Start a webcall session with Daily.co integration."""
    try:
        call_id = call_details.get("call_id")
        if not call_id:
            raise HTTPException(status_code=400, detail="call_id is required")

        logger.info(f"Starting webcall session for call ID: {call_id}")

        result = await webcall_service.create_room_and_tokens(call_details)

        logger.info(f"Webcall session started successfully for call ID: {call_id}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting webcall: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start webcall: {str(e)}")


@router.post("/webrtc/offer")
async def webrtc_offer(request: Dict):
    """WebRTC offer endpoint for SmallWebRTC integration."""
    try:
        logger.info("Received WebRTC offer request")

        result = await webcall_service.create_webrtc_offer(request)

        logger.info("WebRTC offer processed successfully")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing WebRTC offer: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process WebRTC offer: {str(e)}")


@router.get("/webrtc")
async def webrtc_test_page():
    """Simple WebRTC test page."""
    try:
        from pipecat_ai_small_webrtc_prebuilt.frontend import SmallWebRTCPrebuiltUI

        # If the prebuilt UI is available, redirect to it
        return RedirectResponse(url="/client/")
    except ImportError:
        # Simple fallback message
        html = """<!DOCTYPE html>
        <html><head><title>WebRTC Test - Ringg Chatbot</title></head>
        <body>
        <h1>WebRTC Test</h1>
        <p>Please install SmallWebRTC prebuilt UI:</p>
        <code>pip install pipecat-ai-small-webrtc-prebuilt</code>
        </body></html>"""
        return HTMLResponse(html)
