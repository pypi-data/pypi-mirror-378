# Pipecat Framework Architecture Deep Dive

This comprehensive guide covers the complete Pipecat framework architecture, based on thorough analysis of the 307 Python files in `src/pipecat`.

## Table of Contents

1. [Frame System Architecture](#frame-system-architecture)
2. [Pipeline Architecture](#pipeline-architecture)
3. [AI Services Architecture](#ai-services-architecture)
4. [Transport Layer](#transport-layer)
5. [Processors and Aggregators](#processors-and-aggregators)
6. [Complete Code Flow Patterns](#complete-code-flow-patterns)
7. [When to Use What](#when-to-use-what)

## Frame System Architecture

### Frame Hierarchy

Pipecat's entire system is built around **frames** - typed data containers that flow through processing pipelines.

```python
Frame (Base)
├── SystemFrame       # Processed immediately, bypass queues
│   ├── StartFrame     # Pipeline initialization
│   ├── CancelFrame    # Emergency shutdown
│   ├── ErrorFrame     # Error reporting
│   └── InputAudioRawFrame  # User audio input
├── DataFrame         # Queued data processing
│   ├── TextFrame      # Basic text content
│   ├── AudioRawFrame  # Audio data
│   ├── ImageRawFrame  # Image data
│   └── LLMMessagesAppendFrame  # LLM context updates
└── ControlFrame      # Queued control flow
    ├── EndFrame       # Graceful shutdown
    └── LLMFullResponseStartFrame/EndFrame
```

### Frame Processing Rules

**SystemFrames** are processed **immediately** without queuing:
- `StartFrame`, `CancelFrame`, `ErrorFrame`
- `StartInterruptionFrame` (StopInterruptionFrame removed in v0.0.83)
- `InputAudioRawFrame` (user audio has priority)

**DataFrames and ControlFrames** are **queued** for ordered processing:
- `TextFrame`, `AudioRawFrame`, `LLMMessagesAppendFrame`
- `EndFrame`, `LLLFullResponseStartFrame`

### Frame Metadata System

```python
@dataclass
class Frame:
    id: int                          # Unique frame identifier
    name: str                        # Frame type name with counter
    pts: Optional[int]               # Presentation timestamp (nanoseconds)
    metadata: Dict[str, Any]         # Arbitrary metadata
    transport_source: Optional[str]  # Origin transport
    transport_destination: Optional[str]  # Target transport
```

### Key Frame Types and Usage

**Audio Frames:**
```python
OutputAudioRawFrame     # Audio output to transport
TTSAudioRawFrame        # TTS-generated audio
InputAudioRawFrame      # Audio input from transport
UserAudioRawFrame       # User-associated audio
```

**Text Frames:**
```python
TextFrame              # Basic text (LLM → TTS), supports skip_tts field
LLMTextFrame           # LLM-generated text
TranscriptionFrame     # STT transcription (final)
InterimTranscriptionFrame  # STT transcription (partial)
InputTextRawFrame      # User text input (for Gemini Multimodal Live)
```

**LLM Context Frames:**
```python
LLMMessagesAppendFrame # Add messages and optionally trigger LLM (run_llm=True)
LLMMessagesUpdateFrame # Replace context messages and optionally trigger LLM
LLMSetToolsFrame       # Set function calling tools
OpenAILLMContextFrame  # OpenAI-specific context management (legacy)
LLMRunFrame            # Trigger LLM response without context changes
LLMConfigureOutputFrame # Configure LLM output (e.g., skip_tts=True)
```

**Transport Message Frames:**
```python
InputTransportMessageUrgentFrame      # Urgent messages from external sources
DailyInputTransportMessageUrgentFrame # Daily-specific urgent transport messages
```

**User Activity Frames:**
```python
UserSpeakingFrame      # Bidirectional frame sent while VAD detects user speaking
```

**Service Switching Frames:**
```python
ManuallySwitchServiceFrame # Switch between services at runtime (for LLMSwitcher)
```

## Pipeline Architecture

### Sequential Pipeline

**Construction and Linking:**
```python
processors = [stt_service, llm_service, tts_service]
pipeline = Pipeline(processors)
# Creates: Source -> STT -> LLM -> TTS -> Sink
```

**Frame Flow:**
1. Frames enter via `PipelineSource`
2. Each processor maintains `_prev` ← → `_next` links
3. Frames flow through `process_frame()` methods
4. Frames exit via `PipelineSink`

### Parallel Pipeline

**Architecture:**
```python
parallel = ParallelPipeline(
    [audio_processor1, audio_processor2],    # Audio branch
    [video_processor1, video_processor2]     # Video branch
)
```

**Synchronization:**
- Multiple independent processing branches
- `EndFrame` counting ensures all branches complete
- Frame deduplication via `_seen_ids` set
- Upstream/downstream queues coordinate communication

### Frame Queue Management

Each processor maintains multiple async queues:

```python
class FrameProcessor:
    __input_queue: WatchdogQueue         # Incoming frames
    __push_queue: WatchdogQueue          # Outgoing frames
    
    async def push_frame(self, frame: Frame, direction: FrameDirection):
        if isinstance(frame, SystemFrame):
            await self.__internal_push_frame(frame, direction)  # Immediate
        else:
            await self.__push_queue.put((frame, direction))     # Queued
```

### Pipeline Task Execution

**PipelineTask Responsibilities:**
- **Source Management**: Entry point for external frames
- **Sink Management**: Exit point and completion detection  
- **Task Orchestration**: Multiple async tasks for different purposes
- **Lifecycle Management**: Setup, start, running, shutdown, cleanup

**Key Tasks:**
```python
_process_push_queue()    # Main execution driver
_process_up_queue()      # Upstream frame handling
_process_down_queue()    # Downstream frame handling
_process_heartbeat()     # Health monitoring (optional)
_process_idle()          # Idle detection (optional)
```

## AI Services Architecture

### Service Base Class Hierarchy

```python
AIService (extends FrameProcessor)
├── LLMService          # Language models with function calling
├── STTService          # Speech-to-Text
├── TTSService          # Text-to-Speech
├── VisionService       # Image analysis
└── ImageService        # Image generation
```

### LLMService - Advanced Features

**Function Calling System:**
```python
class LLMService:
    # Register function handlers
    def register_function(
        self, 
        function_name: Optional[str],     # None = catch-all
        handler: FunctionCallHandler,
        cancel_on_interruption: bool = True
    )
    
    # Execute multiple functions
    async def run_function_calls(self, function_calls: Sequence[FunctionCallFromLLM])
```

**Context Management:**
- **Legacy**: Uses `OpenAILLMAdapter` by default (pluggable)
- **Universal**: New `LLMContext` - LLM-agnostic context for runtime LLM switching
- **LLMSwitcher**: Runtime switching between different LLM services with shared context
- **LLMContextAggregatorPair**: Universal context aggregator for cross-LLM compatibility
- Supports streaming completions with function calling
- Handles interruption strategies
- Manages conversation context and tool definitions

**Universal Context Pattern:**
```python
# Traditional (service-specific)
context = OpenAILLMContext(messages, tools)
context_aggregator = llm.create_context_aggregator(context)

# Universal (LLM-agnostic)
context = LLMContext(messages, tools)  # Works with any LLM
context_aggregator = LLMContextAggregatorPair(context)

# Runtime LLM switching
llm_switcher = LLMSwitcher([llm_openai, llm_anthropic])
await task.queue_frames([ManuallySwitchServiceFrame(service=llm_anthropic)])
```

**Supported Universal Context Services:**
- OpenAI, Anthropic, Google, Azure, Cerebras, Deepseek, Fireworks AI
- Grok, Groq, Mistral, NVIDIA NIM, Ollama, OpenPipe, OpenRouter
- Perplexity, Qwen, SambaNova, Together.ai

### STTService - Speech Recognition

**Core Pattern:**
```python
class STTService(AIService):
    async def process_frame(self, frame: Frame, direction: FrameDirection):
        if isinstance(frame, AudioRawFrame):
            await self.start_processing_metrics()
            async for result_frame in self.run_stt(frame.audio):
                await self.push_frame(result_frame, direction)
                
    @abstractmethod
    async def run_stt(self, audio: bytes) -> AsyncGenerator[Frame, None]:
        # Implementation-specific STT processing
```

**Variants:**
- `SegmentedSTTService`: VAD-based speech segmentation
- WebSocket-based services with reconnection logic
- Real-time vs batch processing modes

### TTSService - Speech Synthesis

**Text Processing Pipeline:**
```python
class TTSService(AIService):
    _aggregator: BaseTextAggregator    # Sentence aggregation
    _text_filters: List[BaseTextFilter] # Text preprocessing
    
    async def process_frame(self, frame: Frame, direction: FrameDirection):
        if isinstance(frame, TextFrame):
            # 1. Filter text through filters
            # 2. Aggregate into sentences  
            # 3. Generate audio via run_tts()
            # 4. Push TTSAudioRawFrame
```

**Specialized Variants:**
- `WordTTSService`: Word-level timestamps
- `WebsocketTTSService`: WebSocket-based with reconnection
- `InterruptibleTTSService`: Handles mid-speech interruptions
- `AudioContextWordTTSService`: Context-aware audio management
- `AsyncAITTSService`: Streaming TTS with multilingual support (ES, FR, DE, IT)
- `AsyncAIHttpTTSService`: HTTP-based AsyncAI TTS with streaming
- `InworldTTSService`: Low-latency speech generation via Inworld API
- `HeyGenVideoService`: Video avatar with audio streaming integration

### Service Integration Patterns

**Frame Processing Integration:**
```python
# Services receive specific frame types
LLMService:          LLMMessagesAppendFrame → LLMTextFrame
STTService:          AudioRawFrame → TranscriptionFrame  
TTSService:          TextFrame → TTSAudioRawFrame
VisionService:       VisionImageRawFrame → TextFrame
```

**Streaming Pattern:**
```python
async def run_service(self, input_data) -> AsyncGenerator[Frame, None]:
    # 1. Send request to AI service
    # 2. Process streaming response
    # 3. Yield frames as data arrives
    # 4. Handle errors and interruptions
    async for chunk in streaming_response:
        yield OutputFrame(data=chunk)
```

## Transport Layer

### Base Transport Architecture

```python
BaseTransport
├── BaseInputTransport    # Receives frames from external sources
├── BaseOutputTransport   # Sends frames to external destinations
└── Transport combinations for bidirectional communication
```

### Transport Implementations

**Daily (WebRTC):**
- Real-time audio/video via WebRTC
- VAD integration for turn detection
- Participant management and room controls

**FastAPI WebSocket:**
- WebSocket-based frame transport
- Serialization via FrameSerializer
- Request/response pattern support

**Local Audio:**
- System audio input/output
- Development and testing support
- Cross-platform audio device management

### Frame Serialization

**Purpose:** Convert frames to/from wire format for transport

```python
class FrameSerializer:
    def serialize(self, frame: Frame) -> bytes
    def deserialize(self, data: bytes) -> Frame
```

**Provider-Specific Serializers:**
- `TwilioFrameSerializer`: Twilio media stream format
- `PlivoFrameSerializer`: Plivo stream format  
- `LiveKitFrameSerializer`: LiveKit frame format

## Extensions and Specialized Components

### IVR Navigator (`pipecat.extensions.ivr`)
**Automated IVR System Navigation** for telephony systems with intelligent menu traversal:

```python
from pipecat.extensions.ivr.ivr_navigator import IVRNavigator

# Create IVR navigator with specific goal
ivr_navigator = IVRNavigator(
    llm=llm_service,
    ivr_prompt="Navigate to billing department to dispute a charge"
)

# Handle different outcomes
@ivr_navigator.event_handler("on_conversation_detected")
async def on_conversation(processor, conversation_history):
    # Switch to normal conversation mode
    
@ivr_navigator.event_handler("on_ivr_status_changed") 
async def on_ivr_status(processor, status):
    if status == IVRStatus.COMPLETED:
        # Goal achieved, start bot conversation
    elif status == IVRStatus.STUCK:
        # Handle navigation failure
```

**Key Features:**
- **DTMF Input**: Collects keypad input for menu navigation
- **Verbal Responses**: Handles voice-based menu options
- **Goal-Oriented**: Uses LLM to navigate toward specific objectives
- **Status Tracking**: Reports navigation progress and completion

### Voicemail Detection (`pipecat.extensions.voicemail`)
**Automated Voicemail vs Live Detection** for outbound calling:

```python
from pipecat.extensions.voicemail import VoicemailDetector

voicemail_detector = VoicemailDetector(
    llm=text_llm_service,  # Text-only LLM optimization
    detection_timeout=5.0
)

@voicemail_detector.event_handler("on_voicemail_detected")
async def on_voicemail(detector, confidence):
    # Handle voicemail scenario
    
@voicemail_detector.event_handler("on_live_person_detected") 
async def on_live_person(detector, confidence):
    # Begin normal conversation
```

### Audio Filters and Enhancement
**AICFilter** (`pipecat.audio.filters.aic_filter`):
- **Speech Enhancement**: Improves VAD/STT performance
- **No ONNX Dependency**: Lightweight integration via AI-Coustics SDK
- **Real-time Processing**: Filters audio streams in pipeline

**DTMF Audio Processing** (`pipecat.audio.dtmf`):
- **Generic DTMF Generation**: Works across all output transports
- **Audio File Loading**: Pre-generated DTMF tones (0-9, *, #)
- **Transport Integration**: `BaseOutputTransport.write_dtmf()`

### WhatsApp Integration (`pipecat.transports.whatsapp`)
**WhatsApp User-initiated Calls** support:

```python
from pipecat.transports.whatsapp import WhatsAppTransport

whatsapp_transport = WhatsAppTransport(
    api_client=whatsapp_client,
    webhook_handler=webhook_handler
)
```

## Processors and Aggregators

### Frame Processors

**Base FrameProcessor Features:**
- Linked list connectivity (`_prev` ← → `_next`)
- Bidirectional frame flow (upstream/downstream)
- Queue management and async processing
- Lifecycle management (start, stop, cancel)
- Metrics integration and error handling

**Processor Categories:**

**Aggregators** (`processors/aggregators/`):
```python
LLMResponseAggregator     # Collects streaming LLM responses
SentenceAggregator        # Aggregates text into sentences
UserResponseAggregator    # Collects user input with timing
DTMFAggregator           # DTMF digit collection
```

**Filters** (`processors/filters/`):
```python
FrameFilter              # Generic frame filtering
FunctionFilter           # Custom function-based filtering
STTMuteFilter           # STT muting during bot speech
WakeCheckFilter         # Wake word detection
```

**Audio Processors** (`processors/audio/`):
```python
AudioBufferProcessor     # Audio buffering and timing
```

### Context Aggregators

**LLMUserContextAggregator:**
- Aggregates user transcriptions into conversation context
- VAD-aware timing and interruption handling
- Configurable aggregation strategies

**LLMAssistantContextAggregator:**
- Collects LLM responses between start/end frames
- Function call lifecycle tracking
- Interruption handling with state reset

**Context Flow:**
```
TranscriptionFrame → UserContextAggregator → LLMMessagesAppendFrame
LLMTextFrame → AssistantContextAggregator → Updated Context
```

## Complete Code Flow Patterns

### Typical Voice AI Pipeline

```python
# 1. Pipeline Setup
pipeline = Pipeline([
    transport.input(),           # Audio input
    stt_service,                # Speech recognition  
    llm_user_aggregator,        # User context
    llm_service,                # Language model
    llm_assistant_aggregator,   # Assistant context
    tts_service,                # Speech synthesis
    transport.output()          # Audio output
])

# 2. Frame Flow
InputAudioRawFrame → STTService → TranscriptionFrame 
    → LLMUserContextAggregator → LLMMessagesAppendFrame
    → LLMService → LLMTextFrame
    → LLMAssistantContextAggregator → Context Update
    → TTSService → TTSAudioRawFrame → Transport
```

### Function Calling Flow

```python
# 1. Function Registration
llm_service.register_function("weather_lookup", weather_handler)

# 2. Processing Flow
LLMMessagesAppendFrame → LLMService → FunctionCallsStartedFrame
    → FunctionCallInProgressFrame → [Function Execution]
    → FunctionCallResultFrame → [Context Update]
    → LLMMessagesAppendFrame → [Continue LLM Processing]
```

### Interruption Handling Flow

```python
# 1. User Starts Speaking (Immediate)
VAD Detection → StartInterruptionFrame (SystemFrame)
    → [All processors handle immediately]
    → Cancel ongoing TTS/function calls

# 2. User Speech Processing (Ordered)  
StartInterruptionFrame → UserStartedSpeakingFrame (ControlFrame)
    → [Queued processing continues]

# 3. Interruption Recovery
StopInterruptionFrame → UserStoppedSpeakingFrame
    → [Resume normal processing]
```

### Parallel Processing Flow

```python
# Audio + Video parallel processing
parallel_pipeline = ParallelPipeline(
    [audio_input, audio_stt, audio_llm, audio_tts, audio_output],
    [video_input, video_analysis, video_generation, video_output]
)

# Frame synchronization at EndFrame
EndFrame → [Wait for all branches] → Pipeline completion
```

## When to Use What

### Pipeline Types

**Use Sequential Pipeline when:**
- Processors have dependencies (STT → LLM → TTS)
- Order matters for processing
- Simple linear workflow
- Resource constraints favor sequential processing

**Use Parallel Pipeline when:**
- Independent processing branches (audio + video)
- CPU-intensive operations that can be parallelized  
- Different processing speeds for different data types
- Need to maximize throughput

### Frame Types

**Use SystemFrame when:**
- Immediate processing required (user input, errors)
- Bypass queues for urgent operations
- System-level control (start, cancel, interruption)

**Use DataFrame when:**
- Content data (audio, text, images)
- Order matters for processing
- Normal pipeline flow

**Use ControlFrame when:**
- Pipeline flow control
- Ordered control operations
- Response boundaries (start/end markers)

### Service Selection

**LLMService for:**
- Conversational AI with function calling
- Complex reasoning and context management
- Streaming text generation

**STTService for:**
- Real-time speech recognition
- Continuous transcription
- VAD integration

**TTSService for:**
- Speech synthesis with timing control
- Interruption handling
- Text preprocessing and filtering

### Aggregator Usage

**Use Aggregators when:**
- Collecting multiple frames into context
- Managing conversation state
- Implementing timing-based collection
- Handling interruption strategies

**Context Aggregators:**
- `LLMUserContextAggregator`: User input collection
- `LLMAssistantContextAggregator`: Bot response collection
- `SentenceAggregator`: Text sentence boundaries

### Common Patterns

**Real-time Voice AI:**
```python
Pipeline([
    transport.input(),
    stt_service,
    llm_user_context_aggregator,
    llm_service,
    llm_assistant_context_aggregator, 
    tts_service,
    transport.output()
])
```

**Multimodal (Audio + Video):**
```python
ParallelPipeline(
    [audio_input, stt, llm, tts, audio_output],
    [video_input, vision, image_gen, video_output]
)
```

**Function Calling Bot:**
```python
# Register functions
llm_service.register_function("search", search_handler)
llm_service.register_function("weather", weather_handler)

# Standard pipeline with function calling enabled
Pipeline([transport.input(), stt, context_agg, llm, tts, transport.output()])
```

This architecture provides a robust, scalable foundation for building sophisticated real-time conversational AI applications with comprehensive error handling, interruption management, and multi-service integration capabilities.