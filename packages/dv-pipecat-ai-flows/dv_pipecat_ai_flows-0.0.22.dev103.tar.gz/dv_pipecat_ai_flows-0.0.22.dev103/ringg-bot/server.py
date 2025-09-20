# IMPORTANT: Import patch_imports first to handle missing dependencies
import asyncio
import json
import os
import time  # Import time for sleep
from contextlib import asynccontextmanager

import aioboto3
import redis.asyncio as redis
import uvicorn
from env_config import api_config
from fastapi import APIRouter, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from kubernetes_asyncio import client as async_client
from kubernetes_asyncio import config as async_config
from loguru import logger
from misc.router import router as misc_router
from utils.plivo_async_client import cleanup_plivo_session
from utils.twilio_async_client import cleanup_twilio_client
from utils.asterisk_ari_client import cleanup_asterisk_session
from pathlib import Path
import signal

# IMPORTANT: This logger_config import must come first, before any other imports that might use loguru
from utils import logger_config
from rag.weaviate_client import weaviate_client_manager
from starlette.responses import JSONResponse
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE  # Import status code

# Import voice services common functions
from voice_services.common import set_redis_client, set_websocket_connections

# Import all routers
from voice_services.convox.router import router as convox_router
from voice_services.exotel.router import router as exotel_router
from voice_services.plivo.router import router as plivo_router
from voice_services.twilio.router import router as twilio_router
from voice_services.webcall.webcall_router import router as webcall_router
from websocket.router import router as websocket_router

# Add after the existing imports
session = aioboto3.Session(
    aws_access_key_id=api_config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=api_config.AWS_SECRET_ACCESS_KEY,
    region_name=api_config.AWS_REGION,
)
BUCKET_NAME = api_config.S3_BUCKET_NAME

REDIS_URL = api_config.REDIS_URL
redis_pool = None
redis_client = None
is_shutting_down = False
k8s_client = None
DOCKER_KILL_TIMEOUT = 240


def _sigterm_handler(*_):
    try:
        Path("/tmp/DRaining").touch()
    except Exception:
        pass


try:
    signal.signal(signal.SIGTERM, _sigterm_handler)
except Exception:
    # Not all environments allow setting signals (e.g., non-main thread)
    pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize connection
    global redis_pool, redis_client, is_shutting_down, k8s_client

    # Initialize connections
    # Set decode_responses=False to handle binary data like cached MP3s correctly
    redis_pool = redis.ConnectionPool.from_url(REDIS_URL, decode_responses=False)
    redis_client = redis.Redis.from_pool(redis_pool)
    logger.info("Redis connection pool initialized (decode_responses=False)")

    # Initialize async Kubernetes client
    if api_config.ENVIRONMENT in ["production", "staging"]:
        async_config.load_incluster_config()
        k8s_client = async_client.CoreV1Api()
        logger.info("Using in-cluster Kubernetes configuration and initialized k8s client")

    # Set global variables in common module
    set_redis_client(redis_client)
    set_websocket_connections({})

    # Initialize Smart Turn analyzer pool for zero-latency turn detection
    # try:
    #     if api_config.ENABLE_SMART_TURN:
    #         logger.info(f"Initializing Smart Turn analyzer pool (size={api_config.ANALYZER_POOL_SIZE})")

    #         smart_turn_pool = await initialize_smart_turn_pool(
    #             pool_size=api_config.ANALYZER_POOL_SIZE,
    #             enable_smart_turn=api_config.ENABLE_SMART_TURN
    #         )

    #         if smart_turn_pool:
    #             logger.info("Smart Turn analyzer pool initialized and warmed successfully")
    #         else:
    #             logger.info("Smart Turn disabled or pool initialization skipped")
    #     else:
    #         logger.info("Smart Turn is disabled in configuration")
    # except Exception as e:
    #     logger.error(f"Failed to initialize Smart Turn analyzer pool: {e}")
    #     logger.info("Continuing without pre-warmed Smart Turn analyzers")

    is_shutting_down = False
    yield
    is_shutting_down = True
    logger.info("Application is shutting down, waiting for active calls to complete...")
    # Clean up resources
    if redis_client:
        await redis_client.aclose()

    await cleanup_asterisk_session()
    await cleanup_plivo_session()
    await cleanup_twilio_client()

    # Clean up Kubernetes client
    if k8s_client:
        await k8s_client.api_client.close()
        logger.info("Kubernetes client closed")

    # Clean up HTTP client sessions would be handled by individual services

    logger.info("Graceful shutdown completed")


app = FastAPI(lifespan=lifespan)
router = APIRouter()


# Dependency to verify X-API-KEY header for specific endpoints
async def verify_x_api_key_header(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key != api_config.X_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


ngrok_url = api_config.NGROK_URL
print("ngrok_url:", ngrok_url)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@router.get("/live")
async def live():
    # Always 200 unless the process is truly broken
    return {"status": "live"}


@router.get("/ready")
async def ready():
    # Fail readiness when draining so the pod is removed from Service/NEG
    try:
        from pathlib import Path

        draining_flag = Path("/tmp/DRaining").exists()
    except Exception:
        draining_flag = False
    if is_shutting_down or draining_flag:
        return JSONResponse({"status": "draining"}, status_code=HTTP_503_SERVICE_UNAVAILABLE)
    return {"status": "ready"}


@app.get("/drain/start")
async def start_drain():
    global is_shutting_down
    if not is_shutting_down:
        logger.info("Drain requested via /drain/start; entering shutdown mode")
        is_shutting_down = True
    # Create a file flag so all workers/processes see the drain state
    try:
        Path("/tmp/DRaining").touch()
    except Exception as e:
        logger.warning(f"Failed to create drain flag file: {e}")
    return {"status": "draining"}


# Include the main router
app.include_router(router)

# Include all telephony routers
app.include_router(plivo_router)
app.include_router(twilio_router)
app.include_router(exotel_router)
app.include_router(convox_router)

# Include WebSocket router
app.include_router(websocket_router)

# Include WebCall router
app.include_router(webcall_router)

# Include misc router
app.include_router(misc_router)

# Include routers with /pc/v1 prefix for backward compatibility
app.include_router(router, prefix="/pc/v1")
app.include_router(plivo_router, prefix="/pc/v1")
app.include_router(twilio_router, prefix="/pc/v1")
app.include_router(exotel_router, prefix="/pc/v1")
app.include_router(convox_router, prefix="/pc/v1")
app.include_router(websocket_router, prefix="/pc/v1")
app.include_router(webcall_router, prefix="/pc/v1")
app.include_router(misc_router, prefix="/pc/v1")

if __name__ == "__main__":
    print("Executing __main__ block")
    print(f"ENVIRONMENT value: {api_config.ENVIRONMENT}")

    environment = getattr(api_config, "ENVIRONMENT", "development")
    reload = environment == "development" or environment == "local"
    workers = 2 if environment == "production" else 1
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8765,
        reload=reload,
        workers=workers,
        timeout_graceful_shutdown=DOCKER_KILL_TIMEOUT - 10,
    )
