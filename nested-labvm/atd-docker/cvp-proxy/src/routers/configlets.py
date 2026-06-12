from fastapi import APIRouter, HTTPException

from models import (
    ConfigletSyncRequest,
    ConfigletSyncResponse,
    ConfigletInfo,
    ConfigletDetail,
    CvpStatus,
)

router = APIRouter(prefix="/configlets")


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


@router.post("/sync", response_model=ConfigletSyncResponse)
async def sync_configlets(req: ConfigletSyncRequest):
    _require_ready()
    state = _get_state()
    client = state.cvp_client

    configlets_data = [{"name": c.name, "body": c.body} for c in req.configlets]

    async def apply_fn(ws_id):
        return await client.sync_configlets(ws_id, configlets_data)

    ws_id = await client.create_workspace("ATD Configlet Sync")
    counts = await client.sync_configlets(ws_id, configlets_data)

    if counts["created"] == 0 and counts["updated"] == 0:
        return ConfigletSyncResponse(status="success", **counts)

    if not await client.build_workspace(ws_id):
        raise HTTPException(status_code=500, detail="Workspace build failed")

    cc_ids, submitted = await client.submit_workspace(ws_id)
    if not submitted:
        raise HTTPException(status_code=500, detail="Workspace submit failed")

    return ConfigletSyncResponse(status="success", **counts)


@router.get("", response_model=list[ConfigletInfo])
async def list_configlets():
    _require_ready()
    state = _get_state()
    raw = await state.cvp_client.get_all_configlets()
    return [ConfigletInfo(**c) for c in raw]


@router.get("/{name}", response_model=ConfigletDetail)
async def get_configlet(name: str):
    _require_ready()
    state = _get_state()
    result = await state.cvp_client.get_configlet(name)
    if not result:
        raise HTTPException(status_code=404, detail=f"Configlet '{name}' not found")
    return ConfigletDetail(**result)
