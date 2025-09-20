import asyncio
import time
import uuid
from typing import Dict
import aiohttp

from fastapi import HTTPException
from loguru import logger

from env_config import api_config
from utils.generic_functions.common import call_config_validator
from utils.generate_config import generate_runtime_config_object
from voice_services.common import set_runtime_config, get_redis_client
import bot
import bot_with_flows
from voice_services.webcall.webcall_params import WebCallParams
import aiohttp
from pipecat.transports.daily.utils import (
    DailyRESTHelper,
    DailyRoomObject,
    DailyRoomProperties,
    DailyRoomParams,
)
from pipecat.transports.daily.utils import DailyMeetingTokenParams, DailyMeetingTokenProperties

# SmallWebRTC imports (optional - only available if installed)
try:
    from pipecat.transports.network.webrtc_connection import (
        IceServer,
        SmallWebRTCConnection,
    )

    SMALLWEBRTC_AVAILABLE = True
except ImportError:
    SMALLWEBRTC_AVAILABLE = False


class WebCallService:
    def __init__(self):
        self.daily_api_key = api_config.DAILY_API_KEY

    async def create_room_and_tokens(self, call_details: Dict):
        """Create a Daily.co room and generate tokens for bot and user."""
        callback_call_id = call_details.get("call_id")
        log = logger.bind(call_id=callback_call_id)
        room_url = None

        # For webcalls, we need to provide dummy phone number fields that RunConfig requires
        if "from_number" not in call_details and "from" not in call_details:
            call_details["from"] = "webcall"  # Dummy value for webcalls
        if "recipient_phone_number" not in call_details:
            call_details["recipient_phone_number"] = "webcall"  # Dummy value for webcalls

        parsed_config = generate_runtime_config_object(call_details)
        call_config_validator(parsed_config.call_config)

        max_call_length = parsed_config.call_config.max_call_length
        room_name = parsed_config.call_config.room_name
        media_type = parsed_config.call_config.media_type

        # Store call configuration
        await set_runtime_config(callback_call_id, call_details)
        try:
            # Use single aiohttp session for all requests
            async with aiohttp.ClientSession() as session:
                # Create Daily room
                room_response = await self._create_daily_room(
                    session, callback_call_id, max_call_length, room_name, media_type
                )

                room_url = room_response.url

                expiry_minutes = max_call_length // 60

                # Generate tokens with different expiry times
                bot_token = await self._create_daily_token(
                    session,
                    room_url,
                    is_owner=True,
                    user_name="RinggBot",
                    expiry_minutes=expiry_minutes,
                )

                user_token = await self._create_daily_token(
                    session,
                    room_url,
                    is_owner=False,
                    user_name="User",
                    expiry_minutes=expiry_minutes,
                )

            # Create WebCallParams for bot with media type consideration
            webcall_params = WebCallParams(
                media_type="text" if media_type == "text" else "audio",
                room_url=room_url,
                bot_token=bot_token,
                bot_name="RinggBot",
                room_name=room_response.name,  # Include room name for cleanup
            )

            # Launch bot asynchronously
            asyncio.create_task(self._launch_bot(callback_call_id, call_details, webcall_params))

            log.info(f"WebCall room created and bot launched")

            return {
                "status": "success",
                "call_id": callback_call_id,
                "room_url": room_url,
                "token": user_token,  # Return user token for frontend
            }

        except Exception as e:
            log.error(f"Error creating webcall room: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to create webcall room: {str(e)}")

    async def _create_daily_room(
        self,
        session: aiohttp.ClientSession,
        call_id: str,
        max_duration_minutes: int,
        room_name: str,
        media_type: str,
    ) -> DailyRoomObject:
        """Create a Daily.co room via API."""
        daily_helper = DailyRESTHelper(
            daily_api_key=api_config.DAILY_API_KEY, aiohttp_session=session
        )
        room_params = DailyRoomParams(
            name=room_name,
            privacy="private",
            properties=DailyRoomProperties(
                exp=int(time.time()) + (max_duration_minutes * 60),
                max_participants=3,
                enable_chat=media_type == "text",
                start_video_off=True,
                eject_at_room_exp=True,
            ),
        )
        room = await daily_helper.create_room(room_params)
        return room

    async def _create_daily_token(
        self,
        session: aiohttp.ClientSession,
        room_url: str,
        is_owner: bool,
        user_name: str,
        expiry_minutes: int = 15,
    ) -> str:
        """Create a Daily.co meeting token with proper expiry."""

        daily_helper = DailyRESTHelper(daily_api_key=self.daily_api_key, aiohttp_session=session)

        # Import DailyMeetingTokenParams and DailyMeetingTokenProperties for user name

        # Create token parameters with user name only
        # get_token method will set room_name, exp, eject_at_token_exp, and is_owner
        token_params = DailyMeetingTokenParams(
            properties=DailyMeetingTokenProperties(
                user_name=user_name,
            )
        )

        # Create token using DailyRESTHelper
        token = await daily_helper.get_token(
            room_url=room_url,
            expiry_time=expiry_minutes * 60,
            eject_at_token_exp=not is_owner,
            owner=is_owner,
            params=token_params,
        )

        return token

    async def _launch_bot(self, call_id: str, call_details: Dict, webcall_params: WebCallParams):
        """Launch the bot with Daily transport."""
        log = logger.bind(call_id=call_id)

        try:
            redis_client = get_redis_client()

            # Check orchestration mode to determine which bot to use
            orchestration_mode = call_details.get("orchestration_mode", "multi_node")

            if orchestration_mode == "single_node":
                # Use simple bot without flows
                run_bot = bot.run_bot
                log.info(f"Using single_node bot for call {call_id}")
            else:
                # Use bot with flows
                run_bot = bot_with_flows.run_bot
                log.info(f"Using multi_node bot with flows for call {call_id}")

            # Pass WebCallParams to run_bot with explicit channel
            await run_bot(
                websocket_client=None,  # No WebSocket for Daily
                call_id=call_id,
                stream_id=call_id,
                callback_call_id=call_id,
                channel="daily",  # Pass channel directly
                runtime_config=call_details,
                redis_client=redis_client,
                webcall_params=webcall_params,  # Pass as single object
            )

        except Exception as e:
            log.error(f"Error launching bot for webcall: {e}")

    async def delete_room(self, room_name: str) -> bool:
        """Delete a Daily room by name using DailyRESTHelper."""
        try:
            async with aiohttp.ClientSession() as session:
                daily_helper = DailyRESTHelper(
                    daily_api_key=self.daily_api_key, aiohttp_session=session
                )
                return await daily_helper.delete_room_by_name(room_name)
        except Exception:
            return False

    async def create_webrtc_offer(self, request: Dict):
        """Create WebRTC offer endpoint for SmallWebRTC integration."""
        if not SMALLWEBRTC_AVAILABLE:
            raise HTTPException(
                status_code=500,
                detail="SmallWebRTC not available. Install with: pip install 'pipecat-ai[smallwebrtc]'",
            )

        try:
            # Create WebRTC connection
            ice_servers = [IceServer(urls="stun:stun.l.google.com:19302")]
            webrtc_connection = SmallWebRTCConnection(ice_servers)
            await webrtc_connection.initialize(sdp=request["sdp"], type=request["type"])

            # Generate call ID
            call_id = f"webrtc_{uuid.uuid4().hex[:8]}"

            # Create a complete call configuration with flows
            call_details = {
                "call_id": call_id,
                "from": "webrtc",
                "recipient_phone_number": "webrtc",
                "call_type": "webrtc",
                "orchestration_mode": "multi_node",
                "update_call_status_url": "",
                "call_config": {
                    "llm_provider": "openai",
                    "llm_model": "gpt-4o-mini",
                    "llm_temperature": 0.7,
                    "stt_provider": "deepgram",
                    "stt_model": "nova-2",
                    "tts_provider": "elevenlabs",
                    "voice": "Naina",
                    "language": "en-US",
                    "advanced_vad": True,
                    "timezone": "UTC",
                    "max_call_length": 300,
                    "idle_timeout_warning": 30,
                    "idle_timeout_end": 60,
                    "voicemail": {"detect": False, "action": "continue", "retry": False},
                    "voice_config": {"gender": "female", "speed": 1.0},
                    "telephony_provider": "smallwebrtc",
                    "record_locally": True,
                    "mute_during_intro": True,
                    "media_type": "audio",
                },
                "flow_config": {
                    "initial_node": "main",
                    "nodes": {
                        "main": {
                            "context_strategy": {"strategy": "append"},
                            "role_messages": [],
                            "task_messages": [
                                {
                                    "role": "system",
                                    "content": "You are a helpful AI assistant. Have a natural conversation with the user. Keep responses concise and engaging.",
                                }
                            ],
                            "predefined_tools": [],
                            "pre_actions": [
                                {
                                    "type": "tts_say",
                                    "text": "Hello! How can I help you today?",
                                    "use_cache": False,
                                    "mirror_context": True,
                                }
                            ],
                            "post_actions": [],
                            "functions": [],
                            "transition_functions": [],
                            "respond_immediately": True,
                        }
                    },
                },
            }

            parsed_config = generate_runtime_config_object(call_details)
            call_config_validator(parsed_config.call_config)

            # Store call configuration
            await set_runtime_config(call_id, call_details)

            # Launch bot asynchronously with SmallWebRTC
            asyncio.create_task(self._launch_webrtc_bot(call_id, call_details, webrtc_connection))

            logger.info(f"WebRTC connection established for call_id: {call_id}")
            return webrtc_connection.get_answer()

        except Exception as e:
            logger.error(f"WebRTC offer error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _launch_webrtc_bot(self, call_id: str, call_details: Dict, webrtc_connection):
        """Launch the bot with SmallWebRTC transport."""
        log = logger.bind(call_id=call_id)

        try:
            redis_client = get_redis_client()

            # Create WebCallParams for SmallWebRTC
            webcall_params = WebCallParams(
                media_type="audio",  # SmallWebRTC is audio-based
                room_url="webrtc://local",  # Dummy URL for WebRTC
                bot_token="webrtc_token",  # Dummy token
                bot_name="RinggBot",
                room_name=None,  # No room cleanup needed for WebRTC
            )

            # Pass WebRTC connection and call SmallWebRTC directly
            await run_bot(
                websocket_client=None,  # No WebSocket for WebRTC
                call_id=call_id,
                stream_id=f"webrtc_{call_id}",
                callback_call_id=call_id,
                channel="smallwebrtc",  # Use SmallWebRTC channel
                runtime_config=call_details,
                redis_client=redis_client,
                webcall_params=webcall_params,
                webrtc_connection=webrtc_connection,  # Pass WebRTC connection
            )

        except Exception as e:
            log.error(f"Error launching WebRTC bot: {e}")
