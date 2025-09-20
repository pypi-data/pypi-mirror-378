#
# Copyright (c) 2024, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""Action management system for conversation flows.

This module provides the ActionManager class which handles execution of actions
during conversation state transitions. It supports:

- Built-in actions (TTS, conversation ending)
- Custom action registration
- Synchronous and asynchronous handlers
- Pre and post-transition actions
- Error handling and validation

Actions are used to perform side effects during conversations, such as:

- Text-to-speech output
- Database updates
- External API calls
- Custom integrations
"""

import asyncio
import inspect
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Dict, List, Optional

from loguru import logger
from pipecat.frames.frames import (
    BotStoppedSpeakingFrame,
    ControlFrame,
    EndFrame,
    LLMMessagesAppendFrame,
    TTSSpeakFrame,
)
from pipecat.pipeline.task import PipelineTask

from pipecat_flows.exceptions import ActionError
from pipecat_flows.types import ActionConfig, FlowActionHandler

if TYPE_CHECKING:
    from pipecat_flows.manager import FlowManager


@dataclass
class FunctionActionFrame(ControlFrame):
    """Frame containing a function action to be executed.

    Parameters:
        action: Action configuration dictionary.
        function: Function handler to execute.
    """

    action: dict
    function: FlowActionHandler


@dataclass
class ActionFinishedFrame(ControlFrame):
    """Frame indicating that an action has completed execution."""

    pass


class ActionManager:
    """Manages the registration and execution of flow actions.

    Actions are executed during state transitions and can include:

    - Text-to-speech output
    - Database updates
    - External API calls
    - Custom user-defined actions

    Built-in actions:

    - tts_say: Speak text using TTS
    - end_conversation: End the current conversation
    - function: Execute inline functions in the pipeline

    Custom actions can be registered using register_action().
    """

    def __init__(self, task: PipelineTask, flow_manager: "FlowManager"):
        """Initialize the action manager.

        Args:
            task: PipelineTask instance used to queue frames.
            flow_manager: FlowManager instance that this ActionManager is part of.
        """
        self._action_handlers: Dict[str, Callable] = {}
        self._task = task
        self._flow_manager = flow_manager
        self._ongoing_actions_count = 0
        self._ongoing_actions_finished_event = asyncio.Event()
        self._deferred_post_actions: List[ActionConfig] = []

        # Register built-in actions
        self._register_action("tts_say", self._handle_tts_action)
        self._register_action("end_conversation", self._handle_end_action)
        self._register_action("function", self._handle_function_action)

        # Add pipeline observation
        task.set_reached_downstream_filter(
            (ActionFinishedFrame, FunctionActionFrame, BotStoppedSpeakingFrame)
        )

        @task.event_handler("on_frame_reached_downstream")
        async def on_frame_reached_downstream(task, frame):
            if isinstance(frame, FunctionActionFrame):
                # Run function action
                await frame.function(frame.action, flow_manager)
                self._decrement_ongoing_actions_count()
            elif isinstance(frame, BotStoppedSpeakingFrame):
                # Execute deferred post-actions if the bot's turn is over.
                # A BotStoppedSpeakingFrame only indicates that the bot's turn is over if there are
                # no ongoing actions (otherwise one of those actions may have been responsible for it).
                if self._ongoing_actions_count == 0:
                    await self._execute_deferred_post_actions()
            elif isinstance(frame, ActionFinishedFrame):
                # Handle action finished
                self._decrement_ongoing_actions_count()

    def _register_action(self, action_type: str, handler: Callable) -> None:
        """Register a handler for a specific action type.

        Args:
            action_type: String identifier for the action (e.g., "tts_say").
            handler: Async or sync function that handles the action.

        Raises:
            ValueError: If handler is not callable.
        """
        if not callable(handler):
            raise ValueError("Action handler must be callable")
        self._action_handlers[action_type] = handler
        logger.debug(f"Registered handler for action type: {action_type}")

    async def execute_actions(self, actions: Optional[List[ActionConfig]]) -> None:
        """Execute a list of actions.

        Args:
            actions: List of action configurations to execute.

        Raises:
            ActionError: If action execution fails.

        Note:
            Each action must have a 'type' field matching a registered handler.
        """
        if not actions:
            return

        previous_action_type = None
        for action in actions:
            action_type = action.get("type")
            if not action_type:
                raise ActionError("Action missing required 'type' field")

            handler = self._action_handlers.get(action_type)
            if not handler:
                raise ActionError(f"No handler registered for action type: {action_type}")

            ongoing_actions_count = self._ongoing_actions_count
            try:
                # Based on the type of the previous action and the one coming up, we can determine
                # if we need to wait for ongoing actions to finish before proceeding with this next
                # one
                await self._maybe_wait_for_ongoing_actions_to_finish(
                    previous_action_type, action_type
                )

                # Determine if handler can accept flow_manager argument by inspecting its signature
                # Handlers can either take (action) or (action, flow_manager)
                try:
                    handler_positional_arg_count = handler.__code__.co_argcount
                    if inspect.ismethod(handler) and handler_positional_arg_count > 0:
                        # adjust for `self` being the first arg
                        handler_positional_arg_count -= 1
                    can_handle_flow_manager_arg = (
                        handler_positional_arg_count > 1 or handler.__code__.co_flags & 0x04
                    )
                except AttributeError:
                    logger.warning(
                        f"Unable to determine handler signature for action type '{action_type}', "
                        "falling back to legacy single-parameter call"
                    )
                    can_handle_flow_manager_arg = False

                # Invoke handler appropriately, with async and flow_manager arg as needed
                if can_handle_flow_manager_arg:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(action, self._flow_manager)
                    else:
                        handler(action, self._flow_manager)
                else:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(action)
                    else:
                        handler(action)

                # Record the type of the action we just executed
                previous_action_type = action_type
                logger.debug(f"Successfully executed action: {action_type}")

                # If action was end_conversation, break
                # (If we didn't, we could end up waiting for the next actions to finish, and...they
                # never would)
                if action_type == "end_conversation":
                    break
            except Exception as e:
                # Undo any increment of ongoing actions count that happened during this action
                if self._ongoing_actions_count > ongoing_actions_count:
                    self._decrement_ongoing_actions_count()  # Assumption: on increment per action
                raise ActionError(f"Failed to execute action {action_type}: {str(e)}") from e

        # Based on the type of the last action, we may need to wait for ongoing actions to finish
        # before considering this set of actions complete.
        await self._maybe_wait_for_ongoing_actions_to_finish(previous_action_type, None)

    def schedule_deferred_post_actions(self, post_actions: List[ActionConfig]) -> None:
        """Schedule "deferred" post-actions to be executed after next LLM completion.

        Args:
            post_actions: List of actions to execute after LLM response.
        """
        self._deferred_post_actions = post_actions

    def clear_deferred_post_actions(self) -> None:
        """Clear any scheduled deferred post-actions."""
        self._deferred_post_actions = []

    async def _execute_deferred_post_actions(self) -> None:
        """Execute deferred post-actions."""
        actions = self._deferred_post_actions
        self._deferred_post_actions = []
        if actions:
            await self.execute_actions(actions)

    async def _maybe_wait_for_ongoing_actions_to_finish(
        self, previous_action_type: str, upcoming_action_type: Optional[str]
    ) -> None:
        """Wait for ongoing actions to finish before executing the next action if needed.

        This method determines whether to wait based on the types of the previous
        and upcoming actions to avoid the upcoming action having an effect before
        the previous one is done.

        Args:
            previous_action_type: Type of the previously executed action.
            upcoming_action_type: Type of the next action to execute, or None if
                this is the end of the action sequence.
        """
        needs_wait = False
        if previous_action_type == "tts_say":
            # "tts_say" enqueues a TTSSpeakFrame, which has an effect when it hits the TTS node in
            # the pipeline.
            # As long as the upcoming action enqueues a frame with an effect at the same point or
            # later in the pipeline, we don't need to wait.
            # If the upcoming action is:
            # - "tts_say": no need to wait (effect happens at the same point)
            # - "end_conversation": no need to wait (effect happens at the end of the pipeline)
            # - "function": no need to wait (effect happens at the end of the pipeline)
            #  - None: wait (we're done with this set of actions; the next thing to occur may be a
            #    node change/LLM context update, which has an effect earlier in the pipeline)
            # - custom action: wait (we don't know what it will do)
            if upcoming_action_type not in ["tts_say", "end_conversation", "function"]:
                needs_wait = True  # None or custom action
        elif previous_action_type == "function":
            # "function" enqueues a FunctionActionFrame, which has an effect at the end of the
            # pipeline.
            # Functions can take some time to execute (and don't hold up the pipeline as they're
            # doing so), so we need to wait for them to finish before proceeding with the next
            # action or moving on from the current set of actions.
            needs_wait = True
        else:
            # Either previous action was:
            # - None (the upcoming action is the first one), so there's nothing to wait for.
            # - A fully custom action, where we don't wait, like we've always done. Note that we
            #   could, in the future, add new API affordances for users to tell us to wait for the
            #   the action to finish before moving on to the next one along with a way for them to
            #   tell us when the action is done. But let's hold off on doing that since we're
            #   de-emphasizing custom actions in favor of "function" actions, which should meet most
            #   needs.
            # Note that it should not be possible for the previous action to be "end_conversation",
            # since we stop processing actions after that one.
            pass

        if needs_wait:
            await self._ongoing_actions_finished_event.wait()

    async def _handle_tts_action(self, action: dict) -> None:
        """Built-in handler for TTS actions.

        Args:
            action: Action configuration containing:
                - text: Text to speak (required)
                - use_cache: Use caching for TTS audio (optional, default: False)
                - mirror_context: Mirror TTS content to LLM context (optional, default: False)
                
        Note: Caching functionality must be provided via dependency injection through
        flow_manager.state['say_with_cache_handler'] if use_cache=True.
        """
        text = action.get("text")
        if not text:
            logger.error("TTS action missing 'text' field")
            return

        use_cache = action.get("use_cache", False)
        mirror_context = action.get("mirror_context", False)

        try:
            # For now, always use the standard TTS path to avoid pipeline issues
            # Caching can be implemented at the TTS service level instead
            
            # Mark that we're starting the action
            self._increment_ongoing_actions_count()

            # Queue the TTS frame
            await self._task.queue_frame(TTSSpeakFrame(text=text))

            # Queue frame marking the end of the action
            await self._task.queue_frame(ActionFinishedFrame())

            # Mirror content to LLM context if requested
            if mirror_context:
                try:
                    # Add the assistant message (what was said via TTS)
                    assistant_message = {"role": "assistant", "content": text}
                    # Add a system instruction to prevent duplicate greeting
                    system_instruction = {
                        "role": "system", 
                        "content": "The above greeting has already been spoken. Do not greet the user again. Continue the conversation naturally from where it left off."
                    }
                    await self._task.queue_frame(
                        LLMMessagesAppendFrame(messages=[assistant_message, system_instruction])
                    )
                    logger.debug(f"Mirrored TTS content to LLM context with anti-greeting instruction: {text[:50]}...")
                except Exception as e:
                    logger.error(f"Failed to mirror TTS content to LLM context: {e}")

        except Exception as e:
            self._decrement_ongoing_actions_count()
            logger.error(f"TTS error: {e}")

    async def _handle_end_action(self, action: dict) -> None:
        """Built-in handler for ending the conversation.

        This handler queues an EndFrame to terminate the conversation. If the action
        includes a 'text' key, it will queue that text to be spoken before ending.

        Args:
            action: Action configuration dictionary. Optional 'text' key for a
                goodbye message.
        """
        # Mark that we're starting the action
        self._increment_ongoing_actions_count()

        # Queue the action frames
        if action.get("text"):  # Optional goodbye message
            await self._task.queue_frame(TTSSpeakFrame(text=action["text"]))
        await self._task.queue_frame(EndFrame())

        # NOTE: there's no point queueing an ActionFinishedFrame here, since the previously-queued
        # EndFrame ensures that it'll never get delivered to our observer

    async def _handle_function_action(self, action: dict) -> None:
        """Built-in handler for queuing functions to run inline in the pipeline.

        This handler queues a FunctionActionFrame to be executed when the pipeline
        is done with all the work queued before it. It expects a 'handler' key in
        the action containing the function to execute.

        Args:
            action: Action configuration dictionary. Required 'handler' key
                containing the function to execute.
        """
        handler = action.get("handler")
        if not handler:
            logger.error("Function action missing 'handler' field")
            return

        # Mark that we're starting the action
        self._increment_ongoing_actions_count()

        # Queue the action frame (we're queueing rather than running it here to ensure it happens
        # at the appropriate time in the pipeline, like when the bot's turn is over, for example).
        await self._task.queue_frame(FunctionActionFrame(action=action, function=handler))

        # NOTE: we do NOT queue an ActionFinishedFrame here; instead, we will decrement the ongoing
        # actions count when the function has finished executing (the function may take some time)

    def _increment_ongoing_actions_count(self) -> None:
        """Increment the count of ongoing actions and reset the finished event if this is the first action."""
        self._ongoing_actions_count += 1
        if self._ongoing_actions_count == 1:
            self._ongoing_actions_finished_event.clear()

    def _decrement_ongoing_actions_count(self) -> None:
        """Decrement the count of ongoing actions and set the finished event if this was the last action."""
        self._ongoing_actions_count = max(0, self._ongoing_actions_count - 1)
        if self._ongoing_actions_count == 0:
            self._ongoing_actions_finished_event.set()
