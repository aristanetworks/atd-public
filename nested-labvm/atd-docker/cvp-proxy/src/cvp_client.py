import asyncio
import hashlib
import ssl
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional

import requests

from cloudvision.api import client as cv_client
from cloudvision.api.arista.configlet import v1 as configlet
from cloudvision.api.arista.workspace import v1 as workspace
from cloudvision.api.arista.inventory import v1 as inventory
from cloudvision.api.arista.tag import v2 as tag

try:
    from cloudvision.api.arista.changecontrol import v1 as changecontrol
except ImportError:
    changecontrol = None

try:
    from cloudvision.api.arista.studio_topology import v1 as studio_topology
except ImportError:
    studio_topology = None

from fmp import wrappers_pb2 as fmp

from models import CvpStatus

logger = logging.getLogger("cvp_client")

def _val(field, default=""):
    if field is None:
        return default
    return field.value if hasattr(field, "value") else field

RPC_TIMEOUT = 30
BUILD_TIMEOUT = 600
SUBMIT_TIMEOUT = 300
CC_TIMEOUT = 600
MAX_SYNC_RETRIES = 3
MAINLINE_ID = ""


class CVPClient:
    def __init__(self):
        self._status: CvpStatus = CvpStatus.STARTING
        self.channel = None
        self.cvp_version: Optional[str] = None
        self._host: Optional[str] = None
        self._token: Optional[str] = None
        self._cv_client = None
        logger.info("CVP client status: %s", self._status.value)

    @property
    def status(self) -> CvpStatus:
        return self._status

    @status.setter
    def status(self, new_status: CvpStatus):
        if new_status != self._status:
            logger.info("CVP status changed: %s -> %s", self._status.value, new_status.value)
            self._status = new_status

    async def connect(self, host: str, username: str, password: str):
        self._host = host
        self.status = CvpStatus.CONNECTING
        try:
            token = self._login(host, username, password)
            self._token = token
            self._cv_client = cv_client.AsyncCVClient.from_token(
                token=token, host=host, port=443, insecure=True
            )
            self.channel = self._cv_client.__enter__()
            await self._probe()
            self.status = CvpStatus.READY
            logger.info("Connected to CVP at %s", host)
        except Exception as e:
            logger.warning("Failed to connect to CVP: %s", e)
            self.status = CvpStatus.WAITING
            if self._cv_client:
                try:
                    self._cv_client.__exit__(None, None, None)
                except Exception:
                    pass
                self._cv_client = None
            self.channel = None
            raise

    def _login(self, host: str, username: str, password: str) -> str:
        resp = requests.post(
            f"https://{host}/cvpservice/login/authenticate.do",
            auth=(username, password),
            verify=False,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()["sessionId"]

    async def _probe(self):
        stub = inventory.DeviceServiceStub(self.channel)
        req = inventory.DeviceStreamRequest()
        count = 0
        async for _ in stub.get_all(req, timeout=RPC_TIMEOUT):
            count += 1
            if count >= 1:
                break

    async def health_probe(self) -> bool:
        try:
            await self._probe()
            if self.status == CvpStatus.DEGRADED:
                self.status = CvpStatus.READY
            return True
        except Exception:
            if self.status == CvpStatus.READY:
                self.status = CvpStatus.DEGRADED
            return False

    def _require_ready(self):
        if self.status != CvpStatus.READY:
            raise RuntimeError(f"CVP not ready: {self.status.value}")

    # ------------------------------------------------------------------
    # Inventory
    # ------------------------------------------------------------------

    async def get_inventory(self) -> dict[str, dict]:
        self._require_ready()
        stub = inventory.DeviceServiceStub(self.channel)
        req = inventory.DeviceStreamRequest()
        devices = {}
        async for resp in stub.get_all(req, timeout=RPC_TIMEOUT):
            dev = resp.value
            hostname = _val(dev.hostname)
            device_id = _val(dev.key.device_id) if dev.key else ""
            streaming = "active"
            if hasattr(dev, "streaming_status"):
                s = _val(dev.streaming_status)
                s_lower = str(s).lower()
                if "active" in s_lower and "inactive" not in s_lower:
                    streaming = "active"
                elif "inactive" in s_lower:
                    streaming = "inactive"
                else:
                    streaming = "unknown"
            ip_addr = _val(dev.fqdn)
            model = _val(dev.model_name)
            devices[hostname or device_id] = {
                "device_id": device_id,
                "hostname": hostname,
                "ip": ip_addr,
                "streaming_status": streaming,
                "model": model,
            }
        return devices

    async def wait_for_devices(self, count: int, timeout: int = 300) -> dict[str, dict]:
        self._require_ready()
        elapsed = 0
        while elapsed < timeout:
            devices = await self.get_inventory()
            if len(devices) >= count:
                return devices
            await asyncio.sleep(15)
            elapsed += 15
        return await self.get_inventory()

    # ------------------------------------------------------------------
    # Workspace lifecycle
    # ------------------------------------------------------------------

    async def create_workspace(self, display_name: str) -> str:
        self._require_ready()
        ws_id = str(uuid.uuid4())
        stub = workspace.WorkspaceConfigServiceStub(self.channel)
        req = workspace.WorkspaceConfigSetRequest(
            value=workspace.WorkspaceConfig(
                key=workspace.WorkspaceKey(workspace_id=ws_id),
                display_name=display_name,
            )
        )
        await stub.set(req, timeout=RPC_TIMEOUT)
        return ws_id

    async def build_workspace(self, ws_id: str) -> bool:
        build_id = str(uuid.uuid4())
        stub = workspace.WorkspaceConfigServiceStub(self.channel)
        req = workspace.WorkspaceConfigSetRequest(
            value=workspace.WorkspaceConfig(
                key=workspace.WorkspaceKey(workspace_id=ws_id),
                request=workspace.Request.START_BUILD,
                request_params=workspace.RequestParams(request_id=build_id),
            )
        )
        await stub.set(req, timeout=RPC_TIMEOUT)

        state_stub = workspace.WorkspaceServiceStub(self.channel)
        stream_req = workspace.WorkspaceStreamRequest(
            partial_eq_filter=[
                workspace.Workspace(key=workspace.WorkspaceKey(workspace_id=ws_id))
            ]
        )
        async for res in state_stub.subscribe(stream_req, timeout=BUILD_TIMEOUT):
            if res.value.responses and build_id in res.value.responses.values:
                build_res = res.value.responses.values[build_id]
                if build_res.status == workspace.ResponseStatus.SUCCESS:
                    return True
                elif build_res.status == workspace.ResponseStatus.FAIL:
                    logger.error("Build failed: %s", build_res.message.value if build_res.message else "unknown")
                    return False
        return False

    async def submit_workspace(self, ws_id: str) -> tuple[list[str], bool]:
        submit_id = str(uuid.uuid4())
        stub = workspace.WorkspaceConfigServiceStub(self.channel)
        req = workspace.WorkspaceConfigSetRequest(
            value=workspace.WorkspaceConfig(
                key=workspace.WorkspaceKey(workspace_id=ws_id),
                request=workspace.Request.SUBMIT,
                request_params=workspace.RequestParams(request_id=submit_id),
            )
        )
        await stub.set(req, timeout=RPC_TIMEOUT)

        state_stub = workspace.WorkspaceServiceStub(self.channel)
        stream_req = workspace.WorkspaceStreamRequest(
            partial_eq_filter=[
                workspace.Workspace(key=workspace.WorkspaceKey(workspace_id=ws_id))
            ]
        )
        async for res in state_stub.subscribe(stream_req, timeout=SUBMIT_TIMEOUT):
            if res.value.responses and submit_id in res.value.responses.values:
                submit_res = res.value.responses.values[submit_id]
                if submit_res.status == workspace.ResponseStatus.SUCCESS:
                    cc_ids = list(res.value.cc_ids.values) if res.value.cc_ids else []
                    return cc_ids, True
                elif submit_res.status == workspace.ResponseStatus.FAIL:
                    logger.error("Submit failed: %s", submit_res.message.value if submit_res.message else "unknown")
                    return [], False
        return [], False

    async def execute_change_controls(self, cc_ids: list[str]):
        if not changecontrol or not cc_ids:
            return
        for cc_id in cc_ids:
            try:
                await self._execute_single_cc(cc_id)
            except Exception as e:
                logger.error("Failed to execute CC %s: %s", cc_id, e)

    async def _execute_single_cc(self, cc_id: str):
        stub = changecontrol.ChangeControlServiceStub(self.channel)
        get_req = changecontrol.ChangeControlRequest(
            key=changecontrol.ChangeControlKey(id=cc_id)
        )
        cc_resp = await stub.get_one(get_req, timeout=RPC_TIMEOUT)

        config_stub = changecontrol.ChangeControlConfigServiceStub(self.channel)

        approve_req = changecontrol.ChangeControlConfigSetRequest(
            value=changecontrol.ChangeControlConfig(
                key=changecontrol.ChangeControlKey(id=cc_id),
                approve=True,
                version=cc_resp.value.change.time if hasattr(cc_resp.value, 'change') else None,
            )
        )
        await config_stub.set(approve_req, timeout=RPC_TIMEOUT)

        start_req = changecontrol.ChangeControlConfigSetRequest(
            value=changecontrol.ChangeControlConfig(
                key=changecontrol.ChangeControlKey(id=cc_id),
                start=True,
            )
        )
        await config_stub.set(start_req, timeout=RPC_TIMEOUT)

        stream_req = changecontrol.ChangeControlStreamRequest(
            partial_eq_filter=[
                changecontrol.ChangeControl(key=changecontrol.ChangeControlKey(id=cc_id))
            ]
        )
        async for res in stub.subscribe(stream_req, timeout=CC_TIMEOUT):
            status = res.value.status if hasattr(res.value, 'status') else None
            if status and status == changecontrol.ChangeControlStatus.CHANGE_CONTROL_STATUS_COMPLETED:
                return
            if status and status == changecontrol.ChangeControlStatus.CHANGE_CONTROL_STATUS_ERROR:
                raise RuntimeError(f"Change control {cc_id} failed")

    # ------------------------------------------------------------------
    # Configlets
    # ------------------------------------------------------------------

    async def get_all_configlets(self) -> list[dict]:
        self._require_ready()
        stub = configlet.ConfigletServiceStub(self.channel)
        req = configlet.ConfigletStreamRequest()
        results = []
        async for resp in stub.get_all(req, timeout=RPC_TIMEOUT):
            c = resp.value
            results.append({
                "id": c.key.configlet_id.value if c.key and c.key.configlet_id else "",
                "name": c.display_name.value if c.display_name else "",
                "size": c.size.value if c.size else 0,
            })
        return results

    async def get_configlet(self, configlet_id: str) -> Optional[dict]:
        self._require_ready()
        stub = configlet.ConfigletServiceStub(self.channel)
        req = configlet.ConfigletRequest(
            key=configlet.ConfigletKey(
                workspace_id=MAINLINE_ID,
                configlet_id=configlet_id,
            )
        )
        try:
            resp = await stub.get_one(req, timeout=RPC_TIMEOUT)
            c = resp.value
            return {
                "name": c.display_name.value if c.display_name else "",
                "body": c.body.value if c.body else "",
                "size": c.size.value if c.size else 0,
            }
        except grpc.aio.AioRpcError:
            return None

    async def sync_configlets(self, ws_id: str, configlets_data: list[dict]) -> dict:
        self._require_ready()
        stub = configlet.ConfigletConfigServiceStub(self.channel)
        counts = {"created": 0, "updated": 0, "unchanged": 0}

        existing = {}
        try:
            read_stub = configlet.ConfigletServiceStub(self.channel)
            req = configlet.ConfigletStreamRequest()
            async for resp in read_stub.get_all(req, timeout=RPC_TIMEOUT):
                c = resp.value
                cid = c.key.configlet_id.value if c.key and c.key.configlet_id else ""
                digest = c.digest.value if c.digest else ""
                existing[cid] = digest
        except Exception:
            pass

        for cfg in configlets_data:
            name = cfg["name"]
            body = cfg["body"]

            new_digest = hashlib.sha256(body.encode()).hexdigest()
            if name in existing and existing[name] == new_digest:
                counts["unchanged"] += 1
                continue

            req = configlet.ConfigletConfigSetRequest(
                value=configlet.ConfigletConfig(
                    key=configlet.ConfigletKey(
                        workspace_id=ws_id,
                        configlet_id=name,
                    ),
                    display_name=name,
                    body=body,
                )
            )
            await stub.set(req, timeout=RPC_TIMEOUT)
            if name in existing:
                counts["updated"] += 1
            else:
                counts["created"] += 1

        return counts

    # ------------------------------------------------------------------
    # Assignments
    # ------------------------------------------------------------------

    async def apply_assignments(
        self,
        ws_id: str,
        device_assignments: dict[str, list[str]],
        global_configlets: list[str],
    ):
        self._require_ready()
        stub = configlet.ConfigletAssignmentConfigServiceStub(self.channel)

        if global_configlets:
            req = configlet.ConfigletAssignmentConfigSetRequest(
                value=configlet.ConfigletAssignmentConfig(
                    key=configlet.ConfigletAssignmentKey(
                        workspace_id=ws_id,
                        configlet_assignment_id="atd-global",
                    ),
                    display_name="ATD Global Configlets",
                    configlet_ids=fmp.RepeatedString(values=global_configlets),
                    match_policy=configlet.MatchPolicy.MATCH_POLICY_MATCH_ALL,
                    child_assignment_ids=fmp.RepeatedString(
                        values=[f"atd-{hostname}" for hostname in device_assignments]
                    ),
                )
            )
            await stub.set(req, timeout=RPC_TIMEOUT)

        for hostname, configlet_ids in device_assignments.items():
            req = configlet.ConfigletAssignmentConfigSetRequest(
                value=configlet.ConfigletAssignmentConfig(
                    key=configlet.ConfigletAssignmentKey(
                        workspace_id=ws_id,
                        configlet_assignment_id=f"atd-{hostname}",
                    ),
                    display_name=f"ATD {hostname}",
                    configlet_ids=fmp.RepeatedString(values=configlet_ids),
                    query=f"hostname:{hostname}",
                )
            )
            await stub.set(req, timeout=RPC_TIMEOUT)

    async def get_assignments(self) -> dict:
        self._require_ready()
        stub = configlet.ConfigletAssignmentServiceStub(self.channel)
        req = configlet.ConfigletAssignmentStreamRequest()
        results = {}
        async for resp in stub.get_all(req, timeout=RPC_TIMEOUT):
            a = resp.value
            aid = a.key.configlet_assignment_id.value if a.key and a.key.configlet_assignment_id else ""
            results[aid] = {
                "display_name": a.display_name.value if a.display_name else "",
                "configlet_ids": list(a.configlet_ids.values) if a.configlet_ids else [],
                "query": a.query.value if a.query else "",
            }
        return results

    # ------------------------------------------------------------------
    # Tags
    # ------------------------------------------------------------------

    async def init_device_tags(self, ws_id: str, devices: dict[str, dict]) -> int:
        self._require_ready()
        tag_config_stub = tag.TagConfigServiceStub(self.channel)
        tag_assign_stub = tag.TagAssignmentConfigServiceStub(self.channel)
        count = 0

        for hostname, dev_info in devices.items():
            device_id = dev_info.get("device_id", hostname)

            tag_req = tag.TagConfigSetRequest(
                value=tag.TagConfig(
                    key=tag.TagKey(
                        workspace_id=ws_id,
                        element_type=tag.ElementType.ELEMENT_TYPE_DEVICE,
                        label="hostname",
                        value=hostname,
                    )
                )
            )
            await tag_config_stub.set(tag_req, timeout=RPC_TIMEOUT)

            assign_req = tag.TagAssignmentConfigSetRequest(
                value=tag.TagAssignmentConfig(
                    key=tag.TagAssignmentKey(
                        workspace_id=ws_id,
                        element_type=tag.ElementType.ELEMENT_TYPE_DEVICE,
                        label="hostname",
                        value=hostname,
                        device_id=device_id,
                    )
                )
            )
            await tag_assign_stub.set(assign_req, timeout=RPC_TIMEOUT)
            count += 1

        return count

    # ------------------------------------------------------------------
    # Enrollment
    # ------------------------------------------------------------------

    async def create_enrollment_token(self, duration: str = "86400s") -> str:
        self._require_ready()
        resp = requests.post(
            f"https://{self._host}/api/v1/services/admin/Enrollment/AddEnrollmentToken",
            json={"enrollmentToken": {"duration": duration}},
            headers={"Authorization": f"Bearer {self._token}"},
            verify=False,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        if "data" in data:
            return data["data"]
        return data.get("enrollmentToken", {}).get("token", "")

    async def get_enrollment_status(self) -> dict:
        devices = await self.get_inventory()
        total = len(devices)
        inactive = [name for name, dev in devices.items() if dev["streaming_status"] == "inactive"]
        return {
            "total": total,
            "active": total - len(inactive),
            "inactive": len(inactive),
            "inactive_devices": inactive,
        }

    # ------------------------------------------------------------------
    # Change Controls (for uilanding)
    # ------------------------------------------------------------------

    async def get_change_controls(self) -> dict:
        self._require_ready()
        result = {"pending": 0, "running": 0, "completed": 0, "recent": []}
        if not changecontrol:
            return result

        try:
            stub = changecontrol.ChangeControlServiceStub(self.channel)
            req = changecontrol.ChangeControlStreamRequest()
            async for resp in stub.get_all(req, timeout=RPC_TIMEOUT):
                cc = resp.value
                cc_id = _val(cc.key.id) if cc.key else ""
                status_val = str(_val(cc.status)).lower() if hasattr(cc, 'status') else ""
                status_str = "unknown"
                if "completed" in status_val:
                    status_str = "completed"
                    result["completed"] += 1
                elif "running" in status_val:
                    status_str = "running"
                    result["running"] += 1
                elif "pending" in status_val:
                    status_str = "pending"
                    result["pending"] += 1

                result["recent"].append({
                    "id": cc_id,
                    "status": status_str,
                })
            result["recent"] = result["recent"][-20:]
        except Exception as e:
            logger.warning("Failed to get change controls: %s", e)

        return result

    # ------------------------------------------------------------------
    # Studios Onboarding
    # ------------------------------------------------------------------

    async def accept_inventory_updates(self) -> dict:
        self._require_ready()
        if not studio_topology:
            raise RuntimeError("studio_topology module not available")

        async def apply_fn(ws_id):
            sync_stub = studio_topology.UpdateSyncConfigServiceStub(self.channel)
            req = studio_topology.UpdateSyncConfigSetRequest(
                value=studio_topology.UpdateSyncConfig(
                    key=workspace.WorkspaceKey(workspace_id=ws_id),
                    sync_time=datetime.now(timezone.utc),
                )
            )
            await sync_stub.set(req, timeout=RPC_TIMEOUT)

        cc_ids = await self.workspace_flow(
            "ATD Accept Inventory Updates", apply_fn, execute_cc=False
        )
        return {"status": "accepted", "cc_ids": cc_ids}

    # ------------------------------------------------------------------
    # Full workspace flow helpers
    # ------------------------------------------------------------------

    async def workspace_flow(self, display_name: str, apply_fn, *, execute_cc: bool = True):
        ws_id = await self.create_workspace(display_name)
        await apply_fn(ws_id)

        for attempt in range(MAX_SYNC_RETRIES):
            if not await self.build_workspace(ws_id):
                raise RuntimeError("Workspace build failed")

            cc_ids, submitted = await self.submit_workspace(ws_id)
            if submitted:
                if execute_cc and cc_ids:
                    await self.execute_change_controls(cc_ids)
                return cc_ids
            if attempt < MAX_SYNC_RETRIES - 1:
                logger.info("Submit requires sync, retrying (attempt %d)", attempt + 1)
                continue

        raise RuntimeError("Workspace submit failed after retries")
