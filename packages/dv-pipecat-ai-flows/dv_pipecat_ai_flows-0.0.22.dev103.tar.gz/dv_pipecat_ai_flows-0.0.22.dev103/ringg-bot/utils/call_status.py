"""Call status update utilities."""

import json

import aiohttp
from env_config import api_config
from loguru import logger
from utils.http_client import create_http_client_session


async def update_call_status(
    call_id: str, status: str, call_provider: str, error_message: str = None
):
    """Helper function to update call status in backend."""
    if not call_id:
        logger.warning("Cannot update call status: call_id is None")
        return

    try:
        status_url = f"{api_config.CALLING_BACKEND_URL}/calling/inbound/status"
        payload = {
            "call_sid": call_id,
            "status": status,
            "call_provider": call_provider,
        }

        print(f"payload {payload}")

        if error_message:
            logger.error(f"Error {error_message} for {call_provider}", call_id=call_id)

        async with create_http_client_session() as session:
            async with session.patch(status_url, json=payload) as response:
                logger.info(
                    f"{call_provider} status update ({status}): {response.status}",
                    call_id=call_id,
                )
                if response.status == 200:
                    logger.info(f"response.status {response.status}")
                    logger.info(f"{call_provider} status updated successfully", call_id=call_id)
                else:
                    response_text = await response.text()
                    logger.warning(
                        f"{call_provider} status update failed: {response_text}", call_id=call_id
                    )
    except Exception as e:
        logger.error(f"Failed to update {call_provider} status: {e}", call_id=call_id)
