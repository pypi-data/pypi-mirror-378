import asyncio  # noqa: D100
import base64
import json
from datetime import datetime, timezone
from typing import Any, Optional

import aiohttp
from env_config import api_config
from fastapi import HTTPException
from starlette.websockets import WebSocket, WebSocketState

from pipecat.frames.frames import (
    CancelFrame,
    TTSSpeakFrame,
)
from pipecat.pipeline.task import PipelineTask
from pipecat.processors.frame_processor import FrameDirection
from pipecat.transports.network.fastapi_websocket import FastAPIWebsocketTransport

from ..api_calls import update_webcall_status
from ..generic_functions.cleanup import cleanup_connection
from ..plivo_utils import create_plivo_basic_auth_header  # Import the utility function


async def end_call(
    provider,
    call_id,
    stream_id,
    websocket: WebSocket,
    callback_call_id,
    context_aggregator,
    transcript_handler,
    task,
    task_references,
    function_call_monitor,
    logger,
    transport: Optional[FastAPIWebsocketTransport] = None,
    record_locally=False,
    webcall_params=None,
):
    try:
        if provider == "plivo":
            # Construct the specific URL for ending the stream
            auth_id = api_config.PLIVO_AUTH_ID
            plivo_url = "https://api.plivo.com/v1/Account/{}/Call/{}/Stream/{}/".format(
                auth_id, call_id, stream_id
            )

            # Get headers from the utility function
            headers = create_plivo_basic_auth_header()
            async with aiohttp.ClientSession() as session:
                logger.debug(
                    "Making DELETE call to Plivo URL to end stream: {}".format(plivo_url),
                    call_id=callback_call_id,
                )

                async with session.delete(plivo_url, headers=headers) as response:
                    # Plivo returns 204 No Content on successful stream deletion
                    if response.status == 204:
                        logger.info(
                            "Successfully informed Plivo to end the call.", call_id=callback_call_id
                        )
                        return True
                    elif response.status == 404:
                        logger.info(
                            "Plivo call already ended (404 received).", call_id=callback_call_id
                        )
                        return True
                    else:
                        logger.warning(
                            "Failed to end the call with Plivo. Status: {}".format(response.status),
                            call_id=callback_call_id,
                        )
                        return False
        elif provider == "exotel":
            if websocket.client_state != WebSocketState.DISCONNECTED:
                # await task.cancel()
                await transport.input().cancel(CancelFrame())
                await transport.output().cancel(CancelFrame())
                # await websocket.close()
                # await cleanup_connection(
                #     callback_call_id,
                #     context_aggregator,
                #     transcript_handler,
                #     task,
                #     task_references,
                #     function_call_monitor,
                #     logger,
                #     record_locally,
                # )
            return True
        elif provider == "twilio":
            if websocket.client_state != WebSocketState.DISCONNECTED:
                await transport.input().cancel(CancelFrame())
                await transport.output().process_frame(CancelFrame(), FrameDirection.DOWNSTREAM)
            return True
        elif provider in ["custom", "asterisk"]:
            if websocket.client_state != WebSocketState.DISCONNECTED:
                # await task.cancel()
                await transport.input().cancel(CancelFrame())
                await transport.output().process_frame(CancelFrame(), FrameDirection.DOWNSTREAM)
                # await cleanup_connection(
                #     callback_call_id,
                #     context_aggregator,
                #     transcript_handler,
                #     task,
                #     task_references,
                #     function_call_monitor,
                #     logger,
                #     record_locally,
                # )
            return True
        elif provider == "convox":
            if websocket.client_state != WebSocketState.DISCONNECTED:
                # Send callEnd event to ConVox before closing the connection
                try:
                    call_end_event = {
                        "event": "callEnd",
                        "details": {
                            "timestamp": datetime.now(timezone.utc)
                            .isoformat()
                            .replace("+00:00", "Z"),
                            "direction": "WSS",
                            "message": "Event trigger request",
                        },
                    }
                    await websocket.send_json(call_end_event)
                    logger.info(
                        "Sent callEnd event to ConVox",
                        call_id=callback_call_id,
                        extra={"event": call_end_event},
                    )
                except Exception as send_error:
                    logger.warning(
                        f"Failed to send callEnd event to ConVox: {send_error}",
                        call_id=callback_call_id,
                    )

                await transport.input().cancel(CancelFrame())
                await transport.output().process_frame(CancelFrame(), FrameDirection.DOWNSTREAM)

                logger.info(
                    "callEnd event sent to ConVox, connection will be closed by ConVox",
                    call_id=callback_call_id,
                )

            else:
                logger.info(
                    "WebSocket already disconnected for convox provider", call_id=callback_call_id
                )
            return True
        elif provider == "daily":
            # make a call to calling backend with status as completed
            await update_webcall_status(
                call_id=call_id,
                callback_call_id=callback_call_id,
                status="completed",
                sub_status="completed",
                logger=logger,
            )
            # await transport.cleanup()
            await cleanup_connection(
                callback_call_id,
                call_id,
                context_aggregator,
                transcript_handler,
                task,
                task_references,
                function_call_monitor,
                logger,
                record_locally,
                telephony_provider=provider,
                webcall_params=webcall_params,
            )
            logger.info(
                "successfully closed the daily webrtc connection!", call_id=callback_call_id
            )

    except Exception as e:
        print(e)
        logger.exception("End call failed", call_id=callback_call_id)
        return False


async def end_call_function(
    function_name,
    tool_call_id,
    args,
    llm,
    telephony_provider,
    call_id,
    stream_id,
    websocket_client,
    callback_call_id,
    context_aggregator,
    transcript_handler,
    task: PipelineTask,
    task_references,
    bot_speaking_frame_monitor,
    final_message_done_event,
    function_call_monitor,
    logger,
    transport: Optional[FastAPIWebsocketTransport] = None,
    webcall_params=None,
):
    logger.debug("End call function called")
    function_call_monitor.append("end_call_called")
    final_message = args["final_message"]
    await llm.push_frame(TTSSpeakFrame(final_message))

    # Set flag to monitor inactivity and start monitoring task
    bot_speaking_frame_monitor.waiting_for_final_message = True
    bot_speaking_frame_monitor.last_frame_time = None

    async def wait_for_bot_speaking_inactivity():
        try:
            while True:
                await asyncio.sleep(0.2)
                if bot_speaking_frame_monitor.last_frame_time is None:
                    continue
                elapsed = (
                    asyncio.get_event_loop().time() - bot_speaking_frame_monitor.last_frame_time
                )
                if elapsed >= 0.5:
                    break
            final_message_done_event.set()
        except asyncio.CancelledError:
            final_message_done_event.set()
            raise

    inactivity_task = asyncio.create_task(wait_for_bot_speaking_inactivity())
    task_references.append(inactivity_task)
    logger.debug("Waiting for final message audio to finish...")
    await final_message_done_event.wait()
    logger.debug("Final message audio has been sent.")

    bot_speaking_frame_monitor.waiting_for_final_message = False

    success = await end_call(
        telephony_provider,
        call_id,
        stream_id,
        websocket_client,
        callback_call_id,
        context_aggregator,
        transcript_handler,
        task,
        task_references,
        function_call_monitor,
        logger,
        transport,
        record_locally=False,
        webcall_params=webcall_params,
    )
    return success
