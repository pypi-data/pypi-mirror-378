# Pipeline Testing Guide

This guide explains how to test Pipecat pipeline frame sequences without making telephony calls.

## Overview

The `pipeline_test.py` script allows you to:

1. **Simulate Frame Sequences**: Programmatically send `UserStartedSpeakingFrame` → `UserStoppedSpeakingFrame` → `TranscriptionFrame` with precise timing
2. **Observe Pipeline Behavior**: Detailed logging of frame processing and timing
3. **Test Bot Execution**: See how your bot pipeline handles the frame sequence
4. **No Telephony Required**: Pure code-based testing without external calls

## Test Script Features

### Frame Sequence Simulation
- **UserStartedSpeakingFrame** at 50ms
- **UserStoppedSpeakingFrame** at 250ms  
- **TranscriptionFrame** at 330ms (80ms after UserStoppedSpeakingFrame)
- **BotInterruptionFrame** generation via LLMUserContextAggregator
- **Precise Timing Control** using asyncio delays

### Logging and Monitoring
- **Frame-by-frame tracking** with timestamps
- **Processing timing** in milliseconds
- **Pipeline lifecycle** monitoring
- **BotInterruptionFrame detection** and logging
- **Error handling** with detailed stack traces

### Components Tested
- **LLMUserContextAggregator**: Core component that handles user speech events and generates BotInterruptionFrame
- **FastAPI WebSocket Transport**: Real FastAPIWebsocketTransport with mock WebSocket for authentic behavior
- **Frame Processing Flow**: Complete pipeline showing BotInterruptionFrame → StartInterruptionFrame conversion
- **Interruption Flow**: Transport.input() receives BotInterruptionFrame upstream and sends StartInterruptionFrame downstream
- **Timing Relationships**: Frame sequence timing validation  
- **Pipeline Setup**: StartFrame initialization and configuration
- **LLM Integration**: Optional LLM service testing with context aggregation

## Usage

### Prerequisites

```bash
# Ensure you're in the ringg-chatbot directory
cd examples/ringg-chatbot

# Install dependencies
pip install -r requirements.txt

# Set up minimal environment (optional for LLM testing)
export OPENAI_API_KEY="your_key_here"  # Optional
```

### Running the Test

```bash
# Basic test execution
python pipeline_test.py

# With debug logging
PYTHONPATH=/Users/kalicharanvemuru/Documents/Code/pipecat/src python pipeline_test.py
```

### Expected Output

```
==============================================================
PIPECAT PIPELINE TEST - Frame Sequence Simulation  
==============================================================
14:32:15.123 | INFO     | Creating test pipeline with FastAPIWebsocketTransport and LLMUserContextAggregator...
14:32:15.124 | INFO     | LLM context initialized with system prompt: 1 messages
14:32:15.125 | INFO     | LLM service initialized for testing
14:32:15.127 | INFO     | Setting up test frame sequence...
14:32:15.128 | INFO     | Test sequence configured with 5 frames
14:32:15.130 | INFO     | Starting pipeline runner...
14:32:15.135 | INFO     | Starting test frame sequence...
14:32:15.136 | INFO     | Injecting StartFrame at 0.0ms
14:32:15.137 | INFO     | [FrameLogger] Frame #1 at 1.2ms: StartFrame - Direction: DOWNSTREAM
14:32:15.186 | INFO     | Injecting UserStartedSpeakingFrame at 50.1ms  
14:32:15.187 | INFO     | [FrameLogger] Frame #2 at 51.3ms: UserStartedSpeakingFrame - Direction: DOWNSTREAM
14:32:15.387 | INFO     | Injecting UserStoppedSpeakingFrame at 251.4ms
14:32:15.388 | INFO     | [FrameLogger] Frame #3 at 252.6ms: UserStoppedSpeakingFrame - Direction: DOWNSTREAM
14:32:15.467 | INFO     | Injecting TranscriptionFrame at 331.8ms
14:32:15.468 | INFO     | [FrameLogger] Frame #4 at 333.0ms: TranscriptionFrame - Direction: DOWNSTREAM
14:32:15.469 | INFO     | → Transcription: 'Hello, I need help with my account' (final)
14:32:15.472 | INFO     | [FrameLogger] Frame #5 at 336.1ms: BotInterruptionFrame - Direction: UPSTREAM
14:32:15.473 | INFO     | → Bot Interruption Frame detected! (flows upstream)
14:32:15.474 | INFO     | [FrameLogger] Frame #6 at 337.8ms: OpenAILLMContextFrame - Direction: DOWNSTREAM
14:32:15.475 | INFO     | → LLM Context Frame: 2 messages
14:32:15.476 | INFO     |     [0] system: You are a helpful customer service assistant for a telecommunications company...
14:32:15.477 | INFO     |     [1] user: Hello, I need help with my account
14:32:15.478 | INFO     | [FrameLogger] Frame #7 at 340.2ms: StartInterruptionFrame - Direction: DOWNSTREAM
14:32:15.479 | INFO     | → Start Interruption Frame detected! (flows downstream)
14:32:15.637 | INFO     | Test sequence completed
14:32:17.640 | INFO     | Pipeline test completed successfully
```

## Customization

### Modifying Frame Timing

Edit the `setup_test_frames()` function:

```python
# Adjust delays in milliseconds
source.add_test_frame(user_started, delay_ms=100)     # 100ms delay
source.add_test_frame(user_stopped, delay_ms=200)     # 300ms total
source.add_test_frame(transcription, delay_ms=50)     # 50ms after stopped
```

### Adding Custom Frames

```python
# Add more frame types to the sequence
from pipecat.frames.frames import InterimTranscriptionFrame

interim_transcription = InterimTranscriptionFrame(
    text="Hello, I need help...",
    user_id="test_user", 
    timestamp=time_now_iso8601()
)
source.add_test_frame(interim_transcription, delay_ms=150)
```

### Custom Frame Processor

Create your own processor to test specific behavior:

```python
class MyTestProcessor(FrameProcessor):
    async def process_frame(self, frame, direction: FrameDirection):
        if isinstance(frame, TranscriptionFrame):
            # Custom logic for transcription handling
            logger.info(f"Processing transcription: {frame.text}")
            # Add your bot logic here
        
        await self.push_frame(frame, direction)
```

### Integration with Ringg-Chatbot

To test with your actual bot configuration:

```python
# Import your bot components
from bot import create_bot_pipeline
from env_config import api_config

async def create_test_pipeline():
    # Use your actual bot configuration
    call_config = {
        "llm_provider": "openai",
        "llm_model": "gpt-4o-mini",
        "language": "en-US",
        # ... your config
    }
    
    # Create your actual bot pipeline
    pipeline = await create_bot_pipeline(call_config)
    return pipeline, source  # Add your test source
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Set Python path explicitly
   export PYTHONPATH="/Users/kalicharanvemuru/Documents/Code/pipecat/src:$PYTHONPATH"
   ```

2. **LLM Service Errors**
   - The script works without LLM services
   - Set `OPENAI_API_KEY` for full LLM testing
   - Check `utils/llm.py` initialization

3. **Timing Issues**
   - Adjust delays in `setup_test_frames()`
   - Monitor logs for actual vs expected timing
   - Consider system load effects on timing

### Debug Mode

Enable more detailed logging:

```python
# In pipeline_test.py, change logging level
logger.add(
    sys.stdout,
    level="DEBUG",  # Changed from INFO
    format="<green>{time:HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | {message}",
    colorize=True
)
```

## Testing Different Scenarios

### Scenario 1: Fast User Input
```python
# Quick speech pattern
source.add_test_frame(user_started, delay_ms=10)
source.add_test_frame(user_stopped, delay_ms=50)    # 60ms total
source.add_test_frame(transcription, delay_ms=30)   # 30ms after stopped
```

### Scenario 2: Interrupted Speech
```python
# Add interruption frames
from pipecat.frames.frames import StartInterruptionFrame, StopInterruptionFrame

interruption_start = StartInterruptionFrame()
source.add_test_frame(interruption_start, delay_ms=100)

interruption_stop = StopInterruptionFrame()  
source.add_test_frame(interruption_stop, delay_ms=150)
```

### Scenario 3: Multiple Transcriptions
```python
# Test multiple quick transcriptions
transcription1 = TranscriptionFrame(text="Hello", user_id="test", timestamp=time_now_iso8601())
transcription2 = TranscriptionFrame(text="How are you?", user_id="test", timestamp=time_now_iso8601())

source.add_test_frame(transcription1, delay_ms=100)
source.add_test_frame(transcription2, delay_ms=150)
```

This testing framework allows you to validate your bot's frame processing behavior, timing characteristics, and response patterns without requiring actual telephony infrastructure.