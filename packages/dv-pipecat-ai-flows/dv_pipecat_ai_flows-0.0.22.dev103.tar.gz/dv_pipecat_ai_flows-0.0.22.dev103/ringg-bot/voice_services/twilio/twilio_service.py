import asyncio
import urllib.parse
from typing import Dict, Optional

import aiohttp
from fastapi import HTTPException
from loguru import logger
from starlette.websockets import WebSocketState

from env_config import api_config
from voice_services.common import get_websocket_connections, set_runtime_config
from utils.generic_functions.common import call_config_validator
from utils.generate_config import generate_runtime_config_object
from utils.http_client import create_http_client_session
from utils.rate_limiter import (
    CircuitBreakerError,
    RetryWithExponentialBackoff,
    with_twilio_rate_limiting_and_circuit_breaker,
)
from utils.twilio_async_client import AsyncTwilioAPIError, create_twilio_call


class TwilioService:
    def __init__(self):
        self.ngrok_url = api_config.NGROK_URL
        self.calling_backend_url = api_config.CALLING_BACKEND_URL

    async def make_outbound_call(self, call_details: Dict):
        """Make an outbound Twilio call"""
        call_id = call_details.get("call_id")
        parsed_config = generate_runtime_config_object(call_details)
        call_config_validator(parsed_config.call_config)

        update_call_status_url = call_details.get("update_call_status_url")
        max_call_length = parsed_config.call_config.max_call_length
        encoded_call_id = urllib.parse.quote(call_id)
        twilio_record = not parsed_config.call_config.record_locally

        encoded_update_call_status_url = urllib.parse.quote(update_call_status_url)
        await set_runtime_config(call_id, call_details)

        answer_url = f"{self.ngrok_url}/pc/v1/start_call?callback_call_id={encoded_call_id}&max_call_length={max_call_length}&record={twilio_record}&telephony_source=twilio"
        status_url = f"{self.ngrok_url}/pc/v1/twilio/call_status?update_call_status_url={encoded_update_call_status_url}&callback_call_id={encoded_call_id}"

        retry_handler = RetryWithExponentialBackoff(
            max_attempts=api_config.TELEPHONY_RETRY_MAX_ATTEMPTS,
            initial_delay=api_config.TELEPHONY_RETRY_INITIAL_DELAY,
            max_delay=api_config.TELEPHONY_RETRY_MAX_DELAY,
            exponential_base=api_config.TELEPHONY_RETRY_EXPONENTIAL_BASE,
        )

        async def make_twilio_call():
            return await create_twilio_call(
                account_sid=api_config.TWILIO_ACCOUNT_SID,
                auth_token=api_config.TWILIO_AUTH_TOKEN,
                from_=call_details.get("from"),
                to=call_details.get("recipient_phone_number"),
                url=answer_url,
                record=twilio_record,
                status_callback=status_url,
                status_callback_event=[
                    "initiated",
                    "ringing",
                    "answered",
                    "completed",
                    "failed",
                    "no-answer",
                ],
                status_callback_method="POST",
                time_limit=max_call_length,
            )

        try:
            twilio_response = await retry_handler.execute(
                lambda: with_twilio_rate_limiting_and_circuit_breaker(make_twilio_call()),
                retryable_exceptions=(AsyncTwilioAPIError, Exception),
            )

            logger.info(
                f"Twilio call initiated successfully to {call_details.get('recipient_phone_number')} (SID: {twilio_response.get('sid')})",
                call_id=call_id,
            )
        except CircuitBreakerError:
            logger.error(f"Circuit breaker open - Twilio API unavailable", call_id=call_id)
            raise HTTPException(status_code=503, detail="Telephony service temporarily unavailable")
        except AsyncTwilioAPIError as e:
            logger.error(f"Twilio API error in make_call_via_twilio: {e}", call_id=call_id)
            if e.status_code >= 500:
                raise HTTPException(status_code=503, detail="Telephony service error")
            elif e.status_code == 429:
                raise HTTPException(
                    status_code=429, detail="Rate limit exceeded, please retry later"
                )
            elif e.status_code >= 400:
                raise HTTPException(status_code=400, detail=f"Invalid request: {e.message}")
            else:
                raise HTTPException(status_code=500, detail="Telephony service error")

    async def handle_call_status(
        self,
        callback_call_id: str,
        call_sid: str,
        call_status: str,
        call_ended: bool,
        update_call_status_url: Optional[str],
    ):
        """Handle Twilio call status updates"""
        try:
            if update_call_status_url:
                logger.info(
                    f"Update call status URL: {update_call_status_url}", call_id=callback_call_id
                )
                url = update_call_status_url.format(callback_call_id)
                request_body = {
                    "call_id": callback_call_id,
                    "status": call_status,
                    "call_provider": "twilio",
                    "call_provider_call_id": call_sid,
                }

                async with create_http_client_session() as session:
                    async with session.patch(url, json=request_body) as response:
                        if response.status == 200:
                            response_json = await response.json()
                            res_message = response_json.get("message", "no message found")
                        else:
                            response_text = await response.text()
                            res_message = f"{response_text}"
                        res_message = res_message.replace("{", "").replace("}", "")
                        logger.info(
                            f"Ringing callback Response status: {response.status}, Response body: {res_message}",
                            call_id=callback_call_id,
                        )

            # Handle websocket closure if call has ended
            if call_ended:
                try:
                    websocket_connections = get_websocket_connections()
                    if callback_call_id:
                        websocket = websocket_connections.get(callback_call_id)
                        if websocket and websocket.application_state != WebSocketState.DISCONNECTED:
                            await websocket.close()
                            logger.info(
                                f"WebSocket connection closed for callback_call_id: {callback_call_id}",
                                call_id=callback_call_id,
                            )
                except Exception as e:
                    logger.warning("Websocket might be already closed", call_id=callback_call_id)

        except Exception as e:
            logger.error(
                "Exception occurred in updating status call back", call_id=callback_call_id
            )
