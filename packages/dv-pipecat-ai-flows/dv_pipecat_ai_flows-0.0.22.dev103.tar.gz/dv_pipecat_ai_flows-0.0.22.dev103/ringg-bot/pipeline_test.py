#!/usr/bin/env python3
"""
Test script to replicate UserStartedSpeakingFrame → UserStoppedSpeakingFrame → TranscriptionFrame
pipeline execution for bot testing without telephony calls.

This script sets up a minimal Pipecat pipeline and programmatically sends the requested
frame sequence with timing control to observe bot execution logs.
"""

import asyncio
import os
import sys

from env_config import api_config

# Add the project root to Python path
# sys.path.insert(0, '/Users/kalicharanvemuru/Documents/Code/pipecat/src')
# sys.path.insert(0, '/Users/kalicharanvemuru/Documents/Code/pipecat')
from loguru import logger

from pipecat.frames.frames import (
    BotInterruptionFrame,
    EndFrame,
    StartFrame,
    StartInterruptionFrame,
    TranscriptionFrame,
    UserStartedSpeakingFrame,
    UserStoppedSpeakingFrame,
)
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_response import (
    LLMAssistantContextAggregator,
    LLMUserContextAggregator,
)
from pipecat.processors.aggregators.openai_llm_context import (
    OpenAILLMContext,
    OpenAILLMContextFrame,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.services.groq.llm import GroqLLMService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transports.network.fastapi_websocket import (
    FastAPIWebsocketParams,
    FastAPIWebsocketTransport,
)
from pipecat.utils.time import time_now_iso8601

try:
    from fastapi import WebSocket
    from starlette.websockets import WebSocketState
except ImportError:
    WebSocket = None
    WebSocketState = None


class TestFrameProcessor(FrameProcessor):
    """Test processor that logs all frame types and timing."""

    def __init__(self, name: str = "TestProcessor"):
        super().__init__(name=name)
        self.frame_count = 0
        self.start_time = None

    async def process_frame(self, frame, direction: FrameDirection):
        """Log frame processing with timestamps."""
        # Call parent process_frame first to handle lifecycle
        await super().process_frame(frame, direction)

        if not self.start_time:
            self.start_time = asyncio.get_event_loop().time()

        current_time = asyncio.get_event_loop().time()
        elapsed = (current_time - self.start_time) * 1000  # Convert to ms

        self.frame_count += 1

        logger.info(
            f"[{self.name}] Frame #{self.frame_count} at {elapsed:.1f}ms: "
            f"{frame.__class__.__name__} - Direction: {direction.name}"
        )

        # Log frame details for specific types
        if isinstance(frame, (UserStartedSpeakingFrame, UserStoppedSpeakingFrame)):
            logger.info(f"  → Speech event: {frame.name}")
        elif isinstance(frame, TranscriptionFrame):
            logger.info(f"  → Transcription: '{frame.text}' (final)")
        elif isinstance(frame, BotInterruptionFrame):
            logger.info(f"  → Bot Interruption Frame detected! (flows upstream)")
        elif isinstance(frame, StartInterruptionFrame):
            logger.info(f"  → Start Interruption Frame detected! (flows downstream)")
        elif isinstance(frame, OpenAILLMContextFrame):
            # Log context updates to see how conversation evolves
            messages = frame.context.get_messages()
            logger.info(f"  → LLM Context Frame: {len(messages)} messages")
            for i, msg in enumerate(messages):  # Show all messages to see the conversation
                role = msg.get("role", "unknown")
                content = msg.get("content", "")[:100] + (
                    "..." if len(msg.get("content", "")) > 100 else ""
                )
                logger.info(f"    [{i}] {role}: {content}")
        elif isinstance(frame, StartFrame):
            logger.info(f"  → Pipeline started with config: {frame.allow_interruptions}")
        elif isinstance(frame, EndFrame):
            logger.info(f"  → Pipeline ended")

        # Continue frame processing
        await self.push_frame(frame, direction)


class MockWebSocket:
    """Mock WebSocket for testing FastAPIWebsocketTransport."""

    def __init__(self):
        self.client_state = WebSocketState.CONNECTED if WebSocketState else "connected"
        self.application_state = WebSocketState.CONNECTED if WebSocketState else "connected"
        self.sent_data = []
        self.received_data = []

    def iter_bytes(self):
        """Mock binary data iteration."""
        return self._iter_data()

    def iter_text(self):
        """Mock text data iteration."""
        return self._iter_data()

    async def _iter_data(self):
        """Generator that yields received data."""
        # For testing, we don't send any data back
        # This is just to satisfy the transport's receive loop
        while True:
            await asyncio.sleep(0.1)
            if self.received_data:
                yield self.received_data.pop(0)
            else:
                # Keep the connection alive but don't yield anything
                continue

    async def send_bytes(self, data: bytes):
        """Mock send bytes."""
        self.sent_data.append(data)
        logger.info(f"MockWebSocket sent {len(data)} bytes")

    async def send_text(self, data: str):
        """Mock send text."""
        self.sent_data.append(data)
        logger.info(f"MockWebSocket sent text: {data[:100]}...")

    async def close(self):
        """Mock close connection."""
        self.client_state = WebSocketState.DISCONNECTED if WebSocketState else "disconnected"
        self.application_state = WebSocketState.DISCONNECTED if WebSocketState else "disconnected"
        logger.info("MockWebSocket closed")


class TestFrameInjector:
    """Injects test frames directly into a transport input."""

    def __init__(self, transport_input):
        self.transport_input = transport_input
        self.test_frames = []

    def add_test_frame(self, frame, delay_ms: float = 0):
        """Add a frame to be sent after specified delay."""
        self.test_frames.append((frame, delay_ms))

    async def start_test_sequence(self):
        """Send the test frame sequence with timing."""
        logger.info("Starting test frame sequence...")

        start_time = asyncio.get_event_loop().time()

        for frame, delay_ms in self.test_frames:
            if delay_ms > 0:
                await asyncio.sleep(delay_ms / 1000.0)

            current_time = asyncio.get_event_loop().time()
            elapsed = (current_time - start_time) * 1000

            logger.info(f"Injecting {frame.__class__.__name__} at {elapsed:.1f}ms")
            # Inject directly into the transport input
            await self.transport_input.queue_frame(frame)

        logger.info("Test sequence completed")


async def create_test_pipeline():
    """Create a pipeline with real FastAPIWebsocketTransport for testing."""
    # Configure logging
    logger.remove()
    logger.add(
        sys.stdout,
        level="DEBUG",  # Changed to DEBUG to see aggregator internal logs
        format="<green>{time:HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | {message}",
        colorize=True,
    )

    logger.info(
        "Creating test pipeline with FastAPIWebsocketTransport and LLMUserContextAggregator..."
    )

    # Create mock WebSocket and FastAPI transport
    mock_websocket = MockWebSocket()
    transport_params = FastAPIWebsocketParams()
    transport = FastAPIWebsocketTransport(websocket=mock_websocket, params=transport_params)

    # Create frame logger
    frame_logger = TestFrameProcessor("FrameLogger")

    # Create LLM context with initial system prompt and aggregator
    initial_messages = [
        {
            "role": "system",
            "content": """You are a helpful customer service assistant for a telecommunications company. 
            You should be friendly, professional, and helpful. Keep responses concise and conversational.
            
            Your main tasks are to:
            - Help customers with account inquiries
            - Assist with technical support issues
            - Provide billing information
            - Handle service requests
            
            Always be polite and try to resolve issues quickly.""",
        }
    ]

    llm_context = OpenAILLMContext(messages=initial_messages)
    user_context_aggregator = LLMUserContextAggregator(context=llm_context, name="UserContextAgg")
    assistant_context_aggregator = LLMAssistantContextAggregator(
        context=llm_context, name="AssistantContextAgg"
    )

    logger.info(
        f"LLM context initialized with system prompt: {len(llm_context.get_messages())} messages"
    )

    # Add debug logging to the aggregator
    # original_process_frame = user_context_aggregator.process_frame
    # async def debug_process_frame(frame, direction):
    #     logger.info(f"[UserContextAgg] Processing {frame.__class__.__name__} - {direction.name}")
    #     if isinstance(frame, TranscriptionFrame):
    #         logger.info(f"[UserContextAgg] TranscriptionFrame text: '{frame.text}'")
    #         logger.info(f"[UserContextAgg] Current aggregation: '{user_context_aggregator._aggregation}'")
    #         logger.info(f"[UserContextAgg] User speaking: {user_context_aggregator._user_speaking}")
    #         logger.info(f"[UserContextAgg] Bot speaking: {user_context_aggregator._bot_speaking}")
    #     result = await original_process_frame(frame, direction)
    #     return result
    # user_context_aggregator.process_frame = debug_process_frame

    # Create a simple LLM service for testing (optional)

    llm_service = GroqLLMService(
        api_key=api_config.GROQ_API_KEY,
        model="qwen/qwen3-32b",
        params=OpenAILLMService.InputParams(
            extra={"reasoning_effort": "none"},
            temperature=0.7,
        ),
        # metrics=SentryMetrics(),
    )

    # Build pipeline with proper flow:
    # Transport.Input → UserContextAggregator → [LLM] → AssistantContextAggregator → Transport.Output
    # This way BotInterruptionFrame flows upstream to transport.input() which generates StartInterruptionFrame downstream
    processors = [transport.input(), user_context_aggregator]
    if llm_service:
        processors.append(llm_service)
        processors.append(assistant_context_aggregator)  # Add assistant aggregator after LLM
    processors.append(transport.output())

    pipeline = Pipeline(processors)

    # Create frame injector that injects into the transport input
    frame_injector = TestFrameInjector(transport.input())

    return pipeline, frame_injector


async def setup_test_frames(frame_injector: TestFrameInjector):
    """Setup the test frame sequence."""
    logger.info("Setting up test frame sequence...")

    # 1. Start frame to initialize pipeline
    start_frame = StartFrame(allow_interruptions=True, enable_metrics=True)
    # Add metadata after creation
    start_frame.metadata = {"call_id": "test_call_001"}
    frame_injector.add_test_frame(start_frame, delay_ms=0)

    # 2. UserStartedSpeakingFrame
    user_started = UserStartedSpeakingFrame()
    frame_injector.add_test_frame(user_started, delay_ms=50)

    transcription = TranscriptionFrame(
        text="Hello, I need help with my account", user_id="test_user", timestamp=time_now_iso8601()
    )
    frame_injector.add_test_frame(transcription, delay_ms=400)

    # 3. UserStoppedSpeakingFrame (after some speech duration)
    user_stopped = UserStoppedSpeakingFrame()
    frame_injector.add_test_frame(user_stopped, delay_ms=500)

    # 4. Wait longer for the first LLM response to complete before sending second transcription
    # This gives time for the assistant context aggregator to capture the response
    transcription2 = TranscriptionFrame(
        text="Can you hear me?", user_id="test_user", timestamp=time_now_iso8601()
    )
    frame_injector.add_test_frame(
        transcription2,
        delay_ms=3000,  # Wait 3 seconds for first response to complete
    )
    # frame_injector.add_test_frame(user_stopped, delay_ms=500)

    # 5. Add another user interaction sequence
    user_started = UserStartedSpeakingFrame()
    frame_injector.add_test_frame(user_started, delay_ms=50)

    transcription3 = TranscriptionFrame(
        text="Hello, I need help with my account", user_id="test_user", timestamp=time_now_iso8601()
    )
    frame_injector.add_test_frame(transcription3, delay_ms=400)

    # UserStoppedSpeakingFrame (after some speech duration)
    user_stopped = UserStoppedSpeakingFrame()
    frame_injector.add_test_frame(user_stopped, delay_ms=500)

    # 6. End frame to complete the test
    end_frame = EndFrame()
    frame_injector.add_test_frame(end_frame, delay_ms=15000)

    logger.info(f"Test sequence configured with {len(frame_injector.test_frames)} frames")


async def run_pipeline_test():
    """Run the complete pipeline test."""
    logger.info("=" * 60)
    logger.info("PIPECAT PIPELINE TEST - Frame Sequence Simulation")
    logger.info("=" * 60)

    try:
        # Create pipeline and frame injector
        pipeline, frame_injector = await create_test_pipeline()

        # Setup test frames
        await setup_test_frames(frame_injector)

        # Create pipeline task
        task = PipelineTask(
            pipeline,
            params=PipelineParams(
                allow_interruptions=True, enable_metrics=True, enable_usage_metrics=False
            ),
        )

        # Create runner
        runner = PipelineRunner()

        logger.info("Starting pipeline runner...")

        # Start the pipeline
        pipeline_task = asyncio.create_task(runner.run(task))

        # Wait a bit for pipeline to initialize
        await asyncio.sleep(0.1)

        # Start the test sequence
        test_task = asyncio.create_task(frame_injector.start_test_sequence())

        # Wait for test completion
        await test_task

        # Wait a bit more to see any delayed processing
        logger.info("Waiting for pipeline processing to complete...")
        await asyncio.sleep(2.0)

        # Cancel pipeline
        pipeline_task.cancel()

        try:
            await pipeline_task
        except asyncio.CancelledError:
            pass

        logger.info("Pipeline test completed successfully")

    except Exception as e:
        logger.error(f"Pipeline test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    logger.info("Starting Pipecat Pipeline Test...")

    try:
        asyncio.run(run_pipeline_test())
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    logger.info("Test script completed")
