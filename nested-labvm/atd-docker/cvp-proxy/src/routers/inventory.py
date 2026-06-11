from fastapi import APIRouter, HTTPException

from models import InventoryResponse, InventoryWaitRequest, DeviceInfo, CvpStatus

router = APIRouter(prefix="/inventory")


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


@router.get("", response_model=InventoryResponse)
async def get_inventory():
    _require_ready()
    state = _get_state()
    raw = await state.cvp_client.get_inventory()
    devices = {name: DeviceInfo(**info) for name, info in raw.items()}
    return InventoryResponse(devices=devices)


@router.post("/wait", response_model=InventoryResponse)
async def wait_for_devices(req: InventoryWaitRequest):
    _require_ready()
    state = _get_state()
    raw = await state.cvp_client.wait_for_devices(req.count, req.timeout)
    devices = {name: DeviceInfo(**info) for name, info in raw.items()}
    return InventoryResponse(devices=devices)
