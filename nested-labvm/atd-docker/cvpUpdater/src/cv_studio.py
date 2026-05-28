#!/usr/bin/env python3
"""Sync wrapper around CloudVision Studios for ATD lab provisioning.

Pushes per-device static config through CVP's built-in
Static Configuration Studio (studio_id="studio-static-configlet")
via the workspace + change-control lifecycle.

Mirrors the patterns in cloudvision-python/examples/resources/studio/studio_update.py.
"""

import asyncio
import json
import logging
import uuid

import requests
import urllib3

from cloudvision.api import client as cv_client
from cloudvision.api import fmp
from cloudvision.api.arista.changecontrol import v1 as changecontrol
from cloudvision.api.arista.configlet import v1 as configlet
from cloudvision.api.arista.studio import v1 as studio
from cloudvision.api.arista.workspace import v1 as workspace

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

STATIC_CONFIG_STUDIO_ID = "studio-static-configlet"
INPUT_PATH_ROOTS = ["configletAssignmentRoots"]
BASE_CFGS = ["ATD-INFRA"]
ATD_ASSIGNMENT_PREFIX = "atd-lab-"

RPC_TIMEOUT = 30
BUILD_TIMEOUT = 600
CC_EXECUTION_TIMEOUT = 900


def _get_session_token(host, username, password, insecure=True):
    r = requests.post(
        f"https://{host}/cvpservice/login/authenticate.do",
        auth=(username, password),
        verify=not insecure,
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["sessionId"]


class CVStudiosClient:
    def __init__(self, host, username, password, cert_path=None, insecure=True, dry_run=False):
        self._host = host
        self._username = username
        self._password = password
        self._cert_path = cert_path
        self._insecure = insecure
        self._dry_run = dry_run
        self._token = None
        self._grpc_host = host.split(":")[0]
        self._grpc_port = int(host.split(":")[1]) if ":" in host else 443

    def connect(self):
        self._token = _get_session_token(
            self._host, self._username, self._password, self._insecure
        )

    def close(self):
        self._token = None

    def _channel(self):
        if not self._token:
            raise RuntimeError("connect() must be called before issuing requests")
        return cv_client.AsyncCVClient.from_token(
            token=self._token,
            host=self._grpc_host,
            port=self._grpc_port,
            cacert=self._cert_path,
            insecure=self._insecure,
        )

    def push_configlets(self, name_to_body, label="atd-bootstrap"):
        """Push a dict of {configlet_name: eos_config_text} as Configlet resources."""
        asyncio.run(self._push_configlets_async(name_to_body, label))

    def apply_lab(self, per_device_configlets, hostname_to_device_id, label):
        """Update one ConfigletAssignment per device to the given configlet list.

        per_device_configlets: {hostname: [configlet_name, ...]}
        hostname_to_device_id: {hostname: cvp_device_id (serial/macAddress)}
        BASE_CFGS is prepended to each device's list, matching legacy 'preserve ATD-INFRA' behavior.
        """
        asyncio.run(
            self._apply_lab_async(per_device_configlets, hostname_to_device_id, label)
        )

    async def _create_workspace(self, channel, name):
        ws_id = str(uuid.uuid4())
        req = workspace.WorkspaceConfigSetRequest(
            value=workspace.WorkspaceConfig(
                key=workspace.WorkspaceKey(workspace_id=ws_id),
                display_name=name,
            )
        )
        await workspace.WorkspaceConfigServiceStub(channel).set(req, timeout=RPC_TIMEOUT)
        logger.info("workspace created: %s (%s)", ws_id, name)
        return ws_id

    async def _build(self, channel, ws_id):
        build_id = str(uuid.uuid4())
        req = workspace.WorkspaceConfigSetRequest(
            value=workspace.WorkspaceConfig(
                key=workspace.WorkspaceKey(workspace_id=ws_id),
                request=workspace.Request.START_BUILD,
                request_params=workspace.RequestParams(request_id=build_id),
            )
        )
        await workspace.WorkspaceConfigServiceStub(channel).set(req, timeout=RPC_TIMEOUT)
        sub = workspace.WorkspaceStreamRequest(
            partial_eq_filter=[
                workspace.Workspace(key=workspace.WorkspaceKey(workspace_id=ws_id))
            ]
        )
        async for res in workspace.WorkspaceServiceStub(channel).subscribe(
            sub, timeout=BUILD_TIMEOUT
        ):
            if build_id in res.value.responses.values:
                br = res.value.responses.values[build_id]
                if br.status == workspace.ResponseStatus.SUCCESS:
                    logger.info("workspace %s build succeeded", ws_id)
                    return
                raise RuntimeError(
                    f"workspace {ws_id} build failed: {br.message}"
                )
        raise RuntimeError(f"workspace {ws_id} build timed out")

    async def _submit(self, channel, ws_id):
        submit_id = str(uuid.uuid4())
        req = workspace.WorkspaceConfigSetRequest(
            value=workspace.WorkspaceConfig(
                key=workspace.WorkspaceKey(workspace_id=ws_id),
                request=workspace.Request.SUBMIT,
                request_params=workspace.RequestParams(request_id=submit_id),
            )
        )
        await workspace.WorkspaceConfigServiceStub(channel).set(req, timeout=RPC_TIMEOUT)
        sub = workspace.WorkspaceStreamRequest(
            partial_eq_filter=[
                workspace.Workspace(key=workspace.WorkspaceKey(workspace_id=ws_id))
            ]
        )
        async for res in workspace.WorkspaceServiceStub(channel).subscribe(
            sub, timeout=RPC_TIMEOUT
        ):
            if submit_id in res.value.responses.values:
                sr = res.value.responses.values[submit_id]
                if sr.status == workspace.ResponseStatus.FAIL:
                    raise RuntimeError(
                        f"workspace {ws_id} submit failed: {sr.message}"
                    )
            if res.value.state == workspace.WorkspaceState.SUBMITTED:
                cc_ids = list(res.value.cc_ids.values)
                logger.info("workspace %s submitted; cc_ids=%s", ws_id, cc_ids)
                return cc_ids
        raise RuntimeError(f"workspace {ws_id} submit timed out")

    async def _run_cc(self, channel, cc_id):
        key = changecontrol.ChangeControlKey(id=cc_id)
        cc_stub = changecontrol.ChangeControlServiceStub(channel)
        approve_stub = changecontrol.ApproveConfigServiceStub(channel)
        cfg_stub = changecontrol.ChangeControlConfigServiceStub(channel)
        current = await cc_stub.get_one(changecontrol.ChangeControlRequest(key=key))
        await approve_stub.set(
            changecontrol.ApproveConfigSetRequest(
                value=changecontrol.ApproveConfig(
                    key=key,
                    approve=changecontrol.FlagConfig(value=True),
                    version=current.time,
                )
            )
        )
        await cfg_stub.set(
            changecontrol.ChangeControlConfigSetRequest(
                value=changecontrol.ChangeControlConfig(
                    key=key, start=changecontrol.FlagConfig(value=True)
                )
            )
        )
        sub = changecontrol.ChangeControlStreamRequest(
            partial_eq_filter=[changecontrol.ChangeControl(key=key)]
        )
        async for res in cc_stub.subscribe(sub, timeout=CC_EXECUTION_TIMEOUT):
            if res.value.status == changecontrol.ChangeControlStatus.COMPLETED:
                if res.value.error:
                    raise RuntimeError(
                        f"change control {cc_id} failed: {res.value.error}"
                    )
                logger.info("change control %s completed", cc_id)
                return
        raise RuntimeError(f"change control {cc_id} timed out")

    async def _set_configlet(self, channel, ws_id, configlet_id, body):
        req = configlet.ConfigletConfigSetRequest(
            value=configlet.ConfigletConfig(
                key=configlet.ConfigletKey(
                    workspace_id=ws_id, configlet_id=configlet_id
                ),
                display_name=configlet_id,
                body=body,
            )
        )
        await configlet.ConfigletConfigServiceStub(channel).set(req, timeout=RPC_TIMEOUT)

    async def _set_assignment(
        self, channel, ws_id, assignment_id, display_name, configlet_ids, query
    ):
        req = configlet.ConfigletAssignmentConfigSetRequest(
            value=configlet.ConfigletAssignmentConfig(
                key=configlet.ConfigletAssignmentKey(
                    workspace_id=ws_id,
                    configlet_assignment_id=assignment_id,
                ),
                display_name=display_name,
                configlet_ids=fmp.RepeatedString(values=configlet_ids),
                query=query,
                match_policy=configlet.MatchPolicy.MATCH_ALL,
            )
        )
        await configlet.ConfigletAssignmentConfigServiceStub(channel).set(
            req, timeout=RPC_TIMEOUT
        )

    async def _get_studio_roots(self, channel):
        """Read the current mainline value of configletAssignmentRoots, or [] if unset."""
        key = studio.InputsKey(studio_id=STATIC_CONFIG_STUDIO_ID, workspace_id="")
        req = studio.InputsStreamRequest()
        req.partial_eq_filter.append(studio.Inputs(key=key))
        stub = studio.InputsServiceStub(channel)
        roots = []
        async for resp in stub.get_all(req, timeout=RPC_TIMEOUT):
            if list(resp.value.key.path.values) == INPUT_PATH_ROOTS:
                try:
                    val = json.loads(resp.value.inputs)
                    if isinstance(val, list):
                        roots = val
                except (ValueError, TypeError):
                    pass
        return roots

    async def _set_studio_roots(self, channel, ws_id, atd_assignment_ids):
        existing = await self._get_studio_roots(channel)
        preserved = [a for a in existing if not a.startswith(ATD_ASSIGNMENT_PREFIX)]
        merged = list(atd_assignment_ids) + preserved
        req = studio.InputsConfigSetRequest(
            value=studio.InputsConfig(
                key=studio.InputsKey(
                    workspace_id=ws_id,
                    studio_id=STATIC_CONFIG_STUDIO_ID,
                    path=fmp.RepeatedString(values=INPUT_PATH_ROOTS),
                ),
                inputs=json.dumps(merged),
            )
        )
        await studio.InputsConfigServiceStub(channel).set(req, timeout=RPC_TIMEOUT)

    async def _push_configlets_async(self, name_to_body, label):
        with self._channel() as channel:
            ws_id = await self._create_workspace(channel, f"{label} configlet import")
            for name, body in name_to_body.items():
                await self._set_configlet(channel, ws_id, name, body)
            await self._build(channel, ws_id)
            if self._dry_run:
                logger.warning("dry-run: workspace %s built but not submitted", ws_id)
                return
            cc_ids = await self._submit(channel, ws_id)
            for cc in cc_ids:
                await self._run_cc(channel, cc)

    async def _apply_lab_async(self, per_device_configlets, hostname_to_device_id, label):
        with self._channel() as channel:
            ws_id = await self._create_workspace(channel, f"atd lab {label}")
            atd_assignment_ids = []
            for hostname, cfg_list in per_device_configlets.items():
                dev_id = hostname_to_device_id.get(hostname)
                if not dev_id:
                    logger.warning(
                        "device %s not in CVP inventory; skipping", hostname
                    )
                    continue
                assignment_id = f"{ATD_ASSIGNMENT_PREFIX}{hostname}"
                full_cfg_list = BASE_CFGS + list(cfg_list)
                await self._set_assignment(
                    channel,
                    ws_id,
                    assignment_id=assignment_id,
                    display_name=f"ATD-{hostname}",
                    configlet_ids=full_cfg_list,
                    query=f"device:{dev_id}",
                )
                atd_assignment_ids.append(assignment_id)
            await self._set_studio_roots(channel, ws_id, atd_assignment_ids)
            await self._build(channel, ws_id)
            if self._dry_run:
                logger.warning("dry-run: workspace %s built but not submitted", ws_id)
                return
            cc_ids = await self._submit(channel, ws_id)
            for cc in cc_ids:
                await self._run_cc(channel, cc)
