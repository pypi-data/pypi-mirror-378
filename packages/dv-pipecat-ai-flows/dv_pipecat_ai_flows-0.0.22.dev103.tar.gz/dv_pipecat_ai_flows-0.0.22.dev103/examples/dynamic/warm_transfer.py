#
# Copyright (c) 2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#
"""'Warm Handoff' Example using Pipecat Dynamic Flows with OpenAI.

This example demonstrates how to create a bot that transfers a customer to a human agent when the bot is unable to fulfill the customers's request.
This example uses:
- Pipecat Flows for conversation management
- OpenAI gpt-4o as the LLM
- Daily as the transport service

The bot asks how they could be of assistance, and offers to provide information about store location and hours of operation, or begin placing an order.
If the customer says they'd like to do the former, the bot provides an answer.
If the customer says they'd like to do the latter, the bot tries, fails, and transfers the customer to a human agent.
The bot then brings the agent up to speed on the customer's issue before connecting them to the customer and dropping out of the call.

The various parties join with the following Daily meeting token properties:
- bot:
  - owner: true
- customer:
  - user_id: customer
- human agent:
  - user_id: agent

The bot joins with a token with the following properties:
- owner: true

Requirements:
- Daily room URL
- Daily API key
- OpenAI API key
- Deepgram API key
- Cartesia API key
"""

import asyncio
import atexit
import os
import sys
from pathlib import Path
from typing import Any, Dict

import aiohttp
from dotenv import load_dotenv
from loguru import logger
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.services.cartesia.tts import CartesiaHttpTTSService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transports.services.daily import DailyParams, DailyTransport
from pipecat.transports.services.helpers.daily_rest import (
    DailyMeetingTokenParams,
    DailyMeetingTokenProperties,
    DailyRESTHelper,
)

from pipecat_flows import ContextStrategyConfig, FlowManager, FlowResult, NodeConfig
from pipecat_flows.types import ActionConfig, ContextStrategy, FlowArgs, FlowsFunctionSchema

sys.path.append(str(Path(__file__).parent.parent))
from runner import configure

load_dotenv(override=True)

logger.remove(0)
logger.add(sys.stderr, level="DEBUG")

# Flow nodes:
#
# 1. initial_customer_interaction
#    The initial node, where the bot interacts with the customer and tries to help with their requests.
#    Functions:
#    - check_store_location_and_hours_of_operation (always succeeds)
#    - start_order (always fails)
#    - end_customer_conversation
#    Transitions to either:
#    - continued_customer_interaction
#    - transferring_to_human_agent
#
# 2. continued_customer_interaction
#    The bot has already helped the customer with something. Now they're helping them with something else.
#    Functions:
#    - check_store_location_and_hours_of_operation (always succeeds)
#    - start_order (always fails)
#    - end_customer_conversation
#    Transitions to either:
#    - continued_customer_interaction
#    - transferring_to_human_agent
#
# 3. transferring_to_human_agent
#    The customer is asked to please hold while the bot transfers them to a human agent. Hold music plays while the customer waits.
#    Transition:
#    - As soon as the agent connects to the room, we transition to human_agent_interaction.
#
# 4. human_agent_interaction
#    The bot fills in the human agent about what the customer was trying to accomplish that the bot was unable to help with, and what went wrong.
#    The customer continues to hear hold music.
#    Functions:
#    - connect_human_agent_and_customer
#
# 5a. end_customer_conversation
#     The bot says goodbye to the customer and ends the conversation.
#     This is how a conversation ends when a human agent did not need to be brought in.
#
# 5b. end_human_agent_conversation
#     The bot tells the agent that they're being patched through to the customer and ends the conversation (leaving the customer and agent in the room talking to each other).


# Type definitions
class StoreLocationAndHoursOfOperationResult(FlowResult):
    store_location: str
    hours_of_operation: str


class StartOrderResult(FlowResult):
    pass


# Function handlers
async def check_store_location_and_hours_of_operation() -> tuple[
    StoreLocationAndHoursOfOperationResult, NodeConfig
]:
    """Check store location and hours of operation."""
    result = StoreLocationAndHoursOfOperationResult(
        status="success",
        store_location="123 Main St, Anytown, USA",
        hours_of_operation="9am to 5pm, Monday through Friday",
    )
    next_node = next_node_after_customer_task(result)
    return result, next_node


async def start_order() -> tuple[StartOrderResult, NodeConfig]:
    """Start a new order."""
    result = StartOrderResult(status="error")
    next_node = next_node_after_customer_task(result)
    return result, next_node


# Action handlers
async def mute_customer(action: dict, flow_manager: FlowManager):
    """Mute the customer.

    Do it by revoking their canSnd permission, which both mutes them and ensures that they can't unmute.
    """
    transport: DailyTransport = flow_manager.transport
    customer_participant_id = get_customer_participant_id(transport=transport)

    if customer_participant_id:
        await transport.update_remote_participants(
            remote_participants={
                customer_participant_id: {
                    "permissions": {
                        "canSend": [],
                    }
                }
            }
        )


async def start_hold_music(action: dict, flow_manager: FlowManager):
    hold_music_args = flow_manager.state["hold_music_args"]
    flow_manager.state["hold_music_process"] = await asyncio.create_subprocess_exec(
        sys.executable,
        str(hold_music_args["script_path"]),
        "-m",
        hold_music_args["room_url"],
        "-t",
        hold_music_args["token"],
        "-i",
        hold_music_args["wav_file_path"],
    )


async def make_customer_hear_only_hold_music(action: dict, flow_manager: FlowManager):
    """Make it so the customer only hears hold music.

    We don't want them hearing the bot and the human agent talking.
    """
    transport: DailyTransport = flow_manager.transport
    customer_participant_id = get_customer_participant_id(transport=transport)

    if customer_participant_id:
        await transport.update_remote_participants(
            remote_participants={
                customer_participant_id: {
                    "permissions": {"canReceive": {"byUserId": {"hold-music": True}}}
                }
            }
        )


async def print_human_agent_join_url(action: dict, flow_manager: FlowManager):
    """Print the URL for joining as a human agent."""
    logger.info(f"\n\nJOIN AS AGENT:\n{flow_manager.state['human_agent_join_url']}\n")


async def unmute_customer_and_make_humans_hear_each_other(action: dict, flow_manager: FlowManager):
    """Unmute the customer and make it so the customer and human agent can hear each other."""
    transport: DailyTransport = flow_manager.transport
    customer_participant_id = get_customer_participant_id(transport=transport)
    agent_participant_id = get_human_agent_participant_id(transport=transport)

    if customer_participant_id:
        await transport.update_remote_participants(
            remote_participants={
                customer_participant_id: {
                    "permissions": {
                        "canSend": ["microphone"],
                        "canReceive": {"byUserId": {"agent": True}},
                    },
                    "inputsEnabled": {"microphone": True},
                },
                agent_participant_id: {
                    "permissions": {"canReceive": {"byUserId": {"customer": True}}}
                },
            }
        )


# Functions
async def end_customer_conversation(
    args: FlowArgs, flow_manager: FlowManager
) -> tuple[None, NodeConfig]:
    """Transition to the "end_customer_conversation" node."""
    return None, create_end_customer_conversation_node()


async def end_human_agent_conversation(
    args: FlowArgs, flow_manager: FlowManager
) -> tuple[None, NodeConfig]:
    """Transition to the "end_human_agent_conversation" node."""
    return None, create_end_human_agent_conversation_node()


# Helpers
def next_node_after_customer_task(result: FlowResult) -> NodeConfig:
    """Transition to either the "continued_customer_interaction" node or "transferring_to_human_agent" node, depending on the outcome of the previous customer task"""
    if result.get("status") == "success":
        return create_continued_customer_interaction_node()
    else:
        return create_transferring_to_human_agent_node()


# Transitions
async def start_human_agent_interaction(flow_manager: FlowManager):
    """Transition to the "human_agent_interaction" node."""
    await flow_manager.set_node_from_config(create_human_agent_interaction_node())


# Node configuration
def create_initial_customer_interaction_node() -> NodeConfig:
    """Create the "initial_customer_interaction" node.
    This is the initial node where the bot interacts with the customer and tries to help with their requests.
    """
    return NodeConfig(
        name="customer_interaction",
        role_messages=[
            {
                "role": "system",
                "content": "You are an assistant for ABC Widget Company. You must ALWAYS use the available functions to progress the conversation. This is a phone conversation and your responses will be converted to audio. Keep the conversation friendly, casual, and polite. Avoid outputting special characters and emojis.",
            }
        ],
        task_messages=[
            {
                "role": "system",
                "content": """Start off by greeting the customer. Then ask how you could help, offering two choices of what you could help with: you could provide store location and hours of operation, or begin placing an order. Be friendly and casual. 
                
                To help the customer:
                - Use the check_store_location_and_hours_of_operation function to check store location and hours of operation to provide to the customer
                - Use the start_order function to begin placing an order on the customer's behalf

                If the customer wants to end the conversation, call the end_customer_conversation function.
                """,
            }
        ],
        functions=[
            FlowsFunctionSchema(
                name="check_store_location_and_hours_of_operation",
                description="Check store location and hours of operation",
                handler=check_store_location_and_hours_of_operation,
                properties={},
                required=[],
            ),
            FlowsFunctionSchema(
                name="start_order",
                description="Start placing an order",
                handler=start_order,
                properties={},
                required=[],
            ),
            FlowsFunctionSchema(
                name="end_customer_conversation",
                description="End the conversation",
                handler=end_customer_conversation,
                properties={},
                required=[],
            ),
        ],
    )


def create_continued_customer_interaction_node() -> NodeConfig:
    """Create the "continued_customer_interaction" node.
    This is a node where the bot interacts with the customer and tries to help with their requests.
    It assumes that the bot has already previously helped the customer with something.
    """
    return NodeConfig(
        name="continued_customer_interaction",
        task_messages=[
            {
                "role": "system",
                "content": """Ask the customer there's anything else you could help them with today, or if they'd like to end the conversation. If they need more help, re-offer the two choices you offered before: you could provide store location and hours of operation, or begin placing an order.
                
                To help the customer:
                - Use the check_store_location_and_hours_of_operation function to check store location and hours of operation to provide to the customer
                - Use the start_order function to begin placing an order on the customer's behalf

                If the customer wants to end the conversation, call the end_customer_conversation function.
                """,
            }
        ],
        functions=[
            FlowsFunctionSchema(
                name="check_store_location_and_hours_of_operation",
                description="Check store location and hours of operation",
                handler=check_store_location_and_hours_of_operation,
                properties={},
                required=[],
            ),
            FlowsFunctionSchema(
                name="start_order",
                description="Start placing an order",
                handler=start_order,
                properties={},
                required=[],
            ),
            FlowsFunctionSchema(
                name="end_customer_conversation",
                description="End the conversation",
                handler=end_customer_conversation,
                properties={},
                required=[],
            ),
        ],
    )


def create_transferring_to_human_agent_node() -> NodeConfig:
    """Create the "transferring_to_human_agent" node.
    This is the node where the customer is asked to please hold while the bot transfers them to a human agent. Hold music plays while the customer waits.
    """
    return NodeConfig(
        name="transferring_to_human_agent",
        task_messages=[
            {
                "role": "system",
                "content": "Start by apologizing to the customer that there was an issue fulfilling their last request, then inform them that they are being transferred to a human agent. Tell them to please hold while you connect them, and thank them for their patience.",
            }
        ],
        pre_actions=[
            ActionConfig(type="function", handler=mute_customer),
        ],
        post_actions=[
            ActionConfig(type="function", handler=start_hold_music),
            ActionConfig(type="function", handler=make_customer_hear_only_hold_music),
            ActionConfig(type="function", handler=print_human_agent_join_url),
        ],
    )


def create_human_agent_interaction_node() -> NodeConfig:
    """Create the "human_agent_interaction" node.
    This is the node where the bot fills in the human agent about what the customer was trying to accomplish that the bot was unable to help with, and what went wrong.
    The customer continues to hear hold music.
    """
    return NodeConfig(
        name="human_agent_interaction",
        task_messages=[
            {
                "role": "system",
                "content": """You're now talking to an agent who has just joined the call. Assume that the customer you were helping up until this point can no longer hear you. Your job is to be as helpful as you can and bring the agent up to speed so that they can assist the customer. Start by greeting the agent politely and explaining what the customer was trying to do that you were unable to help with, and any relevant error details. Ask the agent if they have any questions or whether they're ready to connect to the customer.
                
                Once the agent tells you they're ready to connect to the customer, call the connect_human_agent_and_customer function.
                """,
            }
        ],
        context_strategy=ContextStrategyConfig(
            strategy=ContextStrategy.RESET_WITH_SUMMARY,
            summary_prompt=(
                "Summarize the conversation with the customer, including what they were trying to accomplish and what, if anything, went wrong while trying to fulfill their requests. Include specific error details."
            ),
        ),
        functions=[
            FlowsFunctionSchema(
                name="connect_human_agent_and_customer",
                description="Connect the human agent to the customer",
                handler=end_human_agent_conversation,
                properties={},
                required=[],
            )
        ],
    )


def create_end_customer_conversation_node() -> NodeConfig:
    """Create the "end_customer_conversation" node.
    This is the node where the bot says goodbye to the customer and ends the conversation.
    This is how a conversation ends when a human agent did not need to be brought in.
    """
    return NodeConfig(
        name="end_customer_conversation",
        task_messages=[
            {
                "role": "system",
                "content": "Thank the customer warmly and mention they can call back anytime if they need more help.",
            }
        ],
        post_actions=[ActionConfig(type="end_conversation")],
    )


def create_end_human_agent_conversation_node() -> NodeConfig:
    """Create the "end_human_agent_conversation" node.
    This is the node where the bot tells the agent that they're being patched through to the customer and ends the conversation (leaving the customer and agent in the room talking to each other).
    """
    return NodeConfig(
        name="end_human_agent_conversation",
        task_messages=[
            {
                "role": "system",
                "content": "Tell the agent that you're patching them through to the customer right now.",
            },
        ],
        post_actions=[
            ActionConfig(type="function", handler=unmute_customer_and_make_humans_hear_each_other),
            ActionConfig(type="end_conversation"),
        ],
    )


# Helpers
def get_customer_participant_id(transport: DailyTransport) -> str:
    return next(
        (
            p["id"]
            for p in transport.participants().values()
            if not p["info"]["isLocal"] and p["info"].get("userId") == "customer"
        ),
        None,
    )


def get_human_agent_participant_id(transport: DailyTransport) -> str:
    return next(
        (
            p["id"]
            for p in transport.participants().values()
            if not p["info"]["isLocal"] and p["info"].get("userId") == "agent"
        ),
        None,
    )


async def get_customer_token(daily_rest_helper: DailyRESTHelper, room_url: str) -> str:
    """Gets a Daily token for the customer, configured with properties:
    {
        user_id: "customer",
        user_name: "Customer",
        permissions: {
            canReceive: {
                base: false,
                byUserId: {
                    bot: true
                }
            }
        }
    }
    """
    return await get_token(
        user_id="customer",
        permissions={
            "canReceive": {
                "base": False,
                "byUserId": {
                    "bot": True,
                },
            }
        },
        daily_rest_helper=daily_rest_helper,
        room_url=room_url,
        user_name="Customer",
    )


async def get_human_agent_token(daily_rest_helper: DailyRESTHelper, room_url: str) -> str:
    """Gets a Daily token for the human agent, configured with properties:
    {
        user_id: "agent",
        user_name: "Agent",
        permissions: {
            canReceive: {
                base: false,
                byUserId: {
                    bot: true
                }
            }
        }
    }
    """
    return await get_token(
        user_id="agent",
        permissions={
            "canReceive": {
                "base": False,
                "byUserId": {
                    "bot": True,
                },
            }
        },
        daily_rest_helper=daily_rest_helper,
        room_url=room_url,
        user_name="Agent",
    )


async def get_hold_music_player_token(daily_rest_helper: DailyRESTHelper, room_url: str) -> str:
    """Gets a Daily token for the hold music player, configured with properrties:
    {
        user_id: "hold-music",
        user_name: "Hold music"
    }
    """
    return await get_token(
        user_id="hold-music",
        permissions={},
        daily_rest_helper=daily_rest_helper,
        room_url=room_url,
        user_name="Hold music",
    )


async def get_token(
    user_id: str,
    permissions: dict,
    daily_rest_helper: DailyRESTHelper,
    room_url: str,
    user_name: str = None,
) -> str:
    return await daily_rest_helper.get_token(
        room_url=room_url,
        owner=False,
        params=DailyMeetingTokenParams(
            properties=DailyMeetingTokenProperties(
                user_id=user_id, user_name=user_name, permissions=permissions
            )
        ),
    )


async def main():
    """Main function to set up and run the bot."""
    async with aiohttp.ClientSession() as session:
        (room_url, token) = await configure(session)

        # Initialize services
        transport = DailyTransport(
            room_url=room_url,
            token=token,
            bot_name="ABC Widget Company Bot",
            params=DailyParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                vad_analyzer=SileroVADAnalyzer(),
            ),
        )
        stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
        tts = CartesiaHttpTTSService(
            api_key=os.getenv("CARTESIA_API_KEY"),
            voice_id="d46abd1d-2d02-43e8-819f-51fb652c1c61",  # Newsman
        )
        llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o")

        # Initialize context
        context = OpenAILLMContext()
        context_aggregator = llm.create_context_aggregator(context)

        # Create pipeline
        pipeline = Pipeline(
            [
                transport.input(),
                stt,
                context_aggregator.user(),
                llm,
                tts,
                transport.output(),
                context_aggregator.assistant(),
            ]
        )
        task = PipelineTask(pipeline=pipeline, params=PipelineParams(allow_interruptions=True))

        # Initialize flow manager
        flow_manager = FlowManager(
            task=task,
            llm=llm,
            context_aggregator=context_aggregator,
            transport=transport,
        )

        # Set up event handlers
        @transport.event_handler("on_first_participant_joined")
        async def on_first_participant_joined(
            transport: DailyTransport, participant: Dict[str, Any]
        ):
            """Start the flow.
            We're assuming the first participant is the customer and not the human agent.
            """
            await transport.capture_participant_transcription(participant["id"])
            # Initialize flow
            await flow_manager.initialize(create_initial_customer_interaction_node())

        @transport.event_handler("on_participant_joined")
        async def on_participant_joined(transport: DailyTransport, participant: Dict[str, Any]):
            """Handle the human agent maybe having joined the call:
            - If the participant who joined is the human agent and we're currently in the "transferring_to_human_agent" node, go to the "human_agent_interaction" node.
            - Otherwise...nothing, for the purposes of this demo. We're assuming the human agent won't join while the conversation flow is any other node.
            """
            user_id = participant.get("info", {}).get("userId")
            if user_id == "agent" and flow_manager.current_node == "transferring_to_human_agent":
                await start_human_agent_interaction(flow_manager=flow_manager)

        @transport.event_handler("on_participant_left")
        async def on_participant_left(
            transport: DailyTransport, participant: Dict[str, Any], reason: str
        ):
            # NOTE: an opportunity for refinement here is to handle the customer leaving while on
            # hold, informing the human agent if needed
            """If all human participants have left, stop the bot"""
            human_participants = {
                k: v
                for k, v in transport.participants().items()
                if v.get("info", {}).get("userId") in {"agent", "customer"}
            }
            if not human_participants:
                await task.cancel()

        # Print URL for joining as customer, and store URL for joining as human agent, to be printed later
        key = os.getenv("DAILY_API_KEY")
        daily_rest_helper = DailyRESTHelper(
            daily_api_key=key,
            daily_api_url=os.getenv("DAILY_API_URL", "https://api.daily.co/v1"),
            aiohttp_session=session,
        )
        customer_token = await get_customer_token(
            daily_rest_helper=daily_rest_helper, room_url=room_url
        )
        human_agent_token = await get_human_agent_token(
            daily_rest_helper=daily_rest_helper, room_url=room_url
        )
        logger.info(
            f"\n\nJOIN AS CUSTOMER:\n{room_url}{'?' if '?' not in room_url else '&'}t={customer_token}\n"
        )
        flow_manager.state["human_agent_join_url"] = (
            f"{room_url}{'?' if '?' not in room_url else '&'}t={human_agent_token}"
        )

        # Prepare hold music args
        flow_manager.state["hold_music_args"] = {
            "script_path": Path(__file__).parent.parent / "assets" / "hold_music" / "hold_music.py",
            "wav_file_path": Path(__file__).parent.parent
            / "assets"
            / "hold_music"
            / "hold_music.wav",
            "room_url": room_url,
            "token": await get_hold_music_player_token(
                daily_rest_helper=daily_rest_helper, room_url=room_url
            ),
        }

        # Clean up hold music process at exit, if needed
        def cleanup_hold_music_process():
            hold_music_process = flow_manager.state.get("hold_music_process")
            if hold_music_process:
                try:
                    hold_music_process.terminate()
                except:
                    # Exception if process already done; we don't care, it didn't hurt to try
                    pass

        atexit.register(cleanup_hold_music_process)

        # Run the pipeline
        runner = PipelineRunner()
        await runner.run(task)


if __name__ == "__main__":
    asyncio.run(main())
