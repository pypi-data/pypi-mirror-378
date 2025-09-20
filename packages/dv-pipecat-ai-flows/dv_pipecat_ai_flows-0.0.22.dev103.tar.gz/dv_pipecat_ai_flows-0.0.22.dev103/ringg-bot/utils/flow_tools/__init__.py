"""Flow-native tool implementations for Pipecat Flows.

These tools follow the Flow function signature: (flow_manager, **args) -> FlowResult
"""

from .query_kb import query_kb
from .stay_on_line import stay_on_line
from .dtmf_output import dtmf_output
from .switch_language import switch_language
from .end_call import end_call
from .call_transfer import call_transfer
from .wait_for_dtmf import wait_for_dtmf
from .generic_function import generic_function

__all__ = [
    "query_kb",
    "stay_on_line",
    "dtmf_output",
    "switch_language",
    "end_call",
    "call_transfer",
    "wait_for_dtmf",
    "generic_function",
]