# Pipecat Flows Agent Handbook

## Mission & Context
- **Primary goal**: build controllable voice agents that split work across multiple conversation nodes using the new flow framework under `src/pipecat_flows/` and the `ringg-bot/` runtime. The legacy single-agent example at `/Users/kalicharanvemuru/Documents/Code/dv-pipecat/examples/ringg-chatbot` is now read-only reference material.
- **Old vs new**: the old example bundled telephony orchestration, business logic, and prompts into one monolithic agent. This repository decouples those responsibilities into FlowManager-driven nodes so that each task (greeting, authentication, routing, escalation, etc.) has its own state, context policy, actions, and tool set.
- **Authoritative docs** live here. Copy anything you need from the old repo, but always implement against the structures described below. Do not point LLMs back to `examples/ringg-chatbot` when you want code changes.

## Where Things Live Now
- `src/pipecat_flows/` &nbsp;— reusable flow engine (FlowManager, adapters, action execution, shared types).
- `ringg-bot/` &nbsp;— production bot implementation that consumes FlowManager. Contains runtime config parsing, transport setup, telephony serializers, utilities, and flow-specific tools.
  - `ringg-bot/utils/generate_config.py` converts runtime JSON into strongly-typed configs and into Pipecat Flow node definitions.
  - `ringg-bot/utils/flow_tools/` holds flow-native functions (query KB, transfer calls, wait for DTMF, etc.) that are registered as node tools.
  - `ringg-bot/transports/` and `ringg-bot/voice_services/` wrap telephony/WebRTC integrations and provider-specific audio services.
  - `ringg-bot/PIPECAT_ARCHITECTURE.md` (synced from the old repo) is the deep dive on base Pipecat pipeline, frames, and processor architecture.
- `tests/` mirrors `src/pipecat_flows/` for unit coverage. Bot-level simulations live under `ringg-bot/tests/` and leverage the pipeline testing harness.

## Flow Engine Essentials (`src/pipecat_flows`)
- **`FlowManager`** (`manager.py`) orchestrates node lifecycles. It:
  - Registers tools/functions with the active LLM service via provider adapters (`adapters.py`).
  - Executes `pre_actions` and `post_actions` via `ActionManager` (`actions.py`) while respecting downstream frame ordering and bot speaking state.
  - Tracks shared `state`, pending transitions, and context strategy per node (`types.ContextStrategyConfig`).
  - Understands both **static flows** (predefined `FlowConfig`) and **dynamic flows** (runtime node injection).
- **Context strategies**: `APPEND`, `RESET`, `RESET_WITH_SUMMARY`. Summaries are generated through provider adapters when `summary_prompt` is supplied.
- **Function schemas**: wrap each callable (direct Python coroutine, JSON schema-defined function, or legacy dict) in a `FlowsFunctionSchema` so FlowManager can:
  - derive name/description/parameters,
  - register it with the provider adapter,
  - route tool calls to the correct Python handler.
- **Actions**: `tts_say`, `end_conversation`, and `function` are built-ins. You can register custom action handlers on `ActionManager` or attach inline `function` actions that execute coroutine callbacks inside the pipeline without breaking frame ordering.
- **Error taxonomy**: `FlowInitializationError`, `FlowTransitionError`, `InvalidFunctionError`, `ActionError`. Make sure LLM prompts surface these when asking for diagnostics.

## Runtime Configuration & Multi-Node Design
- **Entry format**: external orchestrator sends JSON that matches `ringg-bot/utils/generate_config.RunConfig`.
  - `orchestration_mode` determines single vs multi node but our default is multi-node.
  - `flow_config` defines each node: `role_messages`, `task_messages`, context policy, `pre_actions`, `post_actions`, and two tool buckets:
    - `predefined_tools`: shortcuts for built-in direct functions (`query_kb`, `stay_on_line`, `dtmf_output`, `switch_language`, `end_call`, `call_transfer`, `wait_for_dtmf`).
    - `functions`: API-backed or generic adapters that call out to HTTP endpoints via `_function_:generic_function` with optional caching/formatters.
    - `transition_functions`: explicit state transitions that return `{status, next_node}` pairs.
- `parse_flow_config_to_pipecat()` turns that JSON into a FlowManager-ready dict by:
  - Turning every tool into a `FlowsFunctionSchema` with bound handlers.
  - Normalizing action configs (auto enabling `mirror_context` on `tts_say`, disabling cache by default).
  - Resolving `ContextStrategyCustom` into `ContextStrategyConfig`.
- **Runtime overrides** (`Node.overrides`) let you change VAD, fillers, DTMF, or other channel-specific settings for a single node and are consumed when the bot builds pipeline processors.

## How the Bot Uses Flows (`ringg-bot/bot_with_flows.py`)
1. **Config ingestion**: `generate_call_config()` normalizes payload (language codes, `from` → `from_number`, etc.) and returns `RunConfig` with nested `CallConfig` + `FlowConfig`.
2. **Service bootstrap** (`utils/bot_common.initialize_services`): spins up LLM/STT/TTS providers based on the call config (supports OpenAI, Azure, Groq, Vistaar, Deepgram, ElevenLabs, etc.). Handles voice options, vocab injection, caching toggles, and noise filtering.
3. **Pipeline wiring**:
   - Builds `PipelineTask`, transports (`transports.factory.build_transport`), VAD analyzers (`SileroVADAnalyzer`), smart turn modules, background audio mixers, transcript handlers, Redis clients, and hold/idle detectors.
   - Generates `pipecat_flow_config` via `parse_flow_config_to_pipecat` and instantiates `FlowManager` with:
     - Pipeline task for frame scheduling.
     - LLM service + provider adapter auto-detected in `FlowManager.__init__`.
     - `context_aggregator` based on `OpenAILLMContext` (or provider equivalent via adapters).
     - Transport reference so actions can push frames directly.
4. **Execution loop**: the pipeline runner streams frames between transport → STT → FlowManager-controlled LLM → TTS → transport. `ActionManager` uses special frames (`FunctionActionFrame`, `ActionFinishedFrame`, `BotStoppedSpeakingFrame`) to respect downstream ordering and to trigger deferred `post_actions` only after the bot finishes speaking.
5. **State transitions**: node functions call `flow_manager.set_next_node(...)` (via transition handlers) or return `(FlowResult, next_node)` tuples. Context strategies determine how chat history is preserved when switching nodes.
6. **Shutdown**: `end_call` tools/actions push `EndFrame` and clean up transports, mixers, Redis locks, Weaviate connections, and local recordings.

## Toolkit Summary
- **Predefined direct tools** (flow-native and coroutine friendly):
  - `query_kb`: retrieval-augmented answers with optional deterministic field filters; uses `rag/weaviate_script.py` client and respects `rag_collection_name`.
  - `stay_on_line`: keeps participant engaged while escalation or manual join happens.
  - `dtmf_output`, `wait_for_dtmf`: output tones and collect keypad input with optional timeout/digit requirements.
  - `switch_language`: swaps STT/TTS configuration mid-call.
  - `end_call`: gracefully hang up with optional reason phrases.
  - `call_transfer`: connects to live agent, updates telephony transport, and coordinates background audio fillers.
- **Generic API functions**: define `http` payload in config and FlowManager will call `_function_:generic_function`, transparently handle caching (`cache_ttl`, `cache_response`), and format responses (`response_formatter`, `responseSelectedKeys`).
- **Actions**:
  - `tts_say` supports `use_cache`, `mirror_context`, and custom text; it is rendered via `ActionManager._handle_tts_action` by pushing `TTSSpeakFrame` (with optional caching hook in `say_with_cache`).
  - `function` actions run inline async coroutines inside the pipeline (useful for analytics, notifications, or gating state).
  - `end_conversation` injects `EndFrame` and signals transports to hang up.

## Telephony & Transports
- `ringg-bot/server.py` exposes FastAPI HTTP + WebSocket endpoints for Twilio/Plivo/Exotel/Asterisk/ConVox streaming.
- Serializers (`utils/bot_common.get_telephony_serialiser`) adapt audio framing per provider (sample rates, codecs, auth details).
- Transports layer (`transports/`) adds WebRTC (Daily Web Call), WebSocket bridging, and channel-aware configuration through `build_transport`.
- Voice services (`voice_services/`) encapsulate provider-specific quirks (e.g., ElevenLabs v1/v2 API selection, Azure deployment names, Cartesia streaming) so FlowManager stays provider-agnostic.

## Testing & Diagnostics
- `ringg-bot/PIPELINE_TESTING.md` documents frame-level simulations. Use `pipeline_test.py` to feed deterministic frame sequences (user start/stop speaking, transcriptions, interruptions) through the full pipeline without telephony.
- `tests/test_manager.py`, `tests/test_actions.py`, etc., cover FlowManager and ActionManager edge cases (context resets, action ordering, function registration). Extend these tests when adding new features.
- Logging: the bot binds `call_id` to the logger context. Use `logger.bind(...)` when adding instrumentation so traces stay grouped per call.
- Retry & timeout knobs live in `utils/pipeline.py` (idle handlers, hold detector) and `utils/stay_on_line_processor.py`. Update both place and config schema when adjusting thresholds.

## Working Guidelines for LLM Instructions
- Always operate on `ringg-bot/` when modifying production bot logic. Do **not** resurrect `examples/ringg-chatbot`; mention it only as historical reference.
- When adding a new conversational capability:
  1. Extend the runtime schema in `utils/generate_config.py` (Pydantic models).
  2. Create tool/action implementation (prefer `utils/flow_tools` for node functions) with docstrings explaining purpose and expected args.
  3. Register tool via flow config (predefined or API) and ensure tests cover the new behavior.
  4. Update documentation (this file plus any relevant Markdown under `ringg-bot/`).
- Respect context policies: avoid hard-coding resets or summaries—use `ContextStrategyConfig`. Summaries rely on adapter-specific `generate_summary` implementations; provide `summary_prompt` when you expect the LLM to compress history.
- Keep transports and services stateless between calls; shared resources (Redis, Weaviate) must be acquired/released inside the call lifecycle.

## Reference Documents in This Repo
- `ringg-bot/PIPECAT_ARCHITECTURE.md` — deep dive on Pipecat frames, pipelines, services (copied from the legacy repo for completeness).
- `ringg-bot/DEPLOYMENT.md` — GKE deployment pipeline (branches, Helm charts, canary vs stable strategy).
- `ringg-bot/README.md` — Twilio/WebSocket quick start (update instructions here if startup commands change).
- `ringg-bot/PIPELINE_TESTING.md` — simulation harness documentation.
- `docs/` — broader Pipecat flows user guides (keep in sync when adding features).

## Quick FAQ
- **"Where do I define a new node?"** — In the runtime payload (`flow_config.nodes[...]`), then ensure `generate_config.py` understands any new fields you introduce.
- **"How do I trigger a node switch manually?"** — Transition function handlers return `(FlowResult, next_node)` or call `flow_manager.set_next_node(name)` inside the function.
- **"Can a node reuse tools from another node?"** — Yes, add the same predefined tool or API entry. Tool handlers are reusable coroutines; context policy determines how much prior conversation the node inherits.
- **"How do I speak immediately without waiting for TTS cache?"** — Set `use_cache: false` (default) or configure `mirror_context` to avoid echoing system prompts. `ActionManager` already queues speech frames correctly.
- **"Where is the single-node agent prompt now?"** — Legacy fields (`prompt`, `kb_data`, `tools`, `intro_message`) still exist in `CallConfig` for backwards compatibility but should be avoided. Use flow nodes instead.

## Next Steps
- Before coding, confirm the desired behavior aligns with FlowManager capabilities described above.
- Run `ruff` and `pytest` after changes; for telephony features, also run `python ringg-bot/pipeline_test.py` with relevant scenarios.
- Keep this handbook updated whenever new node types, tools, or transports are introduced.
