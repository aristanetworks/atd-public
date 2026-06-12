import logging

from fastapi import APIRouter, HTTPException

from models import (
    EnrollmentTokenRequest,
    EnrollmentTokenResponse,
    EnrollmentStatusResponse,
    TagsInitRequest,
    TagsInitResponse,
    CvpStatus,
)

router = APIRouter()
logger = logging.getLogger("enrollment")


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
async def init_tags(req: TagsInitRequest = TagsInitRequest()):
    _require_ready()
    state = _get_state()
    client = state.cvp_client

    devices = await client.get_inventory()

    if req.hostnames:
        serial_to_device = {}
        for name, info in devices.items():
            did = info.get("device_id", "")
            if did:
                serial_to_device[did] = info

        tagged_devices = {}
        for intended_hostname in req.hostnames:
            dev = serial_to_device.get(intended_hostname)
            if dev:
                tagged_devices[intended_hostname] = dev
                logger.info(
                    "Matched %s to device serial %s (current hostname: %s)",
                    intended_hostname, dev["device_id"], dev.get("hostname", "?"),
                )
            else:
                logger.warning(
                    "No device with serial %s found in inventory", intended_hostname,
                )
    elif req.hostname_map:
        ip_to_device = {}
        for name, info in devices.items():
            ip = info.get("ip", "")
            if ip:
                ip_to_device[ip] = info

        tagged_devices = {}
        for intended_hostname, device_ip in req.hostname_map.items():
            dev = ip_to_device.get(device_ip)
            if dev:
                tagged_devices[intended_hostname] = dev
            else:
                logger.warning(
                    "No device found for %s at IP %s", intended_hostname, device_ip,
                )
    else:
        tagged_devices = devices

    if not tagged_devices:
        logger.warning("No devices matched for tagging")
        return TagsInitResponse(status="no_matches", tags_created=0)

    logger.info("Tagging %d devices: %s", len(tagged_devices), list(tagged_devices.keys()))

    async def apply_fn(ws_id):
        return await client.init_device_tags(ws_id, tagged_devices)

    try:
        cc_ids = await client.workspace_flow("ATD Tag Init", apply_fn)
    except Exception as e:
        logger.error("Tag init workspace flow failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Tag init failed: {e}")

    return TagsInitResponse(status="success", tags_created=len(tagged_devices))
