from fastapi import APIRouter

from models import CvpStatusResponse, ChangeControlsResponse, ChangeControlInfo, CvpStatus

router = APIRouter()


def _get_state():
    from state import app_state
    return app_state


@router.get("/cvp/status", response_model=CvpStatusResponse)
async def get_cvp_status():
    state = _get_state()
    if state.cvp_client.status == CvpStatus.READY:
        return CvpStatusResponse(
            status="UP",
            version=state.cvp_client.cvp_version or "",
        )
    return CvpStatusResponse(status="DOWN", version="")


@router.get("/changecontrols", response_model=ChangeControlsResponse)
async def get_change_controls():
    state = _get_state()
    if state.cvp_client.status != CvpStatus.READY:
        return ChangeControlsResponse()
    try:
        raw = await state.cvp_client.get_change_controls()
        return ChangeControlsResponse(
            pending=raw.get("pending", 0),
            running=raw.get("running", 0),
            completed=raw.get("completed", 0),
            recent=[ChangeControlInfo(**cc) for cc in raw.get("recent", [])],
        )
    except Exception:
        return ChangeControlsResponse()
