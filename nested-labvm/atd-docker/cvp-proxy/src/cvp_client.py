import asyncio
import hashlib
import json
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

try:
    from cloudvision.api.arista.studio import v1 as studio
except ImportError:
    studio = None

try:
    from cloudvision.api.fmp import RepeatedString as _RepeatedString
except ImportError:
    try:
        from fmp.wrappers import RepeatedString as _RepeatedString
    except ImportError:
        from fmp.wrappers_pb2 import RepeatedString as _RepeatedString

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
            self.cvp_version = self._get_version(host, token)
            self._cv_client = cv_client.AsyncCVClient.from_token(
                token=token, host=host, port=443, insecure=True
            )
            self.channel = self._cv_client.__enter__()
            await self._probe()
            self.status = CvpStatus.READY
            logger.info("Connected to CVP at %s (v%s)", host, self.cvp_version or "unknown")
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

    def _get_version(self, host: str, token: str) -> Optional[str]:
        try:
            resp = requests.get(
                f"https://{host}/cvpservice/cvpInfo/getCvpInfo.do",
                cookies={"access_token": token},
                verify=False,
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json().get("version")
        except Exception:
            return None

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
                raw = dev.streaming_status
                name = getattr(raw, "name", str(raw)).lower()
                if "active" in name and "inactive" not in name:
                    streaming = "active"
                elif "inactive" in name:
                    streaming = "inactive"
                else:
                    streaming = "unknown"
                if not devices:
                    logger.info("streaming_status: raw=%r, name=%s -> %s", raw, name, streaming)
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
            active = {k: v for k, v in devices.items() if v["streaming_status"] == "active"}
            total = len(devices)
            streaming = len(active)
            if streaming >= count:
                logger.info("All %d devices actively streaming", streaming)
                return devices
            logger.info(
                "Waiting for devices: %d/%d streaming, %d in inventory (%ds/%ds)",
                streaming, count, total, elapsed, timeout,
            )
            await asyncio.sleep(15)
            elapsed += 15
        devices = await self.get_inventory()
        active = {k: v for k, v in devices.items() if v["streaming_status"] == "active"}
        not_streaming = [k for k, v in devices.items() if v["streaming_status"] != "active"]
        logger.warning(
            "Timed out waiting for devices: %d/%d streaming. Not streaming: %s",
            len(active), count, not_streaming,
        )
        return devices

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

    async def abandon_workspace(self, ws_id: str):
        stub = workspace.WorkspaceConfigServiceStub(self.channel)
        req = workspace.WorkspaceConfigSetRequest(
            value=workspace.WorkspaceConfig(
                key=workspace.WorkspaceKey(workspace_id=ws_id),
                request=workspace.Request.ABANDON,
            )
        )
        await stub.set(req, timeout=RPC_TIMEOUT)
        logger.info("Abandoned workspace %s", ws_id)

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
                msg = _val(build_res.message, "")
                logger.info(
                    "Build response: status=%s message=%r",
                    build_res.status, msg[:500] if msg else "",
                )
                ws = res.value
                for attr in ("state", "last_build_state", "needs_build"):
                    if hasattr(ws, attr):
                        logger.info("  workspace.%s = %r", attr, getattr(ws, attr))
                if build_res.status == workspace.ResponseStatus.SUCCESS:
                    return True
                elif build_res.status == workspace.ResponseStatus.FAIL:
                    logger.error("Build failed: %s", msg)
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
                "id": _val(c.key.configlet_id) if c.key else "",
                "name": _val(c.display_name),
                "size": _val(c.size, 0),
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
                "name": _val(c.display_name),
                "body": _val(c.body),
                "size": _val(c.size, 0),
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
                cid = _val(c.key.configlet_id) if c.key else ""
                digest = _val(c.digest)
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
            await self._ws_set_with_retry(stub, req)
            if name in existing:
                counts["updated"] += 1
            else:
                counts["created"] += 1

        return counts

    # ------------------------------------------------------------------
    # Assignments
    # ------------------------------------------------------------------

    async def _ws_set_with_retry(self, stub, req, max_attempts=15):
        for attempt in range(max_attempts):
            try:
                await stub.set(req, timeout=RPC_TIMEOUT)
                return
            except Exception as e:
                if "workspace status is not available" in str(e) and attempt < max_attempts - 1:
                    logger.info("Workspace not ready, retrying... (%ds)", attempt + 1)
                    await asyncio.sleep(1)
                else:
                    raise

    async def apply_assignments(
        self,
        ws_id: str,
        device_assignments: dict[str, list[str]],
        global_configlets: list[str],
    ) -> str:
        self._require_ready()
        stub = configlet.ConfigletAssignmentConfigServiceStub(self.channel)

        try:
            existing = await self.get_assignments()
            for aid, info in existing.items():
                display = info.get("display_name", "")
                if aid.startswith("atd-") or display.startswith("ATD "):
                    logger.info("Removing stale assignment %s (%s)", aid, display)
                    del_req = configlet.ConfigletAssignmentConfigDeleteRequest(
                        key=configlet.ConfigletAssignmentKey(
                            workspace_id=ws_id,
                            configlet_assignment_id=aid,
                        )
                    )
                    try:
                        await stub.delete(del_req, timeout=RPC_TIMEOUT)
                    except Exception as e:
                        logger.warning("Failed to delete assignment %s: %s", aid, e)
        except Exception as e:
            logger.warning("Failed to clean existing assignments: %s", e)

        parent_id = str(uuid.uuid4())
        child_ids = []

        for hostname, configlet_ids in device_assignments.items():
            aid = str(uuid.uuid4())
            child_ids.append(aid)
            query = f"device:{hostname}"
            logger.info("Assignment %s -> query=%s, configlets=%s", hostname, query, configlet_ids)
            req = configlet.ConfigletAssignmentConfigSetRequest(
                value=configlet.ConfigletAssignmentConfig(
                    key=configlet.ConfigletAssignmentKey(
                        workspace_id=ws_id,
                        configlet_assignment_id=aid,
                    ),
                    display_name=f"ATD {hostname}",
                    configlet_ids=_RepeatedString(values=configlet_ids),
                    query=query,
                    match_policy=configlet.MatchPolicy.MATCH_FIRST,
                )
            )
            await self._ws_set_with_retry(stub, req)

        parent_req = configlet.ConfigletAssignmentConfigSetRequest(
            value=configlet.ConfigletAssignmentConfig(
                key=configlet.ConfigletAssignmentKey(
                    workspace_id=ws_id,
                    configlet_assignment_id=parent_id,
                ),
                display_name="ATD Assignments",
                configlet_ids=_RepeatedString(values=global_configlets) if global_configlets else _RepeatedString(values=[]),
                query="device:*",
                match_policy=configlet.MatchPolicy.MATCH_FIRST,
                child_assignment_ids=_RepeatedString(values=child_ids),
            )
        )
        await self._ws_set_with_retry(stub, parent_req)
        logger.info("Created root assignment %s with %d children", parent_id, len(child_ids))

        await self._set_studio_assignment_roots(ws_id, [parent_id])

        return parent_id

    async def _set_studio_assignment_roots(self, ws_id: str, root_ids: list[str]):
        if not studio:
            logger.warning("studio.v1 module not available, cannot set assignment roots")
            return
        stub = studio.InputsConfigServiceStub(self.channel)
        roots_json = json.dumps(root_ids)
        req = studio.InputsConfigSetRequest(
            value=studio.InputsConfig(
                key=studio.InputsKey(
                    studio_id="studio-static-configlet",
                    workspace_id=ws_id,
                    path="configletAssignmentRoots",
                ),
                inputs=roots_json.encode("utf-8"),
            )
        )
        await self._ws_set_with_retry(stub, req)
        logger.info("Set studio configletAssignmentRoots=%s in workspace %s", roots_json, ws_id)

    async def get_assignments(self) -> dict:
        self._require_ready()
        stub = configlet.ConfigletAssignmentServiceStub(self.channel)
        req = configlet.ConfigletAssignmentStreamRequest()
        results = {}
        async for resp in stub.get_all(req, timeout=RPC_TIMEOUT):
            a = resp.value
            aid = _val(a.key.configlet_assignment_id) if a.key else ""
            child_ids = list(a.child_assignment_ids.values) if a.child_assignment_ids else []
            mp = getattr(a, "match_policy", None)
            mp_str = str(mp) if mp is not None else "unset"
            results[aid] = {
                "display_name": _val(a.display_name),
                "configlet_ids": list(a.configlet_ids.values) if a.configlet_ids else [],
                "query": _val(a.query),
                "child_assignment_ids": child_ids,
                "match_policy": mp_str,
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
                        element_type=getattr(tag.ElementType, "ELEMENT_TYPE_DEVICE", getattr(tag.ElementType, "DEVICE", 1)),
                        label="hostname",
                        value=hostname,
                    )
                )
            )
            await self._ws_set_with_retry(tag_config_stub, tag_req)

            assign_req = tag.TagAssignmentConfigSetRequest(
                value=tag.TagAssignmentConfig(
                    key=tag.TagAssignmentKey(
                        workspace_id=ws_id,
                        element_type=getattr(tag.ElementType, "ELEMENT_TYPE_DEVICE", getattr(tag.ElementType, "DEVICE", 1)),
                        label="hostname",
                        value=hostname,
                        device_id=device_id,
                    )
                )
            )
            await self._ws_set_with_retry(tag_assign_stub, assign_req)
            count += 1

        return count

    async def get_device_tags(self, device_id: str = None) -> dict:
        self._require_ready()
        stub = tag.TagAssignmentServiceStub(self.channel)
        req = tag.TagAssignmentStreamRequest()
        tags = {}
        async for resp in stub.get_all(req, timeout=RPC_TIMEOUT):
            a = resp.value
            if a.key:
                did = _val(a.key.device_id)
                if device_id and did != device_id:
                    continue
                label = _val(a.key.label)
                value = _val(a.key.value)
                if did not in tags:
                    tags[did] = {}
                tags[did][label] = value
        return tags

    # ------------------------------------------------------------------
    # Enrollment
    # ------------------------------------------------------------------

    async def create_enrollment_token(self, duration: str = "86400s") -> str:
        self._require_ready()
        url = f"https://{self._host}/api/v1/services/admin/Enrollment/AddEnrollmentToken"
        payload = {"enrollmentToken": {"duration": duration}}
        try:
            resp = requests.post(
                url,
                json=payload,
                cookies={"access_token": self._token},
                verify=False,
                timeout=30,
            )
            resp.raise_for_status()
        except requests.HTTPError as e:
            logger.error(
                "Enrollment token request failed (%s): %s",
                resp.status_code, resp.text[:500],
            )
            raise
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
            for attempt in range(15):
                try:
                    await sync_stub.set(req, timeout=RPC_TIMEOUT)
                    logger.info("Accepted all inventory updates in workspace %s", ws_id)
                    return
                except Exception as e:
                    if attempt < 14:
                        logger.info("Waiting for workspace to initialize in Studios... (%ds)", attempt + 1)
                        await asyncio.sleep(1)
                    else:
                        raise

        cc_ids = await self.workspace_flow(
            "ATD Accept Inventory Updates", apply_fn, execute_cc=True
        )
        return {"status": "accepted", "cc_ids": cc_ids}

    # ------------------------------------------------------------------
    # Full workspace flow helpers
    # ------------------------------------------------------------------

    async def workspace_flow(self, display_name: str, apply_fn, *, execute_cc: bool = True):
        ws_id = await self.create_workspace(display_name)
        logger.info("[%s] Created workspace %s", display_name, ws_id)
        await apply_fn(ws_id)

        for attempt in range(MAX_SYNC_RETRIES):
            if not await self.build_workspace(ws_id):
                raise RuntimeError("Workspace build failed")
            logger.info("[%s] Workspace built", display_name)

            cc_ids, submitted = await self.submit_workspace(ws_id)
            logger.info("[%s] submitted=%s, cc_ids=%s", display_name, submitted, cc_ids)
            if submitted:
                if execute_cc and cc_ids:
                    logger.info("[%s] Executing %d change controls", display_name, len(cc_ids))
                    await self.execute_change_controls(cc_ids)
                    logger.info("[%s] Change controls executed", display_name)
                elif not cc_ids:
                    logger.warning("[%s] No change controls generated", display_name)
                return cc_ids
            if attempt < MAX_SYNC_RETRIES - 1:
                logger.info("Submit requires sync, retrying (attempt %d)", attempt + 1)
                continue

        raise RuntimeError("Workspace submit failed after retries")
