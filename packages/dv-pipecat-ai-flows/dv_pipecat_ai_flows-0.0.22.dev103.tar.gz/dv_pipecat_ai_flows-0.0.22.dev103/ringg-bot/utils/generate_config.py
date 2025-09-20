from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union, Literal
from loguru import logger

# Import direct flow tools
from utils.flow_tools.query_kb import query_kb
from utils.flow_tools.stay_on_line import stay_on_line
from utils.flow_tools.dtmf_output import dtmf_output
from utils.flow_tools.switch_language import switch_language
from utils.flow_tools.end_call import end_call
from utils.flow_tools.call_transfer import call_transfer
from utils.flow_tools.wait_for_dtmf import wait_for_dtmf
from utils.flow_tools.generic_function import generic_function
from pipecat_flows import ContextStrategyConfig, ContextStrategy
from pipecat_flows.types import FlowsFunctionSchema


class VoicemailConfig(BaseModel):
    detect: bool
    action: str
    retry: bool


class VoiceConfig(BaseModel):
    gender: str
    speed: float


class BackgroundAudioConfig(BaseModel):
    audio_id: str


class FillerConfig(BaseModel):
    enable_filler_words: bool
    filler_words: List[str] = Field(default_factory=list)
    filler_frequency: float = 0.2


class NoiseFilterConfig(BaseModel):
    filter_noise: bool = False
    method: str = "pyrnn_filter"


class DTMFInputConfig(BaseModel):
    timeout: float = 5.0
    digits: Optional[int] = None
    end: Optional[str] = ""
    reset: Optional[str] = None


class CallConfig(BaseModel):
    llm_provider: str
    llm_model: str
    llm_temperature: float
    pre_query_response_phrases: List[str] = Field(default_factory=list)
    stt_provider: str
    stt_model: Optional[str] = None
    tts_provider: str
    voice: str
    language: str
    vocab: List[str] = Field(default_factory=list)
    add_langs: List[str] = Field(default_factory=list)
    advanced_vad: bool
    timezone: str
    max_call_length: int
    idle_timeout_warning: int
    idle_timeout_end: int
    voicemail: VoicemailConfig
    voice_config: VoiceConfig
    telephony_provider: str
    record_locally: Optional[bool] = False
    record: Optional[bool] = False
    dialect: Optional[str] = None
    enable_smart_turn: Optional[bool] = False
    call_hold_config: Optional[Dict[str, Any]] = {"detect": False, "end_count": 3}
    mute_during_intro: Optional[bool] = False
    mute_while_bot_speaking: Optional[bool] = False
    vad_input: Optional[str] = None
    use_tts_cache: Optional[bool] = False
    background_audio_config: Optional[BackgroundAudioConfig] = None
    tts_model: Optional[str] = None
    azure_deployment: Optional[str] = None
    filler_config: Optional[FillerConfig] = None
    dtmf_input: Optional[DTMFInputConfig] = None
    initialize_rag: Optional[bool] = False
    rag_collection_name: Optional[str] = None
    rag_facets_collection_name: Optional[str] = None
    room_name: Optional[str] = None
    media_type: Optional[Literal["text", "audio"]] = None
    codec: Optional[str] = None
    sample_rate: Optional[int] = None
    noise_filter_config: Optional[NoiseFilterConfig] = None
    use_elevenlabs_v2_key: Optional[bool] = False
    # these are only for single node agents
    prompt: Optional[str] = None
    kb_data: Optional[List] = None
    tools: Optional[List] = None
    intro_message: Optional[str] = None


class ContextStrategyCustom(BaseModel):
    strategy: Literal["reset", "append", "reset_with_summary"]
    summary_prompt: Optional[str] = None


class RoleMessage(BaseModel):
    role: str
    content: str


class Action(BaseModel):
    type: str
    text: Optional[str] = None
    # TTS-specific parameters
    use_cache: Optional[bool] = None
    mirror_context: Optional[bool] = None


class FunctionParameters(BaseModel):
    type: str
    properties: Dict[str, Any]
    required: List[str] = Field(default_factory=list)


class TransitionFunction(BaseModel):
    name: str
    description: str
    parameters: FunctionParameters
    transition_to: Optional[str] = None


class HttpConfig(BaseModel):
    url: str
    method: str
    headers: Optional[Dict[str, str]] = None
    query_params: Optional[Dict[str, Any]] = None
    body: Optional[Dict[str, Any]] = None


class ApiFunction(BaseModel):
    name: str
    description: str
    parameters: FunctionParameters
    handler: Literal["_function_:generic_function"]
    http: Optional[HttpConfig] = None  # Optional when handler is _function_:generic_function
    cache_ttl: Optional[int] = None
    cache_response: Optional[bool] = None
    response_formatter: Optional[str] = None
    responseSelectedKeys: List[str] = Field(default_factory=list)


class TransitionFunctionWrapper(BaseModel):
    type: str
    function: TransitionFunction


class ApiFunctionWrapper(BaseModel):
    type: str
    function: ApiFunction


class Node(BaseModel):
    context_strategy: ContextStrategyCustom
    role_messages: List[RoleMessage] = Field(default_factory=list)
    task_messages: List[RoleMessage]
    predefined_tools: List[Union[str, Dict[str, Any]]] = Field(
        default_factory=list
    )  # List of predefined tool names or configs
    pre_actions: List[Action] = Field(default_factory=list)
    post_actions: List[Action] = Field(default_factory=list)
    functions: List[ApiFunctionWrapper] = Field(default_factory=list)  # Custom API functions
    transition_functions: List[TransitionFunctionWrapper] = Field(default_factory=list)
    respond_immediately: bool
    # Node-level overrides for any global configuration (DTMF, VAD, etc.)
    overrides: Optional[Dict[str, Any]] = None


class FlowConfig(BaseModel):
    initial_node: str
    nodes: Dict[str, Node]


class RunConfig(BaseModel):
    call_id: str
    workspace_id: Optional[str] = None
    update_call_status_url: str
    call_type: Literal["inbound", "outbound", "webcall"]
    orchestration_mode: Literal["single_node", "multi_node"]
    call_config: CallConfig
    flow_config: Optional[FlowConfig] = None
    from_number: Optional[str] = None
    recipient_phone_number: Optional[str] = None
    endpoint: Optional[str] = None
    trunk_owner: Optional[str] = None


def generate_runtime_config_object(config_data: dict) -> RunConfig:
    """
    Generate a RunConfig object from the provided configuration data.

    Args:
        config_data: Dictionary containing call configuration data

    Returns:
        RunConfig: Pydantic model with validated configuration
    """
    # Parse the data using the from_number field name
    config_data_copy = config_data.copy()
    logger.info(f"Config data: {config_data_copy}")
    if "from" in config_data_copy:
        config_data_copy["from_number"] = config_data_copy.pop("from")

    # Normalize language codes for hindi
    if "call_config" in config_data_copy:
        call_config = config_data_copy["call_config"]

        # Handle primary language
        if "language" in call_config and call_config["language"].lower() == "hi-in":
            call_config["language"] = "hi"

        # Handle additional languages
        if "add_langs" in call_config and call_config["add_langs"]:
            normalized_langs = []
            for lang in call_config["add_langs"]:
                if lang.lower() == "hi-in":
                    normalized_langs.append("hi")
                else:
                    normalized_langs.append(lang)
            call_config["add_langs"] = normalized_langs

    return RunConfig(**config_data_copy)


def _create_generic_function_handler(function_name: str):
    """Create a flow-native handler for a custom API function."""

    async def handler(args, flow_manager):
        # Call the generic_function with the specific function name
        return await generic_function(flow_manager, function_name, **args)

    return handler


def _process_action(action: Action) -> dict:
    """Process action configuration for tts_say actions."""
    action_dict = action.model_dump()

    # For tts_say actions, ensure mirror_context is enabled to prevent duplicate greetings
    if action.type == "tts_say":
        if action.mirror_context is None:
            action_dict["mirror_context"] = True
        # Disable caching for now to avoid pipeline issues
        if action.use_cache is None:
            action_dict["use_cache"] = False

    return {k: v for k, v in action_dict.items() if v is not None}


def generate_context_strategy(context_strategy: ContextStrategyCustom):
    if context_strategy.strategy == "reset":
        return ContextStrategyConfig(strategy=ContextStrategy.RESET)
    elif context_strategy.strategy == "append":
        return ContextStrategyConfig(strategy=ContextStrategy.APPEND)
    elif context_strategy.strategy == "reset_with_summary":
        return ContextStrategyConfig(
            strategy=ContextStrategy.RESET_WITH_SUMMARY,
            summary_prompt=context_strategy.summary_prompt,
        )


def parse_flow_config_to_pipecat(
    flow_config: FlowConfig, *, deps: Optional[Dict[str, Any]] = None
) -> dict:
    """
    Convert our FlowConfig format to pipecat-flows compatible format.

    Args:
        flow_config: Our internal FlowConfig object
        deps: Dependencies dictionary for handlers

    Returns:
        dict: Pipecat-flows compatible configuration
    """
    deps = deps or {}

    pipecat_config = {"initial_node": flow_config.initial_node, "nodes": {}}

    for node_name, node in flow_config.nodes.items():
        pipecat_node = {
            "role_messages": [msg.model_dump() for msg in node.role_messages]
            if node.role_messages
            else [],
            "task_messages": [msg.model_dump() for msg in node.task_messages],
            "functions": [],
            "pre_actions": [_process_action(action) for action in node.pre_actions],
            "post_actions": [_process_action(action) for action in node.post_actions],
            "context_strategy": generate_context_strategy(node.context_strategy),
        }

        # Add predefined tool functions (direct functions)
        for tool_dict in node.predefined_tools:
            tool_name = tool_dict.get("name")
            tool_func = get_predefined_tool_function(tool_name, tool_dict)
            if tool_func:
                pipecat_node["functions"].append(tool_func)

        # Convert transition functions to pipecat format using FlowsFunctionSchema
        for func_wrapper in node.transition_functions:
            func = func_wrapper.function
            transition_func_schema = FlowsFunctionSchema(
                name=func.name,
                description=func.description,
                properties=func.parameters.properties,
                required=func.parameters.required,
                handler=create_transition_handler(func.transition_to),
            )
            pipecat_node["functions"].append(transition_func_schema)

        # Convert API functions to pipecat format (custom tools)
        for func_wrapper in node.functions:
            func = func_wrapper.function
            # Create a flow-native generic handler for this specific function
            handler_callable = _create_generic_function_handler(func.name)

            # Create FlowsFunctionSchema for custom tools
            custom_func_schema = FlowsFunctionSchema(
                name=func.name,
                description=func.description,
                properties=func.parameters.properties,
                required=func.parameters.required,
                handler=handler_callable,
            )
            pipecat_node["functions"].append(custom_func_schema)

        pipecat_config["nodes"][node_name] = pipecat_node

    return pipecat_config


def create_transition_handler(target_node: str):
    """
    Create a handler function for state transitions.

    Args:
        target_node: The node to transition to

    Returns:
        Async function that returns transition tuple
    """

    async def handler(args, flow_manager):
        return {"status": "ok"}, target_node

    return handler


def _generate_query_kb_function(tool_name: str, tool_config: Dict[str, Any]) -> FlowsFunctionSchema:
    """
    Generate a FlowsFunctionSchema for query_kb tools with dynamic properties.

    Args:
        tool_name: Name of the KB tool (e.g., "query_kb_customer_data")
        tool_config: Configuration containing kb_id, type, and search_fields

    Returns:
        FlowsFunctionSchema for the KB tool
    """
    # Base properties that are always present
    properties = {
        "kb_id": {
            "type": "string",
            "description": "The unique identifier of the knowledge base to query",
        },
        "question": {
            "type": "string",
            "description": "The question to query the knowledge base with. Include as much context and specific details as possible to ensure that the retrieval-augmented generation process can fetch the most relevant records and generate an accurate answer.",
        },
    }

    required = ["kb_id", "question"]

    # Add search field properties for deterministic KBs
    kb_type = tool_config.get("type", "non_deterministic")
    if kb_type == "deterministic":
        search_fields = tool_config.get("search_fields", [])
        for field in search_fields:
            field_name = field.get("field_name")
            field_description = field.get("description", f"The {field_name} field")
            field_type = field.get("field_type", "string")

            if field_name:
                properties[field_name] = {"type": field_type, "description": field_description}
                # All search fields are required for deterministic search
                required.append(field_name)

    # Generate appropriate description based on KB type
    if kb_type == "deterministic":
        description = f"Query the knowledge base for specific data using structured search parameters. This is a deterministic search that requires exact field values to retrieve precise results."
    else:
        description = "Retrieve and synthesize a concise answer from the knowledge base based on the given question. The input should include detailed context and any relevant keywords to enable accurate and targeted search results. This tool uses a retrieval-augmented generation approach to extract key information from stored records, so providing maximum relevant details will improve the quality of the generated answer."

    return FlowsFunctionSchema(
        name=tool_name,
        description=description,
        properties=properties,
        required=required,
        handler=query_kb,
    )


def get_predefined_tool_function(tool_name: str, tool_config: Optional[Dict[str, Any]] = None):
    """
    Get the FlowsFunctionSchema for a predefined tool.

    Args:
        tool_name: Name of the predefined tool
        tool_config: Optional tool configuration for dynamic tools like query_kb

    Returns:
        FlowsFunctionSchema or None if not found
    """
    # Handle dynamic KB tools
    if tool_name and tool_name.startswith("query_kb"):
        return _generate_query_kb_function(tool_name, tool_config or {})

    predefined_tools = {
        "end_call": FlowsFunctionSchema(
            name="end_call",
            description="End the current call when the conversation has reached a natural conclusion or user says bye or tells to cut the call or speak with you later as they are busy.",
            properties={
                "final_message": {
                    "type": "string",
                    "description": "The final message to say to the user before ending the call. Should be a polite goodbye message appropriate for the conversation context. Keep is short and less than 15 words.",
                }
            },
            required=["final_message"],
            handler=end_call,
        ),
        "stay_on_line": FlowsFunctionSchema(
            name="stay_on_line",
            description="Play hold music or messaging while the user waits on the line",
            properties={
                "duration": {
                    "type": "integer",
                    "description": "Duration in seconds to play hold music (default: 10)",
                }
            },
            required=[],
            handler=stay_on_line,
        ),
        "dtmf_output": FlowsFunctionSchema(
            name="dtmf_output",
            description="Generate DTMF tones to interact with phone systems",
            properties={
                "digits": {"type": "string", "description": "The DTMF digits to output (0-9, *, #)"}
            },
            required=["digits"],
            handler=dtmf_output,
        ),
        "switch_language": FlowsFunctionSchema(
            name="switch_language",
            description="Switch the conversation language dynamically",
            properties={
                "language": {
                    "type": "string",
                    "description": "The language code to switch to (e.g., 'en', 'hi', 'es')",
                }
            },
            required=["language"],
            handler=switch_language,
        ),
        "call_transfer": FlowsFunctionSchema(
            name="call_transfer",
            description="Transfer the current call to another phone number",
            properties={
                "phone_number": {
                    "type": "string",
                    "description": "The phone number to transfer the call to",
                },
                "message": {
                    "type": "string",
                    "description": "Optional message to say before transferring",
                },
            },
            required=["phone_number"],
            handler=call_transfer,
        ),
        "wait_for_dtmf": FlowsFunctionSchema(
            name="wait_for_dtmf",
            description="Wait for DTMF input from the user",
            properties={
                "prompt": {
                    "type": "string",
                    "description": "The prompt to say to the user asking for DTMF input",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds to wait for input (default: 5)",
                },
            },
            required=["prompt"],
            handler=wait_for_dtmf,
        ),
    }

    return predefined_tools.get(tool_name)


def _resolve_node_overrides(
    global_config: CallConfig, node_overrides: Optional[Dict[str, Any]], node_name: str = "unknown"
) -> Dict[str, Any]:
    """
    Resolve node-level overrides by merging with global configuration.

    Args:
        global_config: Global call configuration
        node_overrides: Node-specific override configuration

    Returns:
        Dict with resolved configurations for all supported systems
    """
    resolved = {}

    if node_overrides and "dtmf" in node_overrides:
        dtmf_override = node_overrides["dtmf"]
        # If node specifies DTMF, it should be enabled even if global doesn't have it
        global_dtmf = global_config.dtmf_input if global_config.dtmf_input else None
        resolved["dtmf"] = {
            "timeout": dtmf_override.get("timeout", global_dtmf.timeout if global_dtmf else 3.0),
            "digits": dtmf_override.get("digits", global_dtmf.digits if global_dtmf else None),
            "end": dtmf_override.get("end", global_dtmf.end if global_dtmf else ""),
            "reset": dtmf_override.get("reset", global_dtmf.reset if global_dtmf else None),
        }
    elif global_config.dtmf_input:
        # Use global DTMF config if no node override
        resolved["dtmf"] = {
            "timeout": global_config.dtmf_input.timeout,
            "digits": global_config.dtmf_input.digits,
            "end": global_config.dtmf_input.end,
            "reset": global_config.dtmf_input.reset,
        }

    # Handle TTS overrides
    if node_overrides and "tts" in node_overrides:
        tts_override = node_overrides["tts"]
        logger.debug(f"Processing TTS override for node '{node_name}': {tts_override}")
        resolved["tts"] = {
            "provider": tts_override.get("provider", global_config.tts_provider),
            "voice_id": tts_override.get("voice_id", global_config.voice),
            "language": tts_override.get("language", global_config.language),
        }
        # Add voice_model if present (ElevenLabs specific)
        if "voice_model" in tts_override:
            resolved["tts"]["voice_model"] = tts_override["voice_model"]
        elif global_config.tts_model:
            resolved["tts"]["voice_model"] = global_config.tts_model
        logger.debug(f"Generated TTS resolved override for node '{node_name}': {resolved['tts']}")

    return resolved


def generate_data_access_config(
    runtime_config: RunConfig, call_config: CallConfig
) -> Dict[str, Dict[str, Any]]:
    """
    Extract node-specific configurations from runtime_config for quick O(1) lookup.
    Now also processes node-level overrides and merges them with global config.

    Args:
        runtime_config: Original runtime configuration from API
        call_config: Call configuration with defaults (Pydantic model)

    Returns:
        Dict mapping {node_name: {functions: {function_name: config_params}, resolved_overrides: {...}}}
    """
    data_access_node_config = {}

    # Get flow_config from runtime_config
    flow_config = runtime_config.flow_config
    # Access nodes attribute directly from Pydantic model
    nodes = flow_config.nodes if flow_config.nodes else {}

    for node_name, node in nodes.items():
        # Access node attributes directly from Pydantic model
        data_access_node_config[node_name] = {
            "functions": {},
            # Resolved node overrides merged with global config
            "resolved_overrides": _resolve_node_overrides(call_config, node.overrides if node.overrides else None, node_name),
        }

        # Extract predefined tool configs
        predefined_tools = node.predefined_tools if node.predefined_tools else []
        for tool in predefined_tools:
            tool_name = tool.get("name") if isinstance(tool, dict) else tool

            if tool_name and tool_name.startswith("query_kb"):
                # Handle dynamic KB tools (query_kb_customer_data, query_kb_support_docs, etc.)
                data_access_node_config[node_name]["functions"][tool_name] = {
                    "kb_id": tool.get("kb_id"),
                    "type": tool.get("type", "non_deterministic"),
                    "search_fields": tool.get("search_fields", []),
                    "collection_name": call_config.rag_collection_name,
                }
            elif tool_name == "wait_for_dtmf":
                # Handle wait_for_dtmf tool with its configuration
                dtmf_config = tool.get("dtmf_config", {}) if isinstance(tool, dict) else {}
                if dtmf_config:
                    data_access_node_config[node_name]["functions"]["wait_for_dtmf"] = {
                        "dtmf_config": dtmf_config
                    }

        # Extract custom function configs from ApiFunctionWrapper functions
        functions = node.functions if node.functions else []
        for func_wrapper in functions:
            if isinstance(func_wrapper, dict) and "function" in func_wrapper:
                func = func_wrapper["function"]
                func_name = func["name"]

                data_access_node_config[node_name]["functions"][func_name] = {
                    "http_parameters": func.get("http", {}),
                    "cache_ttl": func.get("cache_ttl", 0),
                    "cache_response": func.get("cache_response", False),
                    "response_formatter": func.get("response_formatter"),
                    "responseSelectedKeys": func.get("responseSelectedKeys", []),
                }

    return data_access_node_config


def create_api_handler(api_func):
    """
    Create a handler function for API calls.

    Args:
        api_func: The API function configuration

    Returns:
        Async function that makes the API call
    """

    async def handler(args):
        # This will be replaced with actual API call logic
        # For now, just return None and stay in current state
        return args, None

    return handler
