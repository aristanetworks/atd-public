import time
from fastapi import APIRouter, Response

from models import HealthResponse, ReadyResponse, CvpStatus

router = APIRouter()

_start_time = time.time()


def _get_state():
    from state import app_state
    return app_state


@router.get("/health", response_model=HealthResponse)
async def health():
    state = _get_state()
    elapsed = int(time.time() - _start_time)
    messages = {
        CvpStatus.STARTING: "Proxy starting up...",
        CvpStatus.CONNECTING: "Connecting to CloudVision...",
        CvpStatus.WAITING: f"Waiting for CloudVision to become operational ({elapsed}s elapsed)",
        CvpStatus.READY: "CloudVision is operational",
        CvpStatus.DEGRADED: "CloudVision connection degraded, attempting recovery...",
    }
    return HealthResponse(
        cvp_status=state.cvp_client.status,
        cvp_version=state.cvp_client.cvp_version,
        uptime_seconds=elapsed,
        message=messages.get(state.cvp_client.status, "Unknown state"),
    )


@router.get("/ready")
async def ready(response: Response):
    state = _get_state()
    elapsed = int(time.time() - _start_time)
    if state.cvp_client.status == CvpStatus.READY:
        return ReadyResponse(
            cvp_status=CvpStatus.READY,
            message="CloudVision is operational",
        )
    response.status_code = 503
    return ReadyResponse(
        cvp_status=state.cvp_client.status,
        message=f"CloudVision not ready ({state.cvp_client.status.value}, {elapsed}s elapsed)",
    )
