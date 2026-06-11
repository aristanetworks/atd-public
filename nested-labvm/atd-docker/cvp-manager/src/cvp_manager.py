#!/usr/bin/env python

import os
import time
import logging
from os import path, listdir

from ruamel.yaml import YAML
from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient

from proxy_client import ProxyClient

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("cvp_manager")

TOPO_FILE = "/etc/atd/ACCESS_INFO.yaml"
CVP_CONFIG_FILE = path.expanduser("~/CVP_DATA/.cvpState.txt")
CVP_INFO_FILE = "/home/arista/cvp/cvp_info.yaml"
REPO_PATH = "/opt/atd/"
REPO_TOPO = REPO_PATH + "topologies/"
SLEEP_DELAY = 30
PROXY_URL = os.environ.get("CVP_PROXY_URL", "http://atd-cvp-proxy:8880")


def pS(mstat, mtype):
    logger.info("[%s] %s", mstat, mtype)


def load_yaml(yaml_file):
    with open(yaml_file, "r") as f:
        return YAML().load(f)


def wait_for_file(filepath, description, max_retries=10):
    retries = 0
    while True:
        if path.exists(filepath):
            pS("OK", f"{description} is available.")
            return
        if retries >= max_retries:
            raise SystemExit(f"{description} timer expired")
        retries += 1
        pS("INFO", f"{description} not available...Waiting {SLEEP_DELAY}s")
        time.sleep(SLEEP_DELAY)


def get_managed_nodes(build_yaml, eos_type):
    nodes = []
    if eos_type == "ceos":
        for node in build_yaml["nodes"]:
            if node.get("cv_manage", False):
                nodes.append(node)
    else:
        nodes = build_yaml["nodes"]
    return nodes


def get_device_ip(nodes, device_name, eos_type):
    for node in nodes:
        if eos_type == "ceos":
            if node["name"] == device_name:
                return node["ip_addr"]
        else:
            devn = list(node.keys())[0]
            if devn == device_name:
                return node[devn]["ip_addr"]
    return None


def scp_token_to_device(device_ip, token_path, username, password):
    with SSHClient() as ssh:
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(device_ip, username=username, password=password)
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(token_path, "/tmp/token")


def check_and_fix_streaming(proxy, nodes, eos_type, username, password):
    status = proxy.get_enrollment_status()

    if not status["inactive_devices"]:
        pS("OK", "All devices actively streaming to CVP")
        return

    inactive_count = len(status["inactive_devices"])
    pS("INFO", f"{inactive_count} devices not streaming — re-enrolling")

    token_data = proxy.create_enrollment_token(duration="86400s")

    token_path = path.expanduser("~/token")
    with open(token_path, "w") as f:
        f.write(token_data["token"])

    for device_name in status["inactive_devices"]:
        device_ip = get_device_ip(nodes, device_name, eos_type)
        if device_ip:
            try:
                scp_token_to_device(device_ip, token_path, username, password)
                pS("INFO", f"Re-enrolled {device_name} at {device_ip}")
            except Exception as e:
                pS("ERROR", f"Failed to SCP token to {device_name}: {e}")
        else:
            pS("WARNING", f"No IP found for inactive device {device_name}")

    pS("INFO", "Waiting for devices to resume streaming...")
    max_wait = 180
    elapsed = 0
    while elapsed < max_wait:
        status = proxy.get_enrollment_status()
        if not status["inactive_devices"]:
            pS("OK", "All devices now actively streaming")
            return
        remaining = len(status["inactive_devices"])
        pS("INFO", f"Still waiting on {remaining} devices... ({elapsed}s)")
        time.sleep(15)
        elapsed += 15

    pS("WARNING", f"Timed out waiting for: {status['inactive_devices']}")


def distribute_enrollment_token(proxy, nodes, eos_type, username, password):
    pS("INFO", "Generating enrollment token for device onboarding...")
    token_data = proxy.create_enrollment_token(duration="86400s")

    token_path = path.expanduser("~/token")
    with open(token_path, "w") as f:
        f.write(token_data["token"])

    for node in nodes:
        if eos_type == "ceos":
            devn = node["name"]
            dev_ip = node["ip_addr"]
        else:
            devn = list(node.keys())[0]
            dev_ip = node[devn]["ip_addr"]

        try:
            scp_token_to_device(dev_ip, token_path, username, password)
            pS("INFO", f"Token sent to {devn} at {dev_ip}")
        except Exception as e:
            pS("ERROR", f"Failed to SCP token to {devn}: {e}")


def read_configlets(configlet_dir):
    configlets = []
    if not path.exists(configlet_dir):
        pS("INFO", "No configlet directory found")
        return configlets

    for filename in listdir(configlet_dir):
        if filename.endswith(".py") or filename.endswith(".form"):
            continue
        if filename.lower() == "readme.md":
            continue
        filepath = path.join(configlet_dir, filename)
        if path.isfile(filepath):
            with open(filepath, "r") as f:
                configlets.append({"name": filename, "body": f.read()})
    return configlets


def build_initial_assignments(cvp_yaml):
    device_assignments = {}
    global_configlets = []

    configlets_section = cvp_yaml["cvp_info"]["configlets"]

    if "containers" in configlets_section:
        for container, cfgs in configlets_section["containers"].items():
            if cfgs:
                global_configlets.extend(cfgs)

    if "netelements" in configlets_section:
        for device, cfgs in configlets_section["netelements"].items():
            if cfgs:
                device_assignments[device] = cfgs

    return device_assignments, global_configlets


def main():
    proxy = ProxyClient(PROXY_URL)

    pS("OK", "Starting CVP Manager...")

    wait_for_file(TOPO_FILE, "ACCESS_INFO")
    atd_yaml = load_yaml(TOPO_FILE)

    if "cvp_mode" in atd_yaml and atd_yaml["cvp_mode"] == "bare":
        pS("INFO", "CVP is in bare configuration mode, nothing to do.")
        return

    eos_type = atd_yaml.get("eos_type", "ceos")
    topo_filename = "ceos_build.yml" if eos_type == "ceos" else "topo_build.yml"
    topology = atd_yaml["topology"]
    build_file = f"{REPO_TOPO}{topology}/{topo_filename}"

    wait_for_file(build_file, f"Build file ({topo_filename})")
    build_yaml = load_yaml(build_file)

    nodes = get_managed_nodes(build_yaml, eos_type)
    username = atd_yaml["login_info"]["jump_host"]["user"]
    password = atd_yaml["login_info"]["jump_host"]["pw"]

    configlet_dir = f"/opt/atd/topologies/{topology}/configlets/"

    proxy.wait_for_cvp()

    check_and_fix_streaming(proxy, nodes, eos_type, username, password)

    is_first_boot = not path.exists(CVP_CONFIG_FILE)

    if is_first_boot:
        pS("OK", "Initial ATD topology boot")
        distribute_enrollment_token(proxy, nodes, eos_type, username, password)

        pS("INFO", f"Waiting for {len(nodes)} devices to register...")
        proxy.wait_for_devices(len(nodes), timeout=600)
        pS("OK", f"All {len(nodes)} devices registered")

    pS("INFO", "Reading configlets from disk...")
    configlets = read_configlets(configlet_dir)
    if configlets:
        pS("INFO", f"Syncing {len(configlets)} configlets to CVP...")
        result = proxy.sync_configlets(configlets)
        pS(
            "OK",
            f"Configlet sync: {result.get('created', 0)} created, "
            f"{result.get('updated', 0)} updated, "
            f"{result.get('unchanged', 0)} unchanged",
        )
    else:
        pS("INFO", "No configlets to sync")

    if is_first_boot:
        pS("INFO", "Initializing device tags...")
        tag_result = proxy.init_tags()
        pS("OK", f"Created {tag_result.get('tags_created', 0)} device tags")

        if path.exists(CVP_INFO_FILE):
            cvp_yaml = load_yaml(CVP_INFO_FILE)
            device_assignments, global_configlets = build_initial_assignments(cvp_yaml)
            if device_assignments:
                pS("INFO", f"Applying initial assignments for {len(device_assignments)} devices...")
                result = proxy.apply_assignments(device_assignments, global_configlets)
                pS("OK", f"Assignments applied: {result.get('devices_updated', 0)} devices")

        os.makedirs(path.dirname(CVP_CONFIG_FILE), exist_ok=True)
        with open(CVP_CONFIG_FILE, "w") as tf:
            tf.write("CVP_CONFIGURED\n")
        pS("OK", "Completed initial CVP configuration")
    else:
        pS("OK", "Configlet sync complete (CVP already configured)")


if __name__ == "__main__":
    pS("OK", "Starting...")
    main()
    pS("OK", "Entering idle loop")
    while True:
        time.sleep(600)
