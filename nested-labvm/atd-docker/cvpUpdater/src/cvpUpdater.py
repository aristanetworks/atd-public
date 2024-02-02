#!/usr/bin/env python

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


def importConfiglets(cvp_clnt, cfg_dir):
    """
    Function to import configlets into CVP
    Parameters:
    cvp_clnt = CVP rCVPAPI client (object)
    cfg_dir = Configlet directory (str)
    """
    if path.exists(cfg_dir):
        pS("OK","Configlet directory exists")
        pro_cfglt = listdir(cfg_dir)
        for tmp_cfg in pro_cfglt:
            if '.py' in tmp_cfg:
                pS("INFO",f"Adding/Updating {tmp_cfg} configlet builder.")
                cbname = tmp_cfg.replace('.py','')
                # Check for a form file
                if tmp_cfg.replace('.py', '.form') in pro_cfglt:
                    pS("INFO", f"Form data found for {cbname}")
                    with open(cfg_dir + tmp_cfg.replace('.py', '.form'), 'r') as configletData:
                        configletForm = configletData.read()
                    configletFormData = YAML().load(configletForm)['FormList']
                else:
                    configletFormData = []
                with open(cfg_dir + tmp_cfg,'r') as cfglt:
                    cfg_data = cfglt.read()
                res = cvp_clnt.impConfiglet('builder', cbname, cfg_data, configletFormData)
                pS("OK", f"{res[0]} Configlet Builder: {cbname}")
            elif '.form' in tmp_cfg:
                # Ignoring .form files here
                pass
            else:
                pS("INFO",f"Adding/Updating {tmp_cfg} static configlet.")
                with open(cfg_dir + tmp_cfg,'r') as cfglt:
                    cvp_clnt.impConfiglet('static',tmp_cfg,cfglt.read())
        pS("INFO", "All configlets imported")
        return(True)
    else:
        pS("INFO","No Configlet directory found")
        return(False)



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
    if 'cvp_mode' in atd_yaml:
        if atd_yaml['cvp_mode'] == 'configlets':
            pS("INFO", "CVP Configlet import only mode")
            importConfiglets(cvp_clnt, configlet_location)
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
        # Add configlets into CVP
        # ==========================================
        importConfiglets(cvp_clnt, configlet_location)

        # ==========================================
        # Add new containers into CVP
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
                pS("OK",f"Added {p_cnt} container")
            else:
                pS("INFO", f"{p_cnt} container already exists....skipping")
            if p_cnt not in containers:
                _results = cvprac_clnt.api.search_topology(p_cnt)
                containers[p_cnt] = _results['containerList'][0]
            # Check and add configlets to containers
            if p_cnt in cvp_yaml['cvp_info']['configlets']['containers'].keys():
                cfgs_cnt_ignore = []
                proposed_cfgs = []
                proposed_cnt_cfgs = cvp_yaml['cvp_info']['configlets']['containers'][p_cnt]
                # Get Proposed configlet info
                for _cfg in proposed_cnt_cfgs:
                    _cfg_result = cvprac_clnt.api.get_configlet_by_name(_cfg)
                    proposed_cfgs.append(_cfg_result)
                container_info = cvprac_clnt.api.get_container_by_name(p_cnt)
                p_cnt_id = container_info['key']
                existing_cnt_cfgs = cvprac_clnt.api.get_configlets_by_container_id(p_cnt_id)
                if existing_cnt_cfgs:
                    for ex_cfg in existing_cnt_cfgs['configletList']:
                        if ex_cfg['name'] not in proposed_cnt_cfgs:
                            cfgs_cnt_ignore.append({
                                'name': ex_cfg['name'],
                                'key': ex_cfg['key']
                            })
                pS("OK",f"Configlets found for {p_cnt} container.  Will apply")
                cvprac_clnt.api.remove_configlets_from_container("cvpUpdater", container_info, cfgs_cnt_ignore)
                cvprac_clnt.api.apply_configlets_to_container("cvpUpdater", container_info, proposed_cfgs)
                pending_tasks = cvprac_clnt.api.get_tasks_by_status("pending")
                # Execute all Tasks
                for _task in pending_tasks:
                    cvprac_clnt.api.execute_task(_task['workOrderId'])
                # Perform check to see if there are any existing tasks to be executed
                if pending_tasks:
                    pS("OK", "All pending tasks are executing")
                    for task in pending_tasks:
                        task_id = task['workOrderId']
                        task_info = cvprac_clnt.api.get_task_by_id(task_id)
                        task_status = task_info['workOrderUserDefinedStatus']
                        while task_status != "Completed":
                            task_info = cvprac_clnt.api.get_task_by_id(task_id)
                            task_status = task_info['workOrderUserDefinedStatus']
                            if task_status == 'Failed':
                                pS("iBerg", f"Task ID: {task_id} Status: {task_status}")
                                break
                            elif task_status == 'Completed':
                                pS("INFO", f"Task ID: {task_id} Status: {task_status}")
                                break
                            else:
                                pS("INFO", f"Task ID: {task_id} Status: {task_status}, Waiting 10 seconds...")
                                sleep(10)
                else:
                    pS("INFO", "No pending tasks found")
        # ==========================================
        # Add devices to Inventory/Provisioning
        # ==========================================
        # Perform initial check and do a group add of devices
        tmp_eos_add = []
        cvp_inventory = cvprac_clnt.api.get_inventory()
        for _dev in cvp_inventory:
            _tmp_eos_cfg = []
            _device_name = ''
            # Check if this is a cEOS ZTP setup
            if atd_yaml['eos_type'] == "ceos":
                pS("INFO", f"Adding {_dev['hostname']} with s/n {_dev['serialNumber']}")
                _device_name = _dev['serialNumber']
                _target_cnt = eos_cnt_map[_device_name]
            else:
                pS("INFO", f"Adding {_dev['hostname']}")
                _device_name = eos_dev_map[_dev['ipAddress']]
                _target_cnt = eos_cnt_map[_device_name]
            if _device_name in cvp_yaml['cvp_info']['configlets']['netelements']:
                for _cfg in cvp_yaml['cvp_info']['configlets']['netelements'][_device_name]:
                    _tmp_eos_cfg.append(cvprac_clnt.api.get_configlet_by_name(_cfg))
            cvprac_clnt.api.deploy_device(_dev, _target_cnt, configlets=_tmp_eos_cfg)
        pending_tasks = cvprac_clnt.api.get_tasks_by_status("pending")
        for _task in pending_tasks:
            cvprac_clnt.api.execute_task(_task['workOrderId'])
        pS("OK", "All pending tasks are executing")
        for task in pending_tasks:
            task_id = task['workOrderId']
            task_info = cvprac_clnt.api.get_task_by_id(task_id)
            task_status = task_info['workOrderUserDefinedStatus']
            previous_status = ''
            if task_status == "Completed":
                pS("OK", f"Task ID: {task_id} Status: {task_status}")
            while task_status != "Completed":
                task_info = cvprac_clnt.api.get_task_by_id(task_id)
                task_status = task_info['workOrderUserDefinedStatus']
                if task_status:
                    if task_status == 'Failed':
                        pS("iBerg", f"Task ID: {task_id} Status: {task_status}")
                        break
                    elif task_status == 'Completed':
                        pS("OK", f"Task ID: {task_id} Status: {task_status}")
                    else:
                        pS("INFO", f"Task ID: {task_id} Status: {task_status}, Waiting 10 seconds...")
                        previous_status = task_status
                        sleep(10)
                else:
                    pS("INFO", f"Task ID: {task_id} Status: {previous_status}, Waiting 10 seconds...")
                    sleep(10)

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
        # Logout and close session to CVP
        cvp_clnt.execLogout()
        pS("OK","Logged out of CVP")
    else:
        pS("ERROR","Couldn't connect to CVP")

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
