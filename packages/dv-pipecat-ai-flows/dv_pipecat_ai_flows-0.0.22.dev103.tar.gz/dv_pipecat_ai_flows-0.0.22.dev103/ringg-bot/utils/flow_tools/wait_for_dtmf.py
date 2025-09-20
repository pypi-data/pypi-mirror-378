"""Flow-native wait_for_dtmf tool implementation."""

from pipecat_flows import FlowManager
from pipecat.frames.frames import WaitForDTMFFrame
from pipecat.processors.frame_processor import FrameDirection


async def wait_for_dtmf(flow_manager: FlowManager):
    """
    Wait for the user to press a DTMF digit on the keypad.

    Returns:
        ConsolidatedFunctionResult tuple (result, next_node)
    """
    s = flow_manager.state
    logger = s.get("bot_logger")
    monitor = s.get("function_call_monitor", [])

    monitor.append("wait_for_dtmf_called")

    if logger:
        logger.info("Waiting for DTMF input...")

    try:
        await flow_manager.llm.push_frame(WaitForDTMFFrame(), FrameDirection.UPSTREAM)
        return ({"status": "success", "data": {"message": "Waiting for DTMF input"}}, None)
    except Exception as e:
        if logger:
            logger.error(f"Error waiting for DTMF: {e}")
        return (
            {
                "status": "error", 
                "error": "Looks like there's some error in noting the number entered on keypad"
            }, 
            None
        )
