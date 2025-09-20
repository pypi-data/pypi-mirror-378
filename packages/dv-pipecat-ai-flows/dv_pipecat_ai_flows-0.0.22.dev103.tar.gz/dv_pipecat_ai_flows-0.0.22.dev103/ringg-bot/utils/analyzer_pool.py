"""Smart Turn Analyzer Pool for Zero-Latency Turn Detection.

This module provides pre-warmed Smart Turn analyzers to eliminate
cold-start latency on incoming calls.
"""

import asyncio
from typing import Optional, Tuple

import numpy as np
import torch
from env_config import api_config
from loguru import logger

from pipecat.audio.turn.smart_turn.base_smart_turn import SmartTurnParams
from pipecat.audio.turn.smart_turn.local_smart_turn_v2 import LocalSmartTurnAnalyzerV2


class SmartTurnAnalyzerPool:
    """Pool of pre-warmed Smart Turn analyzers for zero-latency initialization."""

    def __init__(self, pool_size: int = 5):
        """Initialize the Smart Turn analyzer pool.

        Args:
            pool_size: Number of Smart Turn analyzers to pre-warm
        """
        self.pool_size = pool_size
        self.turn_queue = asyncio.Queue()
        self.warmup_complete = False

        # Configuration for Smart Turn
        self.smart_turn_sr = 16000  # Smart Turn internal sample rate
        self.warmup_duration_sec = 2  # Duration for warmup audio

    async def warmup_and_fill(self):
        """Pre-warm and fill the Smart Turn analyzer pool."""
        logger.info(f"Starting Smart Turn analyzer pool warmup (size={self.pool_size})")

        # Prepare warmup audio buffer
        warmup_16k = np.zeros(int(self.smart_turn_sr * self.warmup_duration_sec), dtype=np.float32)

        # Configure thread limits for predictable CPU usage
        torch.set_num_threads(1)
        torch.set_num_interop_threads(1)

        for i in range(self.pool_size):
            logger.debug(f"Warming up Smart Turn analyzer {i + 1}/{self.pool_size}")

            # Create and warm Smart Turn analyzer
            turn_analyzer = await self._create_and_warm_smart_turn(warmup_16k, i)
            if turn_analyzer:
                await self.turn_queue.put(turn_analyzer)
            else:
                logger.warning(
                    f"Failed to create Smart Turn analyzer {i + 1}, pool will have {i} analyzers"
                )
                break

        self.warmup_complete = True
        actual_size = self.turn_queue.qsize()
        logger.info(f"Smart Turn analyzer pool warmup complete. {actual_size} analyzers ready.")

    async def _create_and_warm_smart_turn(
        self, warmup_audio: np.ndarray, index: int
    ) -> Optional[LocalSmartTurnAnalyzerV2]:
        """Create and warm up a Smart Turn analyzer."""
        try:
            # Get model path from api_config or use HuggingFace
            model_path = (
                api_config.LOCAL_SMART_TURN_MODEL_PATH
                if api_config.LOCAL_SMART_TURN_MODEL_PATH
                else None
            )

            if model_path:
                import os

                if not os.path.exists(model_path):
                    logger.warning(f"LOCAL_SMART_TURN_MODEL_PATH set but not found: {model_path}")
                    model_path = None

            turn = LocalSmartTurnAnalyzerV2(
                smart_turn_model_path=model_path,  # None will auto-download from HF
                params=SmartTurnParams(
                    stop_secs=0.6,  # Fallback silence timeout
                    pre_speech_ms=0.0,
                    max_duration_secs=6.0,  # Max audio segment to analyze
                ),
            )

            # Warm up the model with dummy inference
            with torch.inference_mode():
                _ = await turn._predict_endpoint(warmup_audio)

            logger.debug(f"Smart Turn {index + 1} warmed up successfully")
            return turn

        except Exception as e:
            logger.error(f"Failed to create/warm Smart Turn analyzer {index + 1}: {e}")
            logger.info("Continuing without Smart Turn - VAD-only mode")
            return None

    async def acquire(self) -> Optional[LocalSmartTurnAnalyzerV2]:
        """Acquire a warmed Smart Turn analyzer from the pool.

        Returns:
            Smart Turn analyzer or None if pool is empty
        """
        if not self.warmup_complete:
            logger.warning(
                "Acquiring analyzer before warmup complete - waiting for pool initialization"
            )
            # Wait for warmup to complete
            while not self.warmup_complete:
                await asyncio.sleep(0.1)

        # Block until an analyzer is available - this ensures the pool always serves requests
        turn = await self.turn_queue.get()
        logger.debug(
            f"Acquired Smart Turn analyzer from pool (remaining: {self.turn_queue.qsize()})"
        )
        return turn

    async def release(self, turn: Optional[LocalSmartTurnAnalyzerV2]):
        """Release Smart Turn analyzer back to the pool for reuse.

        Args:
            turn: Smart Turn analyzer to release (can be None)
        """
        if turn:
            await self.turn_queue.put(turn)
            logger.debug(
                f"Released Smart Turn analyzer back to pool (available: {self.turn_queue.qsize()})"
            )
        else:
            logger.warning(
                "Attempted to release None analyzer - this indicates an error in acquisition"
            )

    @property
    def is_ready(self) -> bool:
        """Check if the pool is warmed up and ready."""
        return self.warmup_complete

    async def shutdown(self):
        """Clean shutdown of the Smart Turn analyzer pool."""
        logger.info("Shutting down Smart Turn analyzer pool")
        # Drain queue to allow garbage collection
        while not self.turn_queue.empty():
            await self.turn_queue.get()


# Global Smart Turn analyzer pool instance
_smart_turn_pool: Optional[SmartTurnAnalyzerPool] = None


async def initialize_smart_turn_pool(
    pool_size: int = 5, enable_smart_turn: bool = False
) -> Optional[SmartTurnAnalyzerPool]:
    """Initialize the global Smart Turn analyzer pool.

    Args:
        pool_size: Number of Smart Turn analyzers to pre-warm
        enable_smart_turn: Whether to enable Smart Turn (if False, returns None)

    Returns:
        The initialized Smart Turn analyzer pool or None if not enabled
    """
    global _smart_turn_pool

    if not enable_smart_turn:
        logger.info("Smart Turn is disabled, skipping pool initialization")
        return None

    if _smart_turn_pool is None:
        _smart_turn_pool = SmartTurnAnalyzerPool(pool_size=pool_size)
        await _smart_turn_pool.warmup_and_fill()

    return _smart_turn_pool


def get_smart_turn_pool() -> Optional[SmartTurnAnalyzerPool]:
    """Get the global Smart Turn analyzer pool instance.

    Returns:
        The Smart Turn analyzer pool or None if not initialized
    """
    return _smart_turn_pool
