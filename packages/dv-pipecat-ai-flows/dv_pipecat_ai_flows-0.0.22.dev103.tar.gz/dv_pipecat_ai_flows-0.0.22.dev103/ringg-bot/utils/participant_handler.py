import asyncio
import re
from typing import Optional
from loguru import logger
from pipecat.frames.frames import (
    LLMMessagesAppendFrame,
    OutputAudioRawFrame,
    LLMMessagesUpdateFrame,
    TransportMessageUrgentFrame,
    TranscriptionMessage,
    TranscriptionUpdateFrame,
    MixerEnableFrame,
)


class ParticipantHandler:
    """Handles participant lifecycle and audio readiness for all channel types."""

    def __init__(
        self,
        transport,
        channel: str,
        call_config,
        audio_out_sample_rate: int,
        task,
        audio_buffer,
        background_mixer,
        flow_manager,
        bot_logger,
        transcript_handler,
    ):
        self.transport = transport
        self.channel = channel
        self.call_config = call_config
        self.audio_out_sample_rate = audio_out_sample_rate
        self.task = task
        self.audio_buffer = audio_buffer
        self.background_mixer = background_mixer
        self.flow_manager = flow_manager
        self.bot_logger = bot_logger
        self.transcript_handler = transcript_handler

        # State tracking
        self.conversation_started = False
        self.first_user_id = None

    async def _start_conversation_if_needed(self):
        """Initialize the conversation flow once audio is ready."""
        if self.conversation_started:
            return
        self.conversation_started = True

        # Optional: keep small delay
        await asyncio.sleep(0.3)

        # 🔊 prime outbound audio path so first phonemes aren't clipped (only for audio sessions)
        if self.channel == "daily" and self.call_config.media_type != "text":
            await self._prime_output_audio(
                self.transport, self.audio_out_sample_rate, channels=1, ms=800
            )

        # Start recording if enabled
        if self.call_config.record_locally and self.audio_buffer:
            await self.audio_buffer.start_recording()

        # Start background audio if audio ID is provided
        if self.background_mixer and self.call_config.background_audio_config:
            self.bot_logger.info(
                f"Starting background audio with audio ID: {self.call_config.background_audio_config.audio_id if self.call_config.background_audio_config else 'unknown'}"
            )

            # Enable the mixer
            await self.task.queue_frame(MixerEnableFrame(True))

        # Initialize the flow manager to start the conversation flow (if available)
        if self.flow_manager:
            self.bot_logger.info("Initializing flow manager - conversation started")
            await self.flow_manager.initialize()
        else:
            self.bot_logger.info("No flow manager - using legacy bot mode")

    @staticmethod
    def _mic_state(participant: dict) -> str:
        """Get participant's microphone state."""
        return ((participant.get("media") or {}).get("microphone") or {}).get("state")

    def _is_user_participant(self, p: dict) -> bool:
        """Check if participant is a user (not the bot itself)."""
        if (
            hasattr(self.transport, "participant_id")
            and p.get("id") == self.transport.participant_id
        ):
            return False
        name = p.get("info", {}).get("userName") or p.get("user_name") or p.get("name") or ""
        return name != "RinggBot"

    async def _wait_until_mic_playable(self, participant_id: str, timeout=4.0, interval=0.1):
        """Safety net: poll for mic playable state with timeout."""
        end = asyncio.get_event_loop().time() + timeout
        while asyncio.get_event_loop().time() < end:
            p = self.transport.participants().get(participant_id)
            if p and self._mic_state(p) == "playable":
                return True
            await asyncio.sleep(interval)
        return False

    async def _prime_output_audio(
        self, transport, sample_rate: int, channels: int = 1, ms: int = 800
    ):
        """Send ~ms of silence in 20ms chunks to warm the receiver."""
        if sample_rate <= 0:
            self.bot_logger.warning(f"Invalid sample rate for audio priming: {sample_rate}")
            return

        samples_total = int(sample_rate * ms / 1000)
        # 16-bit PCM silence (little-endian); zeros are safe regardless of format
        frame_samples = int(sample_rate / 50)  # 20ms
        if frame_samples <= 0:
            self.bot_logger.warning(f"Invalid frame samples calculated: {frame_samples}")
            return

        chunk_bytes = frame_samples * channels * 2
        if chunk_bytes <= 0:
            self.bot_logger.warning(f"Invalid chunk bytes calculated: {chunk_bytes}")
            return

        silence = b"\x00\x00" * (samples_total * channels)

        for i in range(0, len(silence), chunk_bytes):
            chunk = silence[i : i + chunk_bytes]
            if not chunk:
                break
            frame = OutputAudioRawFrame(audio=chunk, sample_rate=sample_rate, num_channels=channels)
            await transport.send_audio(frame)
            # yield to event loop so Daily can push frames out promptly
            await asyncio.sleep(0)

    def register_event_handlers(self):
        """Register Daily-specific event handlers."""
        if self.channel != "daily":
            return

        @self.transport.event_handler("on_participant_joined")
        async def on_participant_joined(transport, participant, *args, **kwargs):
            if self._is_user_participant(participant):
                self.first_user_id = participant["id"]
                mic_state = self._mic_state(participant)
                self.bot_logger.info(
                    f"First participant joined: {self.first_user_id}, mic={mic_state}"
                )

                # If already playable (rare), start now; else wait for update
                if mic_state == "playable":
                    await self._start_conversation_if_needed()
                else:
                    # Safety net: kick off background wait in case no updated event fires
                    async def _bg():
                        ok = await self._wait_until_mic_playable(participant["id"])
                        if ok:
                            self.bot_logger.info(
                                f"Participant {participant['id']} mic became playable via polling"
                            )
                            await self._start_conversation_if_needed()
                        else:
                            self.bot_logger.warning(
                                f"Participant {participant['id']} mic never became playable, starting anyway"
                            )
                            await self._start_conversation_if_needed()

                    asyncio.create_task(_bg())

        @self.transport.event_handler("on_participant_updated")
        async def on_participant_updated(transport, participant, *args, **kwargs):
            if not self._is_user_participant(participant):
                return
            mic_state = self._mic_state(participant)
            if mic_state == "playable":
                self.bot_logger.info(
                    f"Participant {participant['id']} mic is playable — starting flow"
                )
                await self._start_conversation_if_needed()

        @self.transport.event_handler("on_participant_left")
        async def on_participant_left(transport, participant, reason=None, **kwargs):
            self.bot_logger.info(
                f"Daily: participant left: {participant.get('id')} (reason: {reason})"
            )

        # Handle Daily app messages for text/chat mode
        @self.transport.event_handler("on_app_message")
        async def on_app_message(transport, message, sender, **kwargs):
            """Handle Daily app messages (text chat) and convert to LLM messages."""
            try:
                is_text = self.call_config.media_type == "text"

                # Only process in text mode
                if is_text and isinstance(message, dict) and message.get("type") == "user.chat":
                    text = (message.get("text") or "").strip()
                    if not text:
                        return

                    # Send user input to LLM - flows will handle this automatically
                    await self.task.queue_frame(
                        LLMMessagesAppendFrame(
                            messages=[{"role": "user", "content": text}],
                            run_llm=True,
                        )
                    )
                    self.bot_logger.debug(f"Received user.chat -> queued to LLM: {text!r}")

                    # Also create transcript entry for user message in text mode
                    transcript_message = TranscriptionMessage(role="user", content=text)
                    transcript_frame = TranscriptionUpdateFrame(messages=[transcript_message])
                    await self.transcript_handler.on_transcript_update(self, transcript_frame)
            except Exception as e:
                self.bot_logger.error(f"on_app_message error: {e}")

    async def handle_client_connected(self):
        """Handle client connected event for Daily channel."""
        if self.channel == "daily":
            self.bot_logger.info("Daily: bot connected to room")
        else:
            # Non-Daily channels: start immediately
            self.bot_logger.info(f"{self.channel}: bot connected")
            await self._start_conversation_if_needed()
