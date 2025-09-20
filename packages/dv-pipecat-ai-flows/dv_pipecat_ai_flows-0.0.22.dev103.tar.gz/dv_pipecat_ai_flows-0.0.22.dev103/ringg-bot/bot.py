"""Plivo Chatbot Implementation.

This module sets up and runs the Plivo chatbot using various services and processors
from the Pipecat framework.
"""

# Standard Library Imports
import asyncio
import hashlib  # Added for hashing cache keys
import io  # Added for handling bytes as files
import time
from copy import deepcopy
from datetime import datetime, timezone
from typing import Optional

import aiohttp
import redis.asyncio as redis  # Added for Redis client type hinting

# Third-Party Imports
from cache import cache
from dotenv import load_dotenv
from env_config import api_config
from loguru import logger
from pipecat.adapters.schemas.tools_schema import ToolsSchema
from pipecat.audio.turn.smart_turn.base_smart_turn import SmartTurnParams
from pipecat.audio.turn.smart_turn.fal_smart_turn import FalSmartTurnAnalyzer

# from pipecat.audio.turn.smart_turn.local_smart_turn_v2 import LocalSmartTurnAnalyzerV2
# from pipecat.transcriptions.language import Language # Moved to switch_language.py

# First-Party Imports
from pipecat.frames.frames import BotStoppedSpeakingFrame, Frame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.audio.audio_buffer_processor import AudioBufferProcessor
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

# Local Application Imports
from pipecat.processors.transcript_processor import TranscriptProcessor
from rag.weaviate_script import get_weaviate_client
from starlette.websockets import WebSocket

# from utils.analyzer_pool import get_smart_turn_pool
from utils.background_audio import background_audio_manager
from utils.callbacks import end_callback
from utils.frames_monitor import BotSpeakingFrameMonitor
from utils.generic_functions.cleanup import cleanup_connection
from utils.generic_functions.common import (
    get_vad_params,
    tool_json_to_function_schema,
    is_arabic_present,
)
from utils.generic_functions.response_handler import response_formatters
from utils.llm_functions.call_transfer import call_transfer_handler, call_transfer_tool
from utils.llm_functions.dtmf_output import dtmf_output_handler, dtmf_output_tool  # Import DTMF
from utils.llm_functions.end_call_handler import end_call_function
from utils.llm_functions.generic_function import generic_function_handler
from utils.llm_functions.query_kb import query_knowledge_base
from utils.llm_functions.stay_on_line import stay_on_line_handler, stay_on_line_tool
from utils.llm_functions.switch_language import switch_language_handler, switch_language_tool
from utils.llm_functions.wait_for_dtmf import wait_for_dtmf_handler, wait_for_dtmf_tool
from utils.pipeline import (
    initialise_dtmf_input,
    initialize_filler_config,
    initialize_hold_detector,
    initialize_stt_mute_strategy,
    initialize_user_idle,
    initialize_voicemail_detector,
)
from utils.stay_on_line_processor import StayOnLineProcessor
from utils.llm_functions.tools_definition import base_tools, create_rag_tools
from utils.transcript import save_audio_to_file, TextModeFrameMonitor
from utils.tts import say_with_cache
from utils.generate_config import RunConfig, generate_runtime_config_object
from voice_services.webcall.webcall_params import WebCallParams
from transports.factory import build_transport
from utils.participant_handler import ParticipantHandler
from utils.bot_common import (
    initialize_services,
    setup_context_aggregators,
    create_transcript_handler,
    setup_idle_handlers,
    setup_vad_analyzer,
    get_call_timing,
    setup_redis_client,
    setup_noise_filter,
)
from utils.metrics_collector import create_metrics_collector

# Initialize Environment Variables
load_dotenv(override=True)

# sentry_sdk.init(
#     dsn=api_config.SENTRY_DSN,  # updated from os.getenv("SENTRY_DSN")
#     server_name=get_hostname(),
#     environment=api_config.ENVIRONMENT,  # updated from os.getenv("ENVIRONMENT")
#     sample_rate=0.5,
# )

# logger.remove(0)
# logger.add(sys.stderr, level="DEBUG")


# Define TTSCompletionListener
class TTSCompletionListener(FrameProcessor):  # noqa: D101
    def __init__(self, tts_done_event, **kwargs):  # noqa: D107
        super().__init__(**kwargs)
        self.tts_done_event = tts_done_event
        self.waiting_for_final_tts = False  # Initialize the flag

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await self.push_frame(frame, direction)
        if self.waiting_for_final_tts and isinstance(frame, BotStoppedSpeakingFrame):
            self.tts_done_event.set()
            self.waiting_for_final_tts = False  # Reset the flag


# Using get_telephony_serialiser from bot_common.py


async def run_bot(
    websocket_client: Optional[WebSocket],  # Optional for Daily.co
    call_id,
    stream_id,
    callback_call_id,
    channel: str = "telephony",
    runtime_config: Optional[RunConfig] = None,
    redis_client: redis.Redis = None,
    webcall_params: Optional[WebCallParams] = None,  # Added for Daily.co integration
    webrtc_connection=None,  # Added for SmallWebRTC
):
    bot_logger = logger.bind(call_id=callback_call_id or call_id)

    # Parse config - prioritize runtime_config over legacy call_config
    call_config = runtime_config.call_config
    bot_logger.info("Parsed runtime config successfully")
    bot_logger.info(f"Call config: {call_config}")

    metrics_collector = create_metrics_collector(callback_call_id or call_id)
    bot_logger.info("Metrics collector initialized")

    # Track call timing using common function
    timing = get_call_timing()
    call_start_time = timing["call_start_time"]
    call_end_time = timing["call_end_time"]
    call_duration = timing["call_duration"]

    # Determine if this is chat-only mode
    is_chat_only = webcall_params and webcall_params.media_type == "text"

    function_call_monitor = list()

    # Ensure call_config is available
    if not call_config:
        bot_logger.error("No call configuration provided")
        raise ValueError("call_config is required for bot operation")

    # Setup variables from call_config
    enable_smart_turn = call_config.enable_smart_turn

    # Connect to weaviate if RAG is enabled
    weaviate_client = None
    if call_config.initialize_rag:
        weaviate_client = get_weaviate_client()
        await weaviate_client.connect()

    # Create the final_message_done_event for synchronization
    final_message_done_event = asyncio.Event()
    vad_params_speaking, vad_params_bot_silent = get_vad_params(
        call_config.advanced_vad,
        smart_turn_enabled=enable_smart_turn,
        vad_input=call_config.vad_input,
    )
    arabic_present = is_arabic_present(call_config.language, call_config.add_langs)

    # Create VAD analyzer using common function
    vad_analyzer = setup_vad_analyzer(arabic_present)

    # Get pre-warmed Smart Turn analyzer from pool if enabled
    # turn_analyzer = None
    # smart_turn_pool = get_smart_turn_pool()

    # if enable_smart_turn and smart_turn_pool and smart_turn_pool.is_ready:
    #     try:
    #         turn_analyzer = await smart_turn_pool.acquire()
    #         if turn_analyzer:
    #             bot_logger.info("Using pre-warmed Smart Turn V2 analyzer from pool")
    #         else:
    #             bot_logger.error(
    #                 "Smart Turn pool is empty - this should not happen with proper sizing"
    #             )
    #             # Don't fallback, this indicates a configuration or pool sizing issue
    #             turn_analyzer = None
    #     except Exception as e:
    #         bot_logger.error(f"Failed to acquire Smart Turn analyzer from pool: {e}")
    #         turn_analyzer = None
    # elif enable_smart_turn:
    #     bot_logger.warning("Smart Turn requested but pool not available or not ready")
    #     turn_analyzer = None

    # Setup Redis client
    redis_client = await setup_redis_client(redis_client)

    # Create transcript processor and handler
    transcript = TranscriptProcessor()
    transcript_handler = create_transcript_handler(
        bot_logger, channel, call_config, None
    )  # task will be set later

    # Idempotency flag and lock for cleanup
    cleaning_up = False
    cleanup_lock = asyncio.Lock()

    # Configure turn analyzer based on enable_smart_turn setting
    turn_analyzer = None
    fal_session = None
    if enable_smart_turn:
        fal_session = aiohttp.ClientSession()
        turn_analyzer = FalSmartTurnAnalyzer(
            api_key=api_config.FAL_API_KEY,
            aiohttp_session=fal_session,
            params=SmartTurnParams(stop_secs=0.75, pre_speech_ms=0.0, max_duration_secs=8.0),
        )
        bot_logger.info("FalSmartTurnAnalyzer enabled for semantic turn detection")
    else:
        bot_logger.debug("Smart turn detection disabled")

    # Configure background audio mixer if audio ID is provided
    background_mixer = None
    if call_config.background_audio_config:
        background_mixer = background_audio_manager.create_mixer_from_audio_config(
            call_config.background_audio_config
        )
        if background_mixer:
            bot_logger.info(
                f"Background audio enabled with audio ID: {call_config.background_audio_config.audio_id if call_config.background_audio_config else 'unknown'}"
            )
        else:
            bot_logger.warning("Failed to create background audio mixer")

    # Initialize noise filter if configured
    noise_filter_obj = setup_noise_filter(call_config, call_id, callback_call_id, bot_logger)

    # Build transport based on channel type
    transport, audio_in_sample_rate, audio_out_sample_rate = await build_transport(
        channel=channel,
        call_config=call_config,
        stream_id=stream_id,
        call_id=call_id,
        websocket_client=websocket_client,
        webcall_params=webcall_params,
        vad_analyzer=vad_analyzer,
        turn_analyzer=turn_analyzer,
        background_mixer=background_mixer,
        webrtc_connection=webrtc_connection,
        noise_filter=noise_filter_obj,
    )

    # Initialize all AI services using shared function
    services = await initialize_services(call_id, call_config, bot_logger)
    llm = services["llm"]
    stt = services["stt"]
    tts = services["tts"]

    stay_on_line_processor = None

    # In the run_bot function, before defining end_call_function
    task_references = []

    # --- Expert Tool Registration and Appending ---
    # Build a list of (tool_dict, tool_name, handler_func or None) tuples
    tool_candidates = []
    dedup_names = set()
    for t in deepcopy(base_tools):
        tool_candidates.append((t, t["name"], "end_call" if t["name"] == "end_call" else None))
        dedup_names.add(t["name"])

    # RAG tools (using centralized function)
    if call_config and call_config.kb_data:
        rag_tools = create_rag_tools(call_config.kb_data)
        for rag_tool in rag_tools:
            tool_candidates.append((rag_tool, rag_tool["name"], "query_knowledge_base"))
            dedup_names.add(rag_tool["name"])

    # Switch language tool
    if "switch_language" in call_config.prompt:
        tool_candidates.append(
            (switch_language_tool, switch_language_tool["name"], "switch_language")
        )
        dedup_names.add(switch_language_tool["name"])

    # Call transfer tool
    if "call_transfer" in call_config.prompt:
        tool_candidates.append((call_transfer_tool, call_transfer_tool["name"], "call_transfer"))
        dedup_names.add(call_transfer_tool["name"])

    # DTMF output tool
    if "dtmf_output" in call_config.prompt:
        tool_candidates.append((dtmf_output_tool, dtmf_output_tool["name"], "dtmf_output"))
        dedup_names.add(dtmf_output_tool["name"])

    if "wait_for_dtmf" in call_config.prompt:
        tool_candidates.append((wait_for_dtmf_tool, wait_for_dtmf_tool["name"], "wait_for_dtmf"))
        dedup_names.add(wait_for_dtmf_tool["name"])

    # Stay on line tool
    if "stay_on_line" in call_config.prompt:
        tool_candidates.append((stay_on_line_tool, stay_on_line_tool["name"], "stay_on_line"))
        dedup_names.add(stay_on_line_tool["name"])
        stay_on_line_processor = StayOnLineProcessor(llm_provider=call_config.llm_provider)

    # Custom tools from call_config
    if call_config and call_config.tools:
        for tool in call_config.tools:
            if tool["name"] not in dedup_names:
                tool_candidates.append((tool, tool["name"], "generic_function"))
                dedup_names.add(tool["name"])

    # Handler mapping
    handler_map = {
        "end_call": lambda fn, tool_call_id, args, llm, context, result_callback: end_call_function(
            fn,
            tool_call_id,
            args,
            llm,
            call_config.telephony_provider,
            call_id,
            stream_id,
            websocket_client,
            callback_call_id,
            context_aggregator,
            transcript_handler,
            task,
            task_references,
            bot_speaking_frame_monitor,
            final_message_done_event,
            function_call_monitor,
            bot_logger,
            transport,
        ),
        "query_knowledge_base": lambda fn,
        tool_call_id,
        args,
        llm,
        context,
        result_callback: query_knowledge_base(
            fn,
            tool_call_id,
            args,
            tts,
            call_config.pre_query_response_phrases,
            call_config.kb_name_to_id_map,
            weaviate_client,
            call_config.rag_collection_name,
            result_callback,
            function_call_monitor,
            bot_logger,
            workspace_id=runtime_config.workspace_id,
            facets_collection_name=call_config.rag_facets_collection_name,
            kb_data=call_config.kb_data,
        ),
        "switch_language": lambda fn,
        tool_call_id,
        args,
        llm_svc,
        context,
        result_callback: switch_language_handler(
            fn,
            tool_call_id,
            args,
            llm_svc,
            tts,
            call_config.tts_provider,
            context,
            result_callback,
            function_call_monitor,
            bot_logger,
        ),
        "call_transfer": lambda fn,
        tool_call_id,
        args,
        llm_svc,
        context,
        result_callback: call_transfer_handler(
            fn,
            tool_call_id,
            args,
            context,
            result_callback,
            call_config.telephony_provider,
            call_id,
            bot_logger,
            websocket_client,
            function_call_monitor,
        ),
        "dtmf_output": lambda fn,
        tool_call_id,
        args,
        llm_svc,
        context,
        result_callback: dtmf_output_handler(
            fn,
            tool_call_id,
            args,
            context,
            result_callback,
            call_config.telephony_provider,
            call_id,
            bot_logger,
            function_call_monitor,
        ),
        "generic_function": lambda fn,
        tool_call_id,
        args,
        llm,
        context,
        result_callback: generic_function_handler(
            fn,
            tool_call_id,
            args,
            llm,
            call_config,
            tts,
            call_config.pre_query_response_phrases,
            result_callback,
            cache,
            response_formatters,
            function_call_monitor,
            bot_logger,
        ),
        "wait_for_dtmf": lambda fn,
        tool_call_id,
        args,
        llm,
        context,
        result_callback: wait_for_dtmf_handler(
            fn,
            tool_call_id,
            args,
            llm,
            context,
            result_callback,
            call_config.dtmf_input.timeout,
            bot_logger,
        ),
        "stay_on_line": lambda fn,
        tool_call_id,
        args,
        llm,
        context,
        result_callback: stay_on_line_handler(
            fn,
            tool_call_id,
            args,
            llm,
            context,
            result_callback,
            function_call_monitor,
            stay_on_line_processor,
            bot_logger,
        ),
    }

    # Final tool list and registration
    all_tools = []
    for tool_dict, tool_name, handler_key in tool_candidates:
        all_tools.append(tool_dict)
        if handler_key:
            llm.register_function(tool_name, handler_map[handler_key])
    bot_logger.debug(f"Registered #tools: {len(all_tools)}")
    function_schemas = [tool_json_to_function_schema(tool) for tool in all_tools]
    bot_logger.debug(f"Function #schemas: {len(function_schemas)}")
    tools_schema = ToolsSchema(standard_tools=function_schemas)

    # Services already initialized above

    messages = [
        {
            "role": "system",
            "content": call_config.prompt,
        },
        {"role": "assistant", "content": call_config.intro_message},
    ]

    # if llm_provider == "google":
    #     context = OpenAILLMContext(messages, tools)
    #     context = GoogleLLMContext.upgrade_to_google(context)
    # else:
    # Setup context using shared function
    context = setup_context_aggregators({"messages": messages, "tools_schema": tools_schema})

    # Add call_id and stream_id to context for end_call function
    context.call_id = call_id
    context.stream_id = stream_id
    context_aggregator = llm.create_context_aggregator(context)

    # Create bot speaking monitor (same approach as bot_with_flows.py)
    bot_speaking_frame_monitor = BotSpeakingFrameMonitor(
        final_message_done_event, vad_params_bot_silent, vad_params_speaking
    )

    # Setup idle handlers using shared function
    user_idle = setup_idle_handlers(
        call_config,
        None,  # task - will be set later
        task_references,
        function_call_monitor,
        bot_logger,
        bot_speaking_frame_monitor,
        call_id,
        stream_id,
        websocket_client,
        callback_call_id,
        context_aggregator,
        context,
        transcript_handler,
        transport,
    )

    # Create audio buffer if recording locally
    audio_buffer = None
    if call_config.record_locally:
        audio_buffer = AudioBufferProcessor(
            buffer_size=0,  # Only trigger at end of recording
        )

        # Register event handler
        @audio_buffer.event_handler("on_audio_data")
        async def on_audio_data(buffer, audio, sample_rate, num_channels):
            await save_audio_to_file(audio, sample_rate, num_channels, callback_call_id or call_id)

    pipeline_steps = [
        transport.input(),  # Websocket input from client
        user_idle,
    ]

    # Common end callback for telephony features
    end_callback_func = lambda idle_proc: end_callback(
        idle_proc,
        call_config.telephony_provider,
        call_id,
        stream_id,
        websocket_client,
        callback_call_id,
        context_aggregator,
        transcript_handler,
        task,
        task_references,
        function_call_monitor,
        bot_logger,
        transport,
        call_config.record_locally,
    )

    # Initialize mute strategy and STT for both channels (if not chat-only)
    if not is_chat_only:
        initialize_stt_mute_strategy(
            call_config.mute_during_intro, call_config.mute_while_bot_speaking, pipeline_steps
        )
        pipeline_steps.extend([stt])

    # Telephony-specific processors
    if channel == "telephony":
        initialize_voicemail_detector(
            call_config.mute_during_intro,
            call_config.mute_while_bot_speaking,
            call_config.voicemail.model_dump(),
            pipeline_steps,
            vad_params_bot_silent,
            end_callback_func,
            function_call_monitor,
        )

        initialize_hold_detector(
            call_config.call_hold_config,
            end_callback_func,
            pipeline_steps,
        )

        initialize_filler_config(
            call_config, transport, call_config.voice, call_config.language, pipeline_steps
        )

        if stay_on_line_processor:
            pipeline_steps.append(stay_on_line_processor)

        # Initialize DTMF for all channels
        initialise_dtmf_input(call_config, pipeline_steps)

    # Add core processing pipeline based on mode
    if not is_chat_only:
        # Audio pipeline for voice calls
        pipeline_steps.extend(
            [
                transcript.user(),
                context_aggregator.user(),
                llm,
                tts,
                bot_speaking_frame_monitor,
                transport.output(),
            ]
        )
    else:
        # Text-only pipeline for chat (Daily channel only)
        text_monitor = TextModeFrameMonitor(transcript_handler)
        pipeline_steps.extend(
            [
                context_aggregator.user(),
                llm,
                text_monitor,
                context_aggregator.assistant(),
                transport.output(),
            ]
        )

    # Add audio buffer processor to pipeline if needed (only for audio mode)
    if call_config.record_locally and audio_buffer:
        logger.debug("Adding audio_buffer")
        pipeline_steps.append(audio_buffer)

    # Add transcript processors at the end like the original pattern
    if not is_chat_only:
        pipeline_steps.extend(
            [
                transcript.assistant(),
                context_aggregator.assistant(),
            ]
        )

    pipeline = Pipeline(pipeline_steps)

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            allow_interruptions=True,
            enable_metrics=True,
            audio_in_sample_rate=audio_in_sample_rate,
            audio_out_sample_rate=audio_out_sample_rate,
            start_metadata={
                "voicemail_detect": call_config.voicemail.detect
                if call_config.voicemail
                else False,
                "call_id": callback_call_id or call_id,
            },
        ),
        conversation_id=str(callback_call_id or call_id),
    )

    # Set task reference for transcript handler
    transcript_handler.task = task

    # Initialize participant handler for all channels to handle initialization
    participant_handler = ParticipantHandler(
        transport=transport,
        channel=channel,
        call_config=call_config,
        audio_out_sample_rate=audio_out_sample_rate,
        task=task,
        audio_buffer=audio_buffer,
        background_mixer=background_mixer,
        flow_manager=None,  # No flow manager in legacy bot
        bot_logger=bot_logger,
        transcript_handler=transcript_handler,
    )

    # Register participant event handlers only for daily channel
    print("here is the channel", channel)
    if channel == "daily":
        participant_handler.register_event_handlers()

    # Add metrics collector as observer to capture metrics frames
    task.add_observer(metrics_collector)

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        bot_logger.info("New client connection")

        # Use participant handler to manage initialization (recording, background audio, etc.)
        await participant_handler.handle_client_connected()

        # Send intro message for all modes (say_with_cache handles both audio and text via TTSSpeakFrame)
        await say_with_cache(
            task,
            tts,
            redis_client,
            call_config.use_tts_cache,
            call_config.intro_message,
            transport,
            bot_logger,
        )

    # Register event handler for transcript updates
    @transcript.event_handler("on_transcript_update")
    async def on_transcript_update(processor, frame):
        await transcript_handler.on_transcript_update(processor, frame)

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        nonlocal cleaning_up, call_end_time, call_duration
        async with cleanup_lock:
            if cleaning_up:
                bot_logger.info("Cleanup already performed, skipping.")
                return
            cleaning_up = True

        bot_logger.info("Client disconnected, performing cleanup.")

        # Release Smart Turn analyzer back to pool if used
        # if smart_turn_pool and turn_analyzer:
        #     try:
        #         await smart_turn_pool.release(turn_analyzer)
        #         bot_logger.debug("Released Smart Turn analyzer back to pool")
        #     except Exception as e:
        #         bot_logger.error(f"Failed to release Smart Turn analyzer: {e}")

        # Calculate call end time and duration
        call_end_time = datetime.now(timezone.utc)
        call_duration = (call_end_time - call_start_time).total_seconds()

        # Stop audio recording if enabled
        try:
            if call_config.record_locally and audio_buffer:
                await audio_buffer.stop_recording()
        except Exception as e:
            bot_logger.error(f"Error stopping audio recording: {e}")

        # close weaviate connection
        try:
            if call_config and call_config.initialize_rag:
                if weaviate_client:
                    await weaviate_client.close()
        except Exception as e:
            bot_logger.error(f"Error closing Weaviate connection: {e}")

        # Close FAL session if it was created
        if fal_session:
            try:
                await fal_session.close()
                bot_logger.debug("Closed FAL aiohttp session")
            except Exception as e:
                bot_logger.error(f"Error closing FAL session: {e}")

        await cleanup_connection(
            callback_call_id,
            call_id,
            context_aggregator,
            transcript_handler,
            task,
            task_references,
            function_call_monitor,
            bot_logger,
            call_config.record_locally,
            call_config.telephony_provider,
            call_duration,
        )

    runner = PipelineRunner(handle_sigint=False)

    await runner.run(task)
