from pydantic import BaseModel
from typing import Optional
from enum import Enum


class CvpStatus(str, Enum):
    STARTING = "STARTING"
    CONNECTING = "CONNECTING"
    WAITING = "WAITING"
    READY = "READY"
    DEGRADED = "DEGRADED"


class HealthResponse(BaseModel):
    proxy: str = "ok"
    cvp_status: CvpStatus
    cvp_version: Optional[str] = None
    uptime_seconds: int
    message: str


class ReadyResponse(BaseModel):
    cvp_status: CvpStatus
    message: str


class ConfigletInput(BaseModel):
    name: str
    body: str


class ConfigletSyncRequest(BaseModel):
    configlets: list[ConfigletInput]


class ConfigletSyncResponse(BaseModel):
    status: str
    created: int = 0
    updated: int = 0
    unchanged: int = 0


class ConfigletInfo(BaseModel):
    id: str
    name: str
    size: int


class ConfigletDetail(BaseModel):
    name: str
    body: str
    size: int


class AssignmentApplyRequest(BaseModel):
    device_assignments: dict[str, list[str]]
    global_configlets: list[str] = []


class AssignmentApplyResponse(BaseModel):
    status: str
    devices_updated: int = 0
    cc_ids: list[str] = []


class DeviceInfo(BaseModel):
    device_id: str
    hostname: str
    ip: str = ""
    streaming_status: str = "unknown"
    model: str = ""


class InventoryResponse(BaseModel):
    devices: dict[str, DeviceInfo]


class InventoryWaitRequest(BaseModel):
    count: int
    timeout: int = 300


class TagsInitRequest(BaseModel):
    hostname_map: dict[str, str] = {}
    hostnames: list[str] = []


class TagsInitResponse(BaseModel):
    status: str
    tags_created: int = 0


class EnrollmentTokenRequest(BaseModel):
    duration: str = "86400s"


class EnrollmentTokenResponse(BaseModel):
    token: str


class EnrollmentStatusResponse(BaseModel):
    total: int
    active: int
    inactive: int
    inactive_devices: list[str]


class CvpStatusResponse(BaseModel):
    status: str
    version: str = ""


class ChangeControlInfo(BaseModel):
    id: str
    status: str
    created: str = ""
    stages: dict[str, int] = {}


class ChangeControlsResponse(BaseModel):
    pending: int = 0
    running: int = 0
    completed: int = 0
    recent: list[ChangeControlInfo] = []
