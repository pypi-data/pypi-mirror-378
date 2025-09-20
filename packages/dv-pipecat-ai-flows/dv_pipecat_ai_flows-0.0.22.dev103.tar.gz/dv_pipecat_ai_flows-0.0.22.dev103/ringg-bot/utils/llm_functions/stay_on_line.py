# import
from utils.stay_on_line_processor import StayOnLineProcessor

from pipecat.frames.frames import (
    FunctionCallResultProperties,
    LLMMessagesAppendFrame,
    TTSSpeakFrame,
)
from pipecat.services.llm_service import FunctionCallResultCallback

stay_on_line_tool = {
    "name": "stay_on_line",
    "description": "When the user asks you to wait or hold on or stay on the line, call this function to wait for that duration. And then after that duration, we will resume the call.",
    "parameters": {
        "type": "object",
        "properties": {
            "duration": {
                "type": "integer",
                "description": "The duration in seconds to wait for the user. Default 60.",
            },
            "message": {
                "type": "string",
                "description": "An optional message to say to the user before waiting (e.g., 'Okay, I will wait.').",
            },
        },
        "required": [],
    },
}


async def stay_on_line_handler(
    function_name: str,
    tool_call_id: str,
    args: dict,
    llm,
    context,
    result_callback: FunctionCallResultCallback,
    function_call_monitor,
    stay_on_line_processor: StayOnLineProcessor,
    bot_logger,
):
    try:
        duration = args.get("duration", 60)
        message = args.get("message", "")
        bot_logger.info(f"User requested hold for {duration}s")
        function_call_monitor.append("stay_on_line_called")
        # If the LLM provided a message, push a frame to the TTS service to speak it.
        if message:
            await llm.push_frame(TTSSpeakFrame(text=message))
            # ALSO, push a frame to add the spoken message to the assistant's context.
            assistant_message = {"role": "assistant", "content": message}
            await llm.push_frame(LLMMessagesAppendFrame(messages=[assistant_message]))
        # Initiate hold
        await stay_on_line_processor.start_hold(duration, context)
        # Return immediately (no spoken reply)
        await result_callback(
            f"Staying online. Waiting for {duration} seconds for the user to resume the call.",
            properties=FunctionCallResultProperties(run_llm=False),
        )
    except Exception as e:
        bot_logger.error(f"Error staying online: {e}")
        await result_callback(None)
