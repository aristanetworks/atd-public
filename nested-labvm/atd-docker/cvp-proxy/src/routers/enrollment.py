from fastapi import APIRouter, HTTPException

from models import (
    EnrollmentTokenRequest,
    EnrollmentTokenResponse,
    EnrollmentStatusResponse,
    TagsInitResponse,
    CvpStatus,
)

router = APIRouter()


def _get_state():
    from main import app_state
    return app_state


def _require_ready():
    state = _get_state()
    if state.cvp_client.status != CvpStatus.READY:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "cvp_not_ready",
                "cvp_status": state.cvp_client.status.value,
                "message": f"CloudVision is not yet operational. Current status: {state.cvp_client.status.value}",
            },
        )


@router.post("/enrollment/token", response_model=EnrollmentTokenResponse)
async def create_enrollment_token(req: EnrollmentTokenRequest):
    _require_ready()
    state = _get_state()
    token = await state.cvp_client.create_enrollment_token(req.duration)
    return EnrollmentTokenResponse(token=token)


@router.get("/enrollment/status", response_model=EnrollmentStatusResponse)
async def get_enrollment_status():
    _require_ready()
    state = _get_state()
    status = await state.cvp_client.get_enrollment_status()
    return EnrollmentStatusResponse(**status)


@router.post("/tags/init", response_model=TagsInitResponse)
async def init_tags():
    _require_ready()
    state = _get_state()
    client = state.cvp_client

    devices = await client.get_inventory()
    ws_id = await client.create_workspace("ATD Tag Init")
    count = await client.init_device_tags(ws_id, devices)

    if count > 0:
        if not await client.build_workspace(ws_id):
            raise HTTPException(status_code=500, detail="Tag workspace build failed")
        cc_ids, submitted = await client.submit_workspace(ws_id)
        if not submitted:
            raise HTTPException(status_code=500, detail="Tag workspace submit failed")

    return TagsInitResponse(status="success", tags_created=count)
