"""
Async Twilio client wrapper using official AsyncTwilioHttpClient.

This module provides an async wrapper for Twilio API calls using the official
Twilio Python library's built-in async support, designed to eliminate blocking
operations that cause timeouts under high load.
"""

import asyncio
from typing import Any, Dict, List, Optional

from loguru import logger
from twilio.base.exceptions import TwilioRestException
from twilio.http.async_http_client import AsyncTwilioHttpClient
from twilio.rest import Client


class AsyncTwilioAPIError(Exception):
    """Exception raised for Twilio API errors."""

    def __init__(self, status_code: int, message: str, error_code: Optional[str] = None):
        self.status_code = status_code
        self.message = message
        self.error_code = error_code
        super().__init__(f"Twilio API Error {status_code}: {message}")


class AsyncTwilioCallsManager:
    """
    Async wrapper for Twilio calls API using the official AsyncTwilioHttpClient.

    This class provides async call creation functionality while maintaining
    compatibility with the existing codebase structure.
    """

    def __init__(
        self, account_sid: str, auth_token: str, http_client: Optional[AsyncTwilioHttpClient] = None
    ):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.http_client = http_client or AsyncTwilioHttpClient()
        self.client = Client(account_sid, auth_token, http_client=self.http_client)

    async def create_call(
        self,
        from_: str,
        to: str,
        url: str,
        record: bool = False,
        status_callback: Optional[str] = None,
        status_callback_event: Optional[List[str]] = None,
        status_callback_method: str = "POST",
        time_limit: int = 240,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Create a new outbound call using Twilio's async API.

        Args:
            from_: The phone number to use as caller ID
            to: The phone number to call
            url: URL to fetch TwiML when call is answered
            record: Whether to record the call (default: False)
            status_callback: URL for status callback notifications
            status_callback_event: List of events to notify about
            status_callback_method: HTTP method for status callback
            time_limit: Maximum call duration in seconds
            **kwargs: Additional parameters for the API call

        Returns:
            Dict containing the call details

        Raises:
            AsyncTwilioAPIError: If the API call fails
        """
        try:
            # Use the official async method from Twilio library
            call = await self.client.calls.create_async(
                from_=from_,
                to=to,
                url=url,
                record=record,
                status_callback=status_callback,
                status_callback_event=status_callback_event or [],
                status_callback_method=status_callback_method,
                time_limit=time_limit,
                **kwargs,
            )

            # Convert call object to dict for consistent return format
            return {
                "sid": call.sid,
                "account_sid": call.account_sid,
                "from_": call.from_formatted,
                "to": call.to,
                "status": call.status,
                "start_time": call.start_time,
                "end_time": call.end_time,
                "duration": call.duration,
                "price": call.price,
                "direction": call.direction,
                "answered_by": call.answered_by,
                "forwarded_from": call.forwarded_from,
                "group_sid": call.group_sid,
                "caller_name": call.caller_name,
                "uri": call.uri,
            }

        except TwilioRestException as e:
            logger.error(f"Twilio REST API error: {e}")
            raise AsyncTwilioAPIError(status_code=e.status, message=e.msg, error_code=str(e.code))
        except Exception as e:
            logger.error(f"Unexpected error in Twilio API call: {e}")
            raise AsyncTwilioAPIError(
                status_code=0, message=f"Unexpected error: {str(e)}", error_code="UNEXPECTED_ERROR"
            )


class AsyncTwilioClient:
    """
    Async Twilio client with connection management and error handling.

    This client wraps the official Twilio AsyncTwilioHttpClient while providing
    enhanced error handling and connection management.
    """

    def __init__(
        self, account_sid: str, auth_token: str, http_client: Optional[AsyncTwilioHttpClient] = None
    ):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.http_client = http_client
        self.calls_manager = None

    async def __aenter__(self):
        """Async context manager entry."""
        if self.http_client is None:
            self.http_client = AsyncTwilioHttpClient()

        self.calls_manager = AsyncTwilioCallsManager(
            self.account_sid, self.auth_token, self.http_client
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        # The AsyncTwilioHttpClient handles its own cleanup
        pass

    def get_calls_manager(self) -> AsyncTwilioCallsManager:
        """Get the calls manager instance."""
        if self.calls_manager is None:
            raise RuntimeError("Client not initialized. Use async context manager.")
        return self.calls_manager


# Global HTTP client management for connection reuse
_global_twilio_http_client: Optional[AsyncTwilioHttpClient] = None
_client_lock = asyncio.Lock()


async def get_shared_twilio_http_client() -> AsyncTwilioHttpClient:
    """
    Get a shared AsyncTwilioHttpClient instance for connection reuse.

    The official Twilio AsyncTwilioHttpClient handles connection pooling
    internally, so we can safely share a single instance.

    Returns:
        Shared AsyncTwilioHttpClient instance
    """
    global _global_twilio_http_client

    async with _client_lock:
        if _global_twilio_http_client is None:
            _global_twilio_http_client = AsyncTwilioHttpClient()
            logger.debug("Created shared Twilio AsyncTwilioHttpClient")

    return _global_twilio_http_client


async def cleanup_twilio_client():
    """Clean up the global Twilio HTTP client. Should be called on app shutdown."""
    global _global_twilio_http_client

    async with _client_lock:
        if _global_twilio_http_client is not None:
            # The AsyncTwilioHttpClient handles its own cleanup
            _global_twilio_http_client = None
            logger.debug("Cleaned up shared Twilio AsyncTwilioHttpClient")


async def create_twilio_call(
    account_sid: str,
    auth_token: str,
    from_: str,
    to: str,
    url: str,
    record: bool = False,
    status_callback: Optional[str] = None,
    status_callback_event: Optional[List[str]] = None,
    status_callback_method: str = "POST",
    time_limit: int = 240,
    **kwargs,
) -> Dict[str, Any]:
    """
    Convenience function to create a Twilio call using the shared HTTP client.

    This function provides a drop-in replacement for the synchronous
    twilio_client.calls.create() call pattern used in the existing code.

    Args:
        account_sid: Twilio Account SID
        auth_token: Twilio Auth Token
        from_: The phone number to use as caller ID
        to: The phone number to call
        url: URL to fetch TwiML when call is answered
        record: Whether to record the call (default: False)
        status_callback: URL for status callback notifications
        status_callback_event: List of events to notify about
        status_callback_method: HTTP method for status callback
        time_limit: Maximum call duration in seconds
        **kwargs: Additional parameters for the API call

    Returns:
        Dict containing the call details

    Raises:
        AsyncTwilioAPIError: If the API call fails
    """
    http_client = await get_shared_twilio_http_client()
    calls_manager = AsyncTwilioCallsManager(account_sid, auth_token, http_client)

    return await calls_manager.create_call(
        from_=from_,
        to=to,
        url=url,
        record=record,
        status_callback=status_callback,
        status_callback_event=status_callback_event,
        status_callback_method=status_callback_method,
        time_limit=time_limit,
        **kwargs,
    )
