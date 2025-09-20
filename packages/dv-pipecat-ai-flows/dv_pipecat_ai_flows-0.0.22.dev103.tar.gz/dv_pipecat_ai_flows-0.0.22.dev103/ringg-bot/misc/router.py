from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from misc.misc_service import MiscService
from env_config import api_config
from utils.http_client import create_http_client_session
from kubernetes_asyncio import client as async_client

router = APIRouter(tags=["misc"])

# Import k8s_client from server module
def get_k8s_client():
    """Get the Kubernetes client from server module."""
    try:
        import server
        return getattr(server, 'k8s_client', None)
    except ImportError:
        return None


@router.get("/transcript/{call_id}")
async def get_call_transcript(call_id: str, misc_service=None):
    """Get call transcript by call ID"""
    if misc_service is None:
        misc_service = MiscService()

    try:
        result = await misc_service.get_transcript(call_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transcript_url/{call_id}")
async def get_call_transcript_url(call_id: str, misc_service=None):
    """Get call transcript URL by call ID"""
    if misc_service is None:
        misc_service = MiscService()

    try:
        result = await misc_service.get_transcript_url(call_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache_test_mp3")
async def put_file_on_redis_api(misc_service=None):
    """API to cache test_cache.mp3 in Redis using put_file_on_redis."""
    if misc_service is None:
        misc_service = MiscService()

    try:
        result = await misc_service.cache_test_mp3()
        return result
    except Exception as e:
        logger.error(f"Failed to cache mp3 file: {e}")
        raise HTTPException(status_code=500, detail="Failed to cache MP3 file.")


@router.get("/get_tts_file")
async def get_tts_file_api(text: str = Query(...), misc_service=None):
    """API endpoint to retrieve a cached TTS file from Redis and save it locally."""
    if misc_service is None:
        misc_service = MiscService()

    try:
        result = await misc_service.get_tts_file(text)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error retrieving TTS file from Redis: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve TTS file from Redis.")


@router.get("/status")
async def get_pod_status():
    """Get current pipecat deployment pod status and update calling agent backend using async Kubernetes client."""

    # Get Kubernetes client from server module
    k8s_client = get_k8s_client()

    # Check if Kubernetes client is available
    if k8s_client is None:
        logger.error("Kubernetes client not initialized")
        raise HTTPException(status_code=500, detail="Kubernetes client not available")

    try:
        namespace = "default"
        label_selector = "app.kubernetes.io/name=dv-pipecat"

        try:
            # Use async Kubernetes client
            pods_response = await k8s_client.list_namespaced_pod(
                namespace=namespace, label_selector=label_selector
            )

            # Count running and ready pods
            active_pods = 0
            total_pods = len(pods_response.items)

            for pod in pods_response.items:
                pod_status = pod.status
                phase = pod_status.phase
                conditions = pod_status.conditions or []

                # Check if pod is Running and Ready
                is_running = phase == "Running"
                is_ready = any(
                    condition.type == "Ready" and condition.status == "True"
                    for condition in conditions
                )

                if is_running and is_ready:
                    active_pods += 1

            logger.info(f"Found {total_pods} total pods, {active_pods} running and ready")
        except async_client.ApiException as e:
            logger.error(f"Kubernetes API error: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get pod status: {e}")
    except Exception as e:
        logger.error(f"Error getting pod status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get pod status")

    # Send concurrency update to calling agent backend
    try:
        calling_agent_url = api_config.CALLING_BACKEND_URL
        update_url = f"{calling_agent_url}/admin/global/pods"
        update_payload = {"pods": active_pods}

        # Send POST request to calling agent backend with authentication
        headers = {"X-ADMIN-API-KEY": api_config.ADMIN_API_KEY}

        async with create_http_client_session() as session:
            async with session.patch(update_url, json=update_payload, headers=headers) as response:
                if response.status == 200:
                    response_json = await response.json()
                    logger.info(f"Successfully updated calling agent backend: {response_json}")
                else:
                    response_text = await response.text()
                    logger.error(f"Failed to update calling agent backend: {response_text}")
    except Exception as e:
        logger.error(f"Error updating calling agent backend: {e}")
        # Don't fail the endpoint if backend update fails

    return {"pods": active_pods}
