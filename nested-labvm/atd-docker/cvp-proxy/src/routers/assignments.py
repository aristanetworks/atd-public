import json
import logging

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from models import AssignmentApplyRequest, AssignmentApplyResponse, CvpStatus

router = APIRouter(prefix="/assignments")
logger = logging.getLogger("assignments")


def _get_state():
    from state import app_state
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


@router.post("/apply")
async def apply_assignments(req: AssignmentApplyRequest, stream: bool = False):
    _require_ready()
    if stream:
        return EventSourceResponse(_assignment_stream(req))
    return await _apply_blocking(req)


async def _apply_blocking(req: AssignmentApplyRequest) -> AssignmentApplyResponse:
    state = _get_state()
    client = state.cvp_client

    ws_id = await client.create_workspace("ATD Assignment Apply")
    logger.info("Created assignment workspace %s", ws_id)

    await client.apply_assignments(ws_id, req.device_assignments, req.global_configlets)
    logger.info("Assignments written to workspace, building...")

    if not await client.build_workspace(ws_id):
        raise HTTPException(status_code=500, detail="Workspace build failed")
    logger.info("Workspace built, submitting...")

    cc_ids, submitted = await client.submit_workspace(ws_id)
    logger.info("Workspace submitted=%s, cc_ids=%s", submitted, cc_ids)
    if not submitted:
        raise HTTPException(status_code=500, detail="Workspace submit failed")

    if cc_ids:
        logger.info("Executing %d change controls: %s", len(cc_ids), cc_ids)
        await client.execute_change_controls(cc_ids)
        logger.info("Change controls executed")
    else:
        logger.warning("No change controls generated from assignment workspace")

    return AssignmentApplyResponse(
        status="success",
        devices_updated=len(req.device_assignments),
        cc_ids=cc_ids,
    )


async def _assignment_stream(req: AssignmentApplyRequest):
    state = _get_state()
    client = state.cvp_client

    yield {"data": json.dumps({"phase": "WORKSPACE", "message": "Creating workspace..."})}

    ws_id = await client.create_workspace("ATD Assignment Apply")

    device_count = len(req.device_assignments)
    yield {"data": json.dumps({"phase": "ASSIGNMENTS", "message": f"Updating {device_count} device assignments..."})}
    await client.apply_assignments(ws_id, req.device_assignments, req.global_configlets)

    yield {"data": json.dumps({"phase": "BUILD", "message": "Building configuration..."})}
    if not await client.build_workspace(ws_id):
        yield {"data": json.dumps({"phase": "ERROR", "message": "Workspace build failed"})}
        return

    yield {"data": json.dumps({"phase": "SUBMIT", "message": "Submitting changes..."})}
    cc_ids, submitted = await client.submit_workspace(ws_id)
    if not submitted:
        yield {"data": json.dumps({"phase": "ERROR", "message": "Workspace submit failed"})}
        return

    if cc_ids:
        yield {"data": json.dumps({"phase": "CC", "message": f"Executing change control {cc_ids[0]}..."})}
        await client.execute_change_controls(cc_ids)

    yield {"data": json.dumps({
        "phase": "DONE",
        "message": "Completed",
        "devices_updated": device_count,
        "cc_ids": cc_ids,
    })}


@router.get("")
async def get_assignments():
    _require_ready()
    state = _get_state()
    return await state.cvp_client.get_assignments()
