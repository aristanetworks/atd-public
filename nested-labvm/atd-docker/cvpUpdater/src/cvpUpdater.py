#!/usr/bin/env python

import os

from cvprac.cvp_client import CvpClient
from ruamel.yaml import YAML
from rcvpapi.rcvpapi import *
from paramiko import SSHClient
from paramiko import AutoAddPolicy
from scp import SCPClient
from os import path, listdir, system
from sys import exit
from time import sleep
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from cv_studio import CVStudiosClient

topo_file = '/etc/atd/ACCESS_INFO.yaml'
CVP_CONFIG_FIILE = path.expanduser('~/CVP_DATA/.cvpState.txt')
REPO_PATH = '/opt/atd/'
REPO_TOPO = REPO_PATH + 'topologies/'
CVP_CONTAINERS = []
sleep_delay = 30

# Temporary file_path location for CVP Custom info
cvp_file = '/home/arista/cvp/cvp_info.yaml'


# ==================================
# Start of Global Functions
# ==================================
def getTopoInfo(yaml_file):
    """
    Function that parses the supplied YAML file to build the CVP topology.
    """
    topoInfo = open(yaml_file,'r')
    topoYaml = YAML().load(topoInfo)
    topoInfo.close()
    return(topoYaml)

def checkContainer(cnt):
    """
    Function to check and see if the supplied container is already in the global container list.
    Parameters:
    cnt = Container to add if it does not exist in the list (required)
    """
    if cnt not in CVP_CONTAINERS:
        CVP_CONTAINERS.append(cnt)

def getEosDevice(topo,eosYaml,cvpMapper,topoType):
    """
    Function that Parses through the YAML file and creates a CVPSWITCH class object for each EOS device in the topo file.
    Parameters:
    topo = Topology for the ATD (required)
    eosYAML = vEOS portion of the ACCESS_INFO.yaml file (required)
    cvpMapper = Dict that maps EOS device to container (required)
    """
    EOS_DEV = []
    for dev in eosYaml:
        if topoType == "ceos":
            try:
                EOS_DEV.append(CVPSWITCH(dev["name"], dev["ip_addr"], cvpMapper[dev["name"]]))
                checkContainer(cvpMapper[dev])
            except:
                EOS_DEV.append(CVPSWITCH(dev["name"],dev["ip_addr"]))
        else:
            devn = list(dev.keys())[0]
            try:
                EOS_DEV.append(CVPSWITCH(devn,dev[devn]['ip_addr'],cvpMapper[devn]))
                checkContainer(cvpMapper[dev])
            except:
                EOS_DEV.append(CVPSWITCH(devn,dev[devn]['ip_addr']))
    return(EOS_DEV)

def eosDeviceMapper(eos_type, eos_yaml):
    """
    Function that parses the topology yaml file and makes a mapper object to be used later.
    Parameters:
    eos_type = EOS topology type (ceos/veos) string (required)
    eos_yaml = Topology yaml file (required)
    """
    EOS_DEV = {}
    for dev in eos_yaml:
        if eos_type == "ceos":
            devn = dev["name"]
            EOS_DEV[devn] = dev
        else:
            devn = list(dev.keys())[0]
            _ip_addr = dev[devn]['ip_addr']
            EOS_DEV[_ip_addr] = devn
    return(EOS_DEV)

def eosContainerMapper(cvpYaml):
    """
    Function that Parses through the YAML file and maps device to container.
    Parameters:
    cvpYaml = cvp containers portion of the cvp_info.yaml file (required)
    """
    eMap = {}
    for cnt in cvpYaml.keys():
        if cvpYaml[cnt]['nodes']:
            for eosD in cvpYaml[cnt]['nodes']:
                eMap[eosD] = cnt
    return(eMap)

def pS(mstat,mtype):
    """
    Function to send output from service file to Syslog
    Parameters:
    mstat = Message Status, ie "OK", "INFO" (required)
    mtype = Message to be sent/displayed (required)
    """
    mmes = "\t" + mtype
    print("[{0}] {1}".format(mstat,mmes.expandtabs(7 - len(mstat))))

# ============================================
# CVP Utility Functions
# ============================================

def checkConnected(cvp_clnt, NODES, eos_type):
    """
    Function to check if all nodes have connected and
    are reachable via ping
    Parameters:
    cvp_clnt = CVP rCVPAPI client (object)
    NODES = EOS Node yaml (dict)
    """
    cvp_inventory = cvp_clnt.api.get_inventory()
    tmp_device_count = len(cvp_inventory)
    while len(NODES) > tmp_device_count:
        pS("INFO", f"Only {tmp_device_count} out of {len(NODES)} nodes have registered to CVP. Sleeping {sleep_delay} seconds.")
        sleep(sleep_delay)
        cvp_inventory = cvp_clnt.api.get_inventory()
        tmp_device_count = len(cvp_inventory)
    pS("OK", f"All {tmp_device_count} out of {len(NODES)} nodes have registered to CVP.")
    return(True)


def loadStaticConfiglets(cfg_dir):
    """
    Load all static configlet files from cfg_dir into a {name: body} dict
    for push into the Static Configuration Studio via CVStudiosClient.
    .py (configlet builders) and .form files are no longer supported under
    Studios and are skipped.
    """
    if not path.exists(cfg_dir):
        pS("INFO", "No Configlet directory found")
        return {}
    pS("OK", "Configlet directory exists")
    out = {}
    for name in listdir(cfg_dir):
        if name.endswith(".py") or name.endswith(".form"):
            continue
        with open(cfg_dir + name, "r") as f:
            out[name] = f.read()
        pS("INFO", f"Loaded static configlet: {name}")
    pS("INFO", f"Loaded {len(out)} static configlets from {cfg_dir}")
    return out



def main():
    """
    Main Function if this is the initial deployment for the ATD/CVP
    """
    cvp_clnt = ""
    file_counter = 0
    containers = {}
    NODES = []
    while True:
        if path.exists(topo_file):
            pS("OK", "ACCESS_INFO file is available.")
            break
        else:
            if file_counter >= 10:
                exit('Access INFO timer expired')
            else:
                file_counter += 1
                pS("ERROR", f"ACCESS_INFO file is not available...Waiting for {sleep_delay} seconds")
                sleep(sleep_delay)
    atd_yaml = getTopoInfo(topo_file)
    cvp_yaml = getTopoInfo(cvp_file)
    file_counter = 0
    if atd_yaml["eos_type"] == "ceos":
        topo_filename = "ceos_build.yml"
    else:
        topo_filename = "topo_build.yml"
    pS("INFO", f"Leveraging {topo_filename} build file")
    while True:
        if path.exists(f"{REPO_TOPO}{atd_yaml['topology']}/{topo_filename}"):
            pS("OK", "BUILD file is available.")
            break
        else:
            if file_counter >= 10:
                exit('Topo Build timer expired')
            else:
                file_counter += 1
                pS("ERROR", f"BUILD file is not available...Waiting for {sleep_delay} seconds")
                sleep(sleep_delay)

    build_yaml = getTopoInfo(f"{REPO_TOPO}{atd_yaml['topology']}/{topo_filename}")

    eos_cnt_map = eosContainerMapper(cvp_yaml['cvp_info']['containers'])
    eos_info = getEosDevice(atd_yaml['topology'],build_yaml['nodes'],eos_cnt_map, atd_yaml['eos_type'])
    eos_dev_map = eosDeviceMapper(atd_yaml['eos_type'], build_yaml['nodes'])
    configlet_location = f"/opt/atd/topologies/{atd_yaml['topology']}/configlets/"
    cvpUsername = atd_yaml['login_info']['jump_host']['user']
    cvpPassword = atd_yaml['login_info']['jump_host']['pw']
    while not cvp_clnt:
        try:
            cvprac_clnt = CvpClient()
            cvprac_clnt.api.request_timeout = 180
            cvprac_clnt.connect([atd_yaml['nodes']['cvp'][0]['ip']], cvpUsername, cvpPassword)
            cvp_clnt = CVPCON(atd_yaml['nodes']['cvp'][0]['ip'], cvpUsername, cvpPassword)
            pS("OK",f"Connected to CVP at {atd_yaml['nodes']['cvp'][0]['ip']}")
        except:
            pS("ERROR",f"CVP is currently unavailable....Retrying in {sleep_delay} seconds.")
            sleep(sleep_delay)

    FILE_BUILD = YAML().load(open(f"{REPO_TOPO}{atd_yaml['topology']}/{topo_filename}", 'r'))

    # Perform check and iterate over all nodes that are CV Manage
    if atd_yaml["eos_type"] == "ceos":
        for _node in FILE_BUILD["nodes"]:
            if _node["cv_manage"]:
                NODES.append(_node)
    else:
        NODES = FILE_BUILD['nodes']
    # ==========================================
    # Add Check for configlet import only
    # ==========================================
    cvpUsername = atd_yaml['login_info']['jump_host']['user']
    cvpPassword = atd_yaml['login_info']['jump_host']['pw']
    cvp_host = atd_yaml['nodes']['cvp'][0]['ip']
    dry_run = os.environ.get('ATD_CV_DRY_RUN', '').lower() in ('1', 'true', 'yes')
    cv_studios = CVStudiosClient(host=cvp_host, username=cvpUsername, password=cvpPassword, dry_run=dry_run)
    cv_studios.connect()

    if 'cvp_mode' in atd_yaml:
        if atd_yaml['cvp_mode'] == 'configlets':
            pS("INFO", "CVP Configlet import only mode")
            cv_studios.push_configlets(loadStaticConfiglets(configlet_location), label='atd-bootstrap-configlets-only')
            pS("OK", "Import of configlets complete.")
            return(True)
        elif atd_yaml['cvp_mode'] == 'bare':
            pS("INFO", "CVP will be bare and no configuration.")
            return(True)
    if cvp_clnt:
        # ==========================================
        # Check the current version to see if a 
        # token needs to be generated
        # ==========================================
        _version = cvprac_clnt.api.get_cvp_info()
        _version = _version['version'].split('.')
        _version_major = float(f"{_version[0]}.{_version[1]}")
        
        # ==========================================
        # Check to see how many nodes have connected
        # ==========================================
        checkConnected(cvprac_clnt, NODES, atd_yaml['eos_type'])

        # ==========================================
        # Push static configlets into CVP via Static Configuration Studio
        # ==========================================
        configlet_bodies = loadStaticConfiglets(configlet_location)
        if configlet_bodies:
            cv_studios.push_configlets(configlet_bodies, label='atd-bootstrap')
            pS("OK", "Configlets pushed via Static Configuration Studio")

        # ==========================================
        # Add new containers into CVP (inventory hierarchy — unchanged from legacy)
        # ==========================================
        for p_cnt in cvp_yaml['cvp_info']['containers'].keys():
            if p_cnt not in cvp_clnt.containers.keys():
                if cvp_yaml['cvp_info']['containers'][p_cnt]:
                    parent_name = cvp_yaml['cvp_info']['containers'][p_cnt]['parent']
                    if parent_name not in containers:
                        _results = cvprac_clnt.api.search_topology(parent_name)
                        containers[parent_name] = _results['containerList'][0]
                    cvprac_clnt.api.add_container(p_cnt, parent_name, containers[parent_name]['key'])
                else:
                    if "Tenant" not in containers:
                        _results = cvprac_clnt.api.search_topology("Tenant")
                        containers["Tenant"] = _results['containerList'][0]
                    cvprac_clnt.api.add_container(p_cnt, "Tenant", containers["Tenant"]['key'])
                pS("OK", f"Added {p_cnt} container")
            else:
                pS("INFO", f"{p_cnt} container already exists....skipping")
            if p_cnt not in containers:
                _results = cvprac_clnt.api.search_topology(p_cnt)
                containers[p_cnt] = _results['containerList'][0]

        # ==========================================
        # Deploy devices into their containers (no configlets yet — Studio handles those)
        # ==========================================
        per_device_configlets = {}
        hostname_to_device_id = {}
        cvp_inventory = cvprac_clnt.api.get_inventory()
        container_cfg_map = cvp_yaml['cvp_info']['configlets'].get('containers', {})
        netelement_cfg_map = cvp_yaml['cvp_info']['configlets'].get('netelements', {})
        for _dev in cvp_inventory:
            if atd_yaml['eos_type'] == "ceos":
                pS("INFO", f"Adding {_dev['hostname']} with s/n {_dev['serialNumber']}")
                _device_name = _dev['serialNumber']
            else:
                pS("INFO", f"Adding {_dev['hostname']}")
                _device_name = eos_dev_map[_dev['ipAddress']]
            _target_cnt = eos_cnt_map[_device_name]
            cvprac_clnt.api.deploy_device(_dev, _target_cnt)

            # Build per-device bootstrap configlet list: container configlets + per-device configlets.
            container_cfgs = container_cfg_map.get(_target_cnt, []) or []
            device_cfgs = netelement_cfg_map.get(_device_name, []) or []
            combined = list(dict.fromkeys(list(container_cfgs) + list(device_cfgs)))
            per_device_configlets[_dev['hostname']] = combined
            dev_id = _dev.get('serialNumber') or _dev.get('systemMacAddress')
            if dev_id:
                hostname_to_device_id[_dev['hostname']] = dev_id

        # ==========================================
        # Apply per-device ConfigletAssignments via Static Configuration Studio
        # ==========================================
        if per_device_configlets:
            cv_studios.apply_lab(
                per_device_configlets=per_device_configlets,
                hostname_to_device_id=hostname_to_device_id,
                label='bootstrap',
            )
            pS("OK", "Bootstrap ConfigletAssignments applied via Static Configuration Studio")

        # ==========================================
        # Creating Snapshots
        # ==========================================
        if "snapshots" in cvp_yaml["cvp_info"]:
            if cvp_yaml['cvp_info']['snapshots']:
                for p_snap in cvp_yaml['cvp_info']['snapshots']:
                    NEW_SNAP = True
                    for e_snap in cvp_clnt.snapshots:
                        if p_snap['name'] == e_snap['name']:
                            NEW_SNAP = False
                    if NEW_SNAP:
                        cvp_clnt.createSnapshot(p_snap['name'],p_snap['commands'])
                        pS("OK",f"Created {p_snap['name']} Snapshot")
                    else:
                        pS("OK",f"Snapshot {p_snap['name']} already exists")
        # Close the Studios client (session times out on its own; rcvpapi session is left alone).
        cv_studios.close()
        pS("OK", "Closed Static Configuration Studio session")
    else:
        pS("ERROR", "Couldn't connect to CVP")

if __name__ == '__main__':
    # Open Syslog
    pS("OK","Starting...")

    if not path.exists(CVP_CONFIG_FIILE):
        # Start the main Service
        pS("OK","Initial ATD Topo Boot")
        main()
        with open(CVP_CONFIG_FIILE,'w') as tf:
            tf.write("CVP_CONFIGURED\n")
        pS("OK","Completed CVP Configuration")
    else:
        pS("OK","CVP is already configured")
    while True:
          sleep(600)
