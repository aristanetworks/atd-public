#!/usr/bin/env python


from ruamel.yaml import YAML
from rcvpapi.rcvpapi import *
import requests, json
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

def getEosDevice(topo,eosYaml,cvpMapper):
    """
    Function that Parses through the YAML file and creates a CVPSWITCH class object for each EOS device in the topo file.
    Parameters:
    topo = Topology for the ATD (required)
    eosYAML = vEOS portion of the ACCESS_INFO.yaml file (required)
    cvpMapper = Dict that maps EOS device to container (required)
    """
    EOS_DEV = []
    for dev in eosYaml:
        devn = list(dev.keys())[0]
        try:
            EOS_DEV.append(CVPSWITCH(devn,dev[devn]['ip_addr'],cvpMapper[devn]))
            checkContainer(cvpMapper[dev])
        except:
            EOS_DEV.append(CVPSWITCH(devn,dev[devn]['ip_addr']))
    return(EOS_DEV)

def eosContainerMapper(cvpYaml):
    """
    Function that Parses through the YAML file and maps device to container.
    Parameters:
    cvpYaml = cvp containers portion of the cvp_info.yaml file (required)
    """
    eMap = {}
    for cnt in cvpYaml.keys():
        if cvpYaml[cnt]:
            for eosD in cvpYaml[cnt]:
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

def checkConnected(cvp_clnt, NODES):
    """
    Function to check if all nodes have connected and
    are reachable via ping
    Parameters:
    cvp_clnt = CVP rCVPAPI client (object)
    NODES = EOS Node yaml (dict)
    """
    tmp_device_count = len(cvp_clnt.inventory)
    while len(NODES) > tmp_device_count:
        pS("INFO", "Only {0} out of {1} nodes have registered to CVP. Sleeping {2} seconds.".format(tmp_device_count, len(NODES), sleep_delay))
        sleep(sleep_delay)
        cvp_clnt.getDeviceInventory()
        tmp_device_count = len(cvp_clnt.inventory)
    pS("OK", "All {0} out of {1} nodes have registered to CVP.".format(tmp_device_count, len(NODES)))
    pS("INFO", "Checking to see if all nodes are reachable")
    # Make sure all nodes are up and reachable
    for vnode in cvp_clnt.inventory:
        while True:
            vresponse = cvp_clnt.ipConnectivityTest(cvp_clnt.inventory[vnode]['ipAddress'])
            if 'data' in vresponse:
                if vresponse['data'] == 'success':
                    pS("OK", "{0} is up and reachable at {1}".format(vnode, cvp_clnt.inventory[vnode]['ipAddress']))
                    break
            else:
                pS("INFO", "{0} is NOT reachable at {1}. Sleeping {2} seconds.".format(vnode, cvp_clnt.inventory[vnode]['ipAddress'], sleep_delay))
                sleep(sleep_delay)
    pS("OK", "All Devices are registered and reachable.")
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
                pS("INFO","Adding/Updating {0} configlet builder.".format(tmp_cfg))
                cbname = tmp_cfg.replace('.py','')
                # !!! Add section to check for .form file to import form list options
                with open(cfg_dir + tmp_cfg,'r') as cfglt:
                    cvp_clnt.impConfiglet('builder',cbname,cfglt.read())
            elif '.form' in tmp_cfg:
                # Ignoring .form files here
                pass
            else:
                pS("INFO","Adding/Updating {0} static configlet.".format(tmp_cfg))
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
    while True:
        if path.exists(topo_file):
            pS("OK", "ACCESS_INFO file is available.")
            break
        else:
            if file_counter >= 10:
                exit('Access INFO timer expired')
            else:
                file_counter += 1
                pS("ERROR", "ACCESS_INFO file is not available...Waiting for {0} seconds".format(sleep_delay))
                sleep(sleep_delay)
    atd_yaml = getTopoInfo(topo_file)
    cvp_yaml = getTopoInfo(cvp_file)
    file_counter = 0
    while True:
        if path.exists(REPO_TOPO + atd_yaml['topology'] + '/topo_build.yml'):
            pS("OK", "TOPO_BUILD file is available.")
            break
        else:
            if file_counter >= 10:
                exit('Topo Build timer expired')
            else:
                file_counter += 1
                pS("ERROR", "TOPO_BUILD file is not available...Waiting for {0} seconds".format(sleep_delay))
                sleep(sleep_delay)

    build_yaml = getTopoInfo(REPO_TOPO + atd_yaml['topology'] + '/topo_build.yml')
    eos_cnt_map = eosContainerMapper(cvp_yaml['cvp_info']['containers'])
    eos_info = getEosDevice(atd_yaml['topology'],build_yaml['nodes'],eos_cnt_map)
    configlet_location = '/opt/atd/topologies/{0}/configlets/'.format(atd_yaml['topology'])
    cvpUsername = atd_yaml['login_info']['jump_host']['user']
    cvpPassword = atd_yaml['login_info']['jump_host']['pw']
    while not cvp_clnt:
        try:
            cvp_clnt = CVPCON(atd_yaml['nodes']['cvp'][0]['ip'], cvpUsername, cvpPassword)
            pS("OK","Connected to CVP at {0}".format(atd_yaml['nodes']['cvp'][0]['ip']))
        except:
            pS("ERROR","CVP is currently unavailable....Retrying in {0} seconds.".format(sleep_delay))
            sleep(sleep_delay)
    
    # Check to see if all nodes have connected to CVP before proceeding
    FILE_BUILD = YAML().load(open(REPO_TOPO + atd_yaml['topology'] + '/topo_build.yml', 'r'))
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
    if cvp_clnt:
        # ==========================================
        # Check to see how many nodes have connected
        # ==========================================
        checkConnected(cvp_clnt, NODES)

        # ==========================================
        # Add configlets into CVP
        # ==========================================
        importConfiglets(cvp_clnt, configlet_location)

        # ==========================================
        # Add new containers into CVP
        # ==========================================
        for p_cnt in cvp_yaml['cvp_info']['containers'].keys():
            if p_cnt not in cvp_clnt.containers.keys():
                cvp_clnt.addContainer(p_cnt,"Tenant")
                cvp_clnt.saveTopology()
                cvp_clnt.getAllContainers()
                pS("OK","Added {0} container".format(p_cnt))
            else:
                pS("INFO","{0} container already exists....skipping".format(p_cnt))
            # Check and add configlets to containers
            if p_cnt in cvp_yaml['cvp_info']['configlets']['containers'].keys():
                cfgs_cnt_ignore = []
                proposed_cnt_cfgs = cvp_yaml['cvp_info']['configlets']['containers'][p_cnt]
                p_cnt_id = cvp_clnt.getContainerId(p_cnt)[0]['Key']
                existing_cnt_cfgs = cvp_clnt.getConfigletsByContainerId(p_cnt_id)
                if existing_cnt_cfgs:
                    for ex_cfg in existing_cnt_cfgs['configletList']:
                        if ex_cfg['name'] not in proposed_cnt_cfgs:
                            cfgs_cnt_ignore.append(ex_cfg['name'])
                pS("OK","Configlets found for {0} container.  Will apply".format(p_cnt))
                cvp_clnt.removeContainerConfiglets(p_cnt, cfgs_cnt_ignore)
                cvp_clnt.addContainerConfiglets(p_cnt, proposed_cnt_cfgs)
                cvp_clnt.applyConfigletsContainers(p_cnt)
                cvp_clnt.saveTopology()
                cvp_clnt.getAllTasks("pending")
                task_response = cvp_clnt.execAllTasks("pending")
                # Perform check to see if there are any existing tasks to be executed
                if task_response:
                    pS("OK", "All pending tasks are executing")
                    for task_id in task_response['ids']:
                        task_status = cvp_clnt.getTaskStatus(task_id)['taskStatus']
                        while task_status != "Completed":
                            task_status = cvp_clnt.getTaskStatus(task_id)['taskStatus']
                            if task_status == 'Failed':
                                pS("iBerg", "Task ID: {0} Status: {1}".format(task_id, task_status))
                                break
                            elif task_status == 'Completed':
                                pS("INFO", "Task ID: {0} Status: {1}".format(task_id, task_status))
                                break
                            else:
                                pS("INFO", "Task ID: {0} Status: {1}, Waiting 10 seconds...".format(task_id, task_status))
                                sleep(10)
                else:
                    pS("INFO", "No pending tasks found")
        # ==========================================
        # Update configlet info for all containers
        # ==========================================
        for p_cnt in cvp_clnt.containers:
            cvp_clnt.updateContainersConfigletsInfo(p_cnt)
        # ==========================================
        # Add devices to Inventory/Provisioning
        # ==========================================
        # Perform initial check and do a group add of devices
        tmp_eos_add = []
        for eos in eos_info:
            # Check to see if the device is already provisioned
            if eos.hostname not in cvp_clnt.inventory.keys():
                pS("INFO","Adding {}".format(eos.hostname))
                tmp_eos_add.append(eos.ip)
            else:
                pS("INFO","{} is already added into Provisioning".format(eos.hostname))
        if tmp_eos_add:
            # Import all devices not 
            pS("INFO","Importing devices: {0}".format(", ".join(tmp_eos_add)))
            cvp_clnt.addDeviceInventory(tmp_eos_add)
        for eos in eos_info:
            # Check to see if the device has a target container
            if eos.targetContainerName:
                pS("INFO", "{0} is the target container for {1}".format(eos.targetContainerName, eos.hostname))
                eos.updateContainer(cvp_clnt)
                if eos.targetContainerName != eos.parentContainer["name"]:
                    pS("INFO", "Moving {0} from {1} to {2}".format(eos.hostname, eos.parentContainer['name'], eos.targetContainerName))
                    cvp_clnt.moveDevice(eos)
                    try:
                        cvp_clnt.genConfigBuilders(eos)
                    except KeyError:
                        pS("INFO", "No Configlet Builders Found for {0}".format(eos.hostname))
                if cvp_yaml['cvp_info']['configlets']['netelements']:
                    if eos.hostname in cvp_yaml['cvp_info']['configlets']['netelements']:
                        eos_new_cfgs = cvp_yaml['cvp_info']['configlets']['netelements'][eos.hostname]
                        # Check to see if there are any existing configlets applied
                        tmp_eos_cfgs = cvp_clnt.getConfigletsByNetElementId(eos)
                        if tmp_eos_cfgs:
                            tmp_cfgs_remove = []
                            for cfg in tmp_eos_cfgs['configletList']:
                                if cfg['name'] not in eos_new_cfgs and cfg['name'] not in cvp_clnt.containers['Tenant']['configlets']['names'] and cfg['name'] not in cvp_clnt.containers[eos.targetContainerName]['configlets']['names']:
                                    tmp_cfgs_remove.append(cfg['name'])
                            pS("INFO", "[{0}] Configlets to remove: {1}".format(eos.hostname, ", ".join(tmp_cfgs_remove)))
                            eos.removeConfiglets(cvp_clnt, tmp_cfgs_remove)
                        cvp_clnt.addDeviceConfiglets(eos, eos_new_cfgs)
                cvp_clnt.applyConfiglets(eos)
        cvp_clnt.saveTopology()
        pS("OK", "Topology saved")
        cvp_clnt.getAllTasks("pending")
        task_response = cvp_clnt.execAllTasks("pending")
        pS("OK", "All pending tasks are executing")
        for task_id in task_response['ids']:
            previous_status = ''
            task_status = cvp_clnt.getTaskStatus(task_id)['taskStatus']
            while task_status != "Completed":
                task_status = cvp_clnt.getTaskStatus(task_id)
                if 'taskStatus' in task_status:
                    task_status = task_status['taskStatus']
                    if task_status == 'Failed':
                        pS("iBerg", "Task ID: {0} Status: {1}".format(task_id, task_status))
                        break
                    elif task_status == 'Completed':
                        pS("INFO", "Task ID: {0} Status: {1}".format(task_id, task_status))
                    else:
                        pS("INFO", "Task ID: {0} Status: {1}, Waiting 10 seconds...".format(task_id, task_status))
                        previous_status = task_status
                        sleep(10)
                else:
                    pS("INFO", "Task ID: {0} Status: {1}, Waiting 10 seconds...".format(task_id, previous_status))
                    sleep(10)

        # ==========================================
        # Creating Snapshots
        # ==========================================
        if cvp_yaml['cvp_info']['snapshots']:
            for p_snap in cvp_yaml['cvp_info']['snapshots']:
                NEW_SNAP = True
                for e_snap in cvp_clnt.snapshots:
                    if p_snap['name'] == e_snap['name']:
                        NEW_SNAP = False
                if NEW_SNAP:
                    cvp_clnt.createSnapshot(p_snap['name'],p_snap['commands'])
                    pS("OK","Created {0} Snapshot".format(p_snap['name']))
                else:
                    pS("OK","Snapshot {0} already exists".format(p_snap['name']))
        # Logout and close session to CVP
        cvp_clnt.execLogout()
        pS("OK","Logged out of CVP")
        # # Adding section to reboot all vEOS nodes in case 
        # # multi-agent needs to initialize on initial deployment
        # for eos in eos_info:
        #     pS("INFO", "Rebooting {0}".format(eos.hostname))
        #     system("/usr/bin/ssh -f arista@{0} reload now".format(eos.ip))
        #     pS("OK", "{0} has been rebooted.".format(eos.hostname))
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
