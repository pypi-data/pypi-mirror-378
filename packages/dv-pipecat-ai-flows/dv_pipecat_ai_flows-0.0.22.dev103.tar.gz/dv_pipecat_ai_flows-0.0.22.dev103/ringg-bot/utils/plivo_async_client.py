"""
Async Plivo API client implementation using aiohttp.

This module provides an async alternative to the synchronous Plivo REST client,
designed to eliminate blocking operations that cause timeouts under high load.
"""

import asyncio
import base64
import json
from typing import Any, Dict, Optional

import aiohttp
from loguru import logger
from utils.http_client import (
    get_plivo_timeout,
    get_plivo_connector,
)


class AsyncPlivoAPIError(Exception):
    """Exception raised for Plivo API errors."""

    def __init__(
        self,
        status_code: int,
        message: str,
        error_code: Optional[str] = None,
        is_retryable: bool = True,
    ):
        self.status_code = status_code
        self.message = message
        self.error_code = error_code
        self.is_retryable = is_retryable
        super().__init__(f"Plivo API Error {status_code}: {message}")


class AsyncPlivoCallsAPI:
    """Async implementation of Plivo Calls API."""

    def __init__(self, auth_id: str, auth_token: str, session: aiohttp.ClientSession):
        self.auth_id = auth_id
        self.auth_token = auth_token
        self.session = session
        self.base_url = "https://api.plivo.com/v1/Account"

        # Create basic auth header
        credentials = f"{auth_id}:{auth_token}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
        }

    async def create(
        self,
        from_: str,
        to_: str,
        answer_url: str,
        hangup_url: str,
        ring_url: str,
        answer_method: str = "POST",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Create a new outbound call.

        Args:
            from_: The phone number to use as caller ID
            to_: The phone number to call
            answer_url: URL to fetch XML when call is answered
            hangup_url: URL to notify when call ends
            ring_url: URL to notify when phone starts ringing
            answer_method: HTTP method for answer_url (default: POST)
            **kwargs: Additional parameters for the API call

        Returns:
            Dict containing the API response

        Raises:
            AsyncPlivoAPIError: If the API call fails
        """
        url = f"{self.base_url}/{self.auth_id}/Call/"

        payload = {
            "from": from_,
            "to": to_,
            "answer_url": answer_url,
            "hangup_url": hangup_url,
            "ring_url": ring_url,
            "answer_method": answer_method,
            **kwargs,
        }

        try:
            async with self.session.post(url, json=payload, headers=self.headers) as response:
                response_text = await response.text()

                if response.status >= 400:
                    # Try to parse error from response
                    try:
                        error_data = json.loads(response_text)
                        error_message = error_data.get("message", "Unknown error")
                        error_code = error_data.get("error", None)
                    except json.JSONDecodeError:
                        error_message = response_text or f"HTTP {response.status}"
                        error_code = None

                    raise AsyncPlivoAPIError(
                        status_code=response.status, message=error_message, error_code=error_code
                    )

                # Parse successful response
                try:
                    return json.loads(response_text)
                except json.JSONDecodeError:
                    # If response isn't JSON, return raw text
                    return {"raw_response": response_text, "status": "success"}

        except aiohttp.ClientError as e:
            error_str = str(e).lower()
            # Check if this is a timeout during response reading (likely successful call)
            if "timeout" in error_str and "reading" in error_str:
                logger.warning(
                    f"Socket timeout during response reading - call may have succeeded: {e}"
                )
                # Non-retryable timeout as call likely succeeded on Plivo's end
                raise AsyncPlivoAPIError(
                    status_code=0,
                    message=f"Timeout reading response (call may have succeeded): {str(e)}",
                    error_code="RESPONSE_TIMEOUT",
                    is_retryable=False,
                )
            else:
                logger.error(f"HTTP client error in Plivo API call: {e}")
                raise AsyncPlivoAPIError(
                    status_code=0,
                    message=f"Connection error: {str(e)}",
                    error_code="CONNECTION_ERROR",
                )
        except asyncio.TimeoutError:
            logger.warning("Request timeout - call may have succeeded on Plivo's end")
            # Non-retryable timeout as call likely succeeded on Plivo's end
            raise AsyncPlivoAPIError(
                status_code=0,
                message="Request timeout (call may have succeeded)",
                error_code="TIMEOUT",
                is_retryable=False,
            )


class AsyncPlivoClient:
    """
    Async Plivo REST client with connection pooling and timeout management.

    This client is designed to replace the synchronous plivo.RestClient()
    while maintaining the same API interface.
    """

    def __init__(
        self, auth_id: str, auth_token: str, session: Optional[aiohttp.ClientSession] = None
    ):
        self.auth_id = auth_id
        self.auth_token = auth_token
        self._session = session
        self._owned_session = session is None
        self.calls = None

    async def __aenter__(self):
        """Async context manager entry."""
        if self._session is None:
            # Create session with optimized settings for Plivo API
            self._session = aiohttp.ClientSession(
                timeout=get_plivo_timeout(),
                connector=get_plivo_connector(),
                raise_for_status=False,  # We'll handle status codes ourselves
            )

        self.calls = AsyncPlivoCallsAPI(self.auth_id, self.auth_token, self._session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._owned_session and self._session:
            await self._session.close()

    def get_calls_api(self, session: aiohttp.ClientSession) -> AsyncPlivoCallsAPI:
        """Get the calls API instance with the provided session."""
        return AsyncPlivoCallsAPI(self.auth_id, self.auth_token, session)


# Global session management for connection pooling across requests
_global_plivo_session: Optional[aiohttp.ClientSession] = None
_session_lock = asyncio.Lock()


async def get_shared_plivo_session() -> aiohttp.ClientSession:
    """
    Get a shared aiohttp session for Plivo API calls.

    This ensures connection pooling across multiple API calls,
    significantly improving performance under high load.

    Returns:
        Shared aiohttp ClientSession instance
    """
    global _global_plivo_session

    async with _session_lock:
        if _global_plivo_session is None or _global_plivo_session.closed:
            _global_plivo_session = aiohttp.ClientSession(
                timeout=get_plivo_timeout(),
                connector=get_plivo_connector(),
                raise_for_status=False,  # We'll handle status codes ourselves
            )

    return _global_plivo_session


async def cleanup_plivo_session():
    """Clean up the global Plivo session. Should be called on app shutdown."""
    global _global_plivo_session

    async with _session_lock:
        if _global_plivo_session and not _global_plivo_session.closed:
            await _global_plivo_session.close()
            _global_plivo_session = None


async def create_plivo_call(
    auth_id: str,
    auth_token: str,
    from_: str,
    to_: str,
    answer_url: str,
    hangup_url: str,
    ring_url: str,
    answer_method: str = "POST",
    **kwargs,
) -> Dict[str, Any]:
    """
    Convenience function to create a Plivo call using the shared session.

    This function provides a drop-in replacement for the synchronous
    plivo_client.calls.create() call pattern used in the existing code.

    Args:
        auth_id: Plivo Auth ID
        auth_token: Plivo Auth Token
        from_: The phone number to use as caller ID
        to_: The phone number to call
        answer_url: URL to fetch XML when call is answered
        hangup_url: URL to notify when call ends
        ring_url: URL to notify when phone starts ringing
        answer_method: HTTP method for answer_url (default: POST)
        **kwargs: Additional parameters for the API call

    Returns:
        Dict containing the API response

    Raises:
        AsyncPlivoAPIError: If the API call fails
    """
    session = await get_shared_plivo_session()
    calls_api = AsyncPlivoCallsAPI(auth_id, auth_token, session)

    return await calls_api.create(
        from_=from_,
        to_=to_,
        answer_url=answer_url,
        hangup_url=hangup_url,
        ring_url=ring_url,
        answer_method=answer_method,
        **kwargs,
    )
