"""
Rate limiting utilities for API calls.

This module provides rate limiting functionality to ensure compliance with
API provider limits (e.g., Plivo's 2 CPS outbound call limit).
"""

import asyncio
import time
from collections import deque
from typing import Any, Dict, Optional

from env_config import api_config
from loguru import logger


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter implementation.

    This implementation allows for burst capacity while maintaining
    the average rate over time. It's ideal for API rate limiting
    where occasional bursts are acceptable but sustained high rates
    need to be controlled.
    """

    def __init__(self, rate: float, burst_capacity: Optional[int] = None):
        """
        Initialize the token bucket rate limiter.

        Args:
            rate: Maximum rate in requests per second
            burst_capacity: Maximum number of requests that can be made instantly.
                          If None, defaults to rate (allowing 1 second of burst)
        """
        self.rate = rate
        self.burst_capacity = burst_capacity or int(rate) or 1
        self.tokens = self.burst_capacity
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: int = 1) -> bool:
        """
        Acquire tokens from the bucket.

        Args:
            tokens: Number of tokens to acquire (default: 1)

        Returns:
            True if tokens were successfully acquired, False otherwise
        """
        async with self._lock:
            now = time.monotonic()

            # Refill tokens based on elapsed time
            elapsed = now - self.last_refill
            tokens_to_add = elapsed * self.rate
            self.tokens = min(self.burst_capacity, self.tokens + tokens_to_add)
            self.last_refill = now

            # Check if we have enough tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True

            return False

    async def wait_for_token(self, tokens: int = 1) -> None:
        """
        Wait until tokens are available and acquire them.

        Args:
            tokens: Number of tokens to acquire (default: 1)
        """
        while True:
            if await self.acquire(tokens):
                return

            # Calculate how long to wait for next token
            async with self._lock:
                wait_time = tokens / self.rate

            logger.debug(f"Rate limit reached, waiting {wait_time:.2f} seconds")
            await asyncio.sleep(min(wait_time, 0.1))  # Cap wait time at 100ms intervals


class SlidingWindowRateLimiter:
    """
    Sliding window rate limiter implementation.

    This implementation tracks requests in a sliding time window,
    providing more accurate rate limiting but with higher memory usage.
    """

    def __init__(self, rate: float, window_seconds: float = 1.0):
        """
        Initialize the sliding window rate limiter.

        Args:
            rate: Maximum rate in requests per second
            window_seconds: Size of the sliding window in seconds
        """
        self.rate = rate
        self.window_seconds = window_seconds
        self.max_requests = int(rate * window_seconds)
        self.requests: deque = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> bool:
        """
        Try to acquire permission for a request.

        Returns:
            True if request is allowed, False if rate limited
        """
        async with self._lock:
            now = time.monotonic()

            # Remove requests outside the window
            cutoff_time = now - self.window_seconds
            while self.requests and self.requests[0] <= cutoff_time:
                self.requests.popleft()

            # Check if we can make the request
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True

            return False

    async def wait_for_slot(self) -> None:
        """Wait until a request slot is available."""
        while True:
            if await self.acquire():
                return

            # Wait for the oldest request to exit the window
            async with self._lock:
                if self.requests:
                    wait_time = (self.requests[0] + self.window_seconds) - time.monotonic()
                    wait_time = max(0.01, wait_time)  # Minimum 10ms wait
                else:
                    wait_time = 0.01

            logger.debug(f"Rate limit reached, waiting {wait_time:.2f} seconds")
            await asyncio.sleep(wait_time)


class CircuitBreakerError(Exception):
    """Exception raised when circuit breaker is open."""

    pass


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.

    Prevents cascade failures by temporarily stopping requests
    to a failing service, giving it time to recover.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception,
    ):
        """
        Initialize the circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Time to wait before trying again (seconds)
            expected_exception: Exception type that counts as failure
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half-open
        self._lock = asyncio.Lock()

    async def __aenter__(self):
        """Context manager entry."""
        async with self._lock:
            now = time.monotonic()

            if self.state == "open":
                if (
                    self.last_failure_time
                    and (now - self.last_failure_time) > self.recovery_timeout
                ):
                    self.state = "half-open"
                    logger.info("Circuit breaker transitioning to half-open")
                else:
                    raise CircuitBreakerError("Circuit breaker is open")

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        async with self._lock:
            if exc_type and issubclass(exc_type, self.expected_exception):
                # Failure occurred
                self.failure_count += 1
                self.last_failure_time = time.monotonic()

                if self.failure_count >= self.failure_threshold:
                    self.state = "open"
                    logger.warning(f"Circuit breaker opened after {self.failure_count} failures")

            else:
                # Success
                if self.state == "half-open":
                    self.state = "closed"
                    self.failure_count = 0
                    logger.info("Circuit breaker closed after successful request")
                elif self.state == "closed":
                    self.failure_count = 0


# Global rate limiters for different services
_plivo_rate_limiter: Optional[TokenBucketRateLimiter] = None
_plivo_circuit_breaker: Optional[CircuitBreaker] = None
_twilio_rate_limiter: Optional[TokenBucketRateLimiter] = None
_twilio_circuit_breaker: Optional[CircuitBreaker] = None


def get_plivo_rate_limiter() -> TokenBucketRateLimiter:
    """Get the global Plivo rate limiter instance."""
    global _plivo_rate_limiter

    if _plivo_rate_limiter is None:
        _plivo_rate_limiter = TokenBucketRateLimiter(
            rate=api_config.PLIVO_RATE_LIMIT_CPS,
            burst_capacity=api_config.PLIVO_RATE_LIMIT_BURST,
        )

    return _plivo_rate_limiter


def get_plivo_circuit_breaker() -> CircuitBreaker:
    """Get the global Plivo circuit breaker instance."""
    global _plivo_circuit_breaker

    if _plivo_circuit_breaker is None:
        _plivo_circuit_breaker = CircuitBreaker(
            failure_threshold=api_config.PLIVO_CIRCUIT_BREAKER_FAILURE_THRESHOLD,
            recovery_timeout=api_config.PLIVO_CIRCUIT_BREAKER_RECOVERY_TIMEOUT,
            expected_exception=Exception,
        )

    return _plivo_circuit_breaker


def get_twilio_rate_limiter() -> TokenBucketRateLimiter:
    """Get the global Twilio rate limiter instance."""
    global _twilio_rate_limiter

    if _twilio_rate_limiter is None:
        _twilio_rate_limiter = TokenBucketRateLimiter(
            rate=api_config.TWILIO_RATE_LIMIT_CPS,
            burst_capacity=api_config.TWILIO_RATE_LIMIT_BURST,
        )

    return _twilio_rate_limiter


def get_twilio_circuit_breaker() -> CircuitBreaker:
    """Get the global Twilio circuit breaker instance."""
    global _twilio_circuit_breaker

    if _twilio_circuit_breaker is None:
        _twilio_circuit_breaker = CircuitBreaker(
            failure_threshold=api_config.TWILIO_CIRCUIT_BREAKER_FAILURE_THRESHOLD,
            recovery_timeout=api_config.TWILIO_CIRCUIT_BREAKER_RECOVERY_TIMEOUT,
            expected_exception=Exception,
        )

    return _twilio_circuit_breaker


async def with_plivo_rate_limiting_and_circuit_breaker(coro):
    """
    Execute a coroutine with Plivo rate limiting and circuit breaker protection.

    This function combines both rate limiting and circuit breaker patterns
    to provide comprehensive protection for Plivo API calls.

    Args:
        coro: Coroutine to execute

    Returns:
        Result of the coroutine

    Raises:
        CircuitBreakerError: If circuit breaker is open
        Any exception raised by the coroutine
    """
    rate_limiter = get_plivo_rate_limiter()
    circuit_breaker = get_plivo_circuit_breaker()

    # Wait for rate limit clearance
    await rate_limiter.wait_for_token()

    # Execute with circuit breaker protection
    async with circuit_breaker:
        return await coro


async def with_twilio_rate_limiting_and_circuit_breaker(coro):
    """
    Execute a coroutine with Twilio rate limiting and circuit breaker protection.

    This function combines both rate limiting and circuit breaker patterns
    to provide comprehensive protection for Twilio API calls.

    Args:
        coro: Coroutine to execute

    Returns:
        Result of the coroutine

    Raises:
        CircuitBreakerError: If circuit breaker is open
        Any exception raised by the coroutine
    """
    rate_limiter = get_twilio_rate_limiter()
    circuit_breaker = get_twilio_circuit_breaker()

    # Wait for rate limit clearance
    await rate_limiter.wait_for_token()

    # Execute with circuit breaker protection
    async with circuit_breaker:
        return await coro


class RetryWithExponentialBackoff:
    """
    Retry mechanism with exponential backoff.

    Useful for handling transient network errors and rate limiting responses.
    """

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
    ):
        """
        Initialize retry configuration.

        Args:
            max_attempts: Maximum number of retry attempts
            initial_delay: Initial delay between retries (seconds)
            max_delay: Maximum delay between retries (seconds)
            exponential_base: Base for exponential backoff calculation
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base

    async def execute(self, coro_func, *args, retryable_exceptions: tuple = (Exception,), **kwargs):
        """
        Execute a coroutine function with retry logic.

        Args:
            coro_func: Async function to execute
            *args: Arguments for the function
            retryable_exceptions: Tuple of exception types that should trigger retry
            **kwargs: Keyword arguments for the function

        Returns:
            Result of the function call

        Raises:
            Last exception encountered if all retries fail
        """
        last_exception = None

        for attempt in range(self.max_attempts):
            try:
                return await coro_func(*args, **kwargs)

            except retryable_exceptions as e:
                last_exception = e
                # Check if this specific exception should be retried
                if hasattr(e, "is_retryable") and not e.is_retryable:
                    logger.warning(f"Non-retryable exception encountered: {e}")
                    raise

                if attempt == self.max_attempts - 1:
                    # Last attempt failed, re-raise
                    raise

                # Calculate delay with exponential backoff
                delay = min(self.initial_delay * (self.exponential_base**attempt), self.max_delay)

                logger.warning(
                    f"Attempt {attempt + 1}/{self.max_attempts} failed: {e}. "
                    f"Retrying in {delay:.2f} seconds"
                )

                await asyncio.sleep(delay)

        # This should never be reached, but just in case
        if last_exception:
            raise last_exception
