#!/usr/bin/env python3

from ruamel.yaml import YAML
from rcvpapi.rcvpapi import *
import requests, json, syslog
from os import path, listdir, system
from time import sleep
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

topo_file = '/etc/ACCESS_INFO.yaml'
CVP_CONFIG_FILE = '/home/arista/.cvpState.txt'
CVP_CONTAINERS = []
FILE_DELAY = 10

# Temporary file_path location for CVP Custom info
cvp_file = '/home/arista/cvp/cvp_info.yaml'
pDEBUG = True

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
        try:
            EOS_DEV.append(CVPSWITCH(dev['hostname'],dev['internal_ip'],cvpMapper[dev['hostname']]))
            checkContainer(cvpMapper[dev['hostname']])
        except:
            EOS_DEV.append(CVPSWITCH(dev['hostname'],dev['internal_ip']))
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
    syslog.syslog("[{0}] {1}".format(mstat,mmes.expandtabs(7 - len(mstat))))
    if pDEBUG:
        print("[{0}] {1}".format(mstat,mmes.expandtabs(7 - len(mstat))))

def main():
    """
    Main Function if this is the initial deployment for the ATD/CVP
    """
    cvp_clnt = ""
    while not path.exists(topo_file):
        sleep(FILE_DELAY)
        pS("INFO", "Topo file not found, waiting.")
    while not path.exists(cvp_file):
        sleep(FILE_DELAY)
        pS("INFO", "CVP build file not found, waiting.")
    atd_yaml = getTopoInfo(topo_file)
    cvp_yaml = getTopoInfo(cvp_file)
    eos_cnt_map = eosContainerMapper(cvp_yaml['cvp_info']['containers'])
    eos_info = getEosDevice(atd_yaml['topology'],atd_yaml['nodes']['veos'],eos_cnt_map)
    configlet_location = '/tmp/atd/topologies/{0}/configlets/'.format(atd_yaml['topology'])
    for c_login in atd_yaml['login_info']['cvp']['shell']:
        if c_login['user'] == 'arista':
            while not cvp_clnt:
                try:
                    cvp_clnt = CVPCON(atd_yaml['nodes']['cvp'][0]['internal_ip'],c_login['user'],c_login['pw'])
                    pS("OK","Connected to CVP at {0}".format(atd_yaml['nodes']['cvp'][0]['internal_ip']))
                except:
                    pS("ERROR","CVP is currently unavailable....Retrying in 30 seconds.")
                    sleep(30)
    if cvp_clnt:
        # ==========================================
        # Add configlets into CVP
        # ==========================================
        while not path.exists(configlet_location):
            sleep(FILE_DELAY)
            pS("INFO", "Configlets directory not found, waiting...")
        if path.exists(configlet_location):
            pS("OK","Configlet directory exists")
            pro_cfglt = listdir(configlet_location)
            for tmp_cfg in pro_cfglt:
                if '.py' in tmp_cfg:
                    pS("INFO","Adding/Updating {0} configlet builder.".format(tmp_cfg))
                    cbname = tmp_cfg.replace('.py','')
                    # !!! Add section to check for .form file to import form list options
                    with open(configlet_location + tmp_cfg,'r') as cfglt:
                        cvp_clnt.impConfiglet('builder',cbname,cfglt.read())
                elif '.form' in tmp_cfg:
                    # Ignoring .form files here
                    pass
                else:
                    pS("INFO","Adding/Updating {0} static configlet.".format(tmp_cfg))
                    with open(configlet_location + tmp_cfg,'r') as cfglt:
                        cvp_clnt.impConfiglet('static',tmp_cfg,cfglt.read())
        else:
            pS("INFO","No Configlet directory found")
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
            task_status = cvp_clnt.getTaskStatus(task_id)['taskStatus']
            while task_status != "Completed":
                task_status = cvp_clnt.getTaskStatus(task_id)['taskStatus']
                if task_status == 'Failed':
                    pS("iBerg", "Task ID: {0} Status: {1}".format(task_id, task_status))
                    break
                elif task_status == 'Completed':
                    pS("INFO", "Task ID: {0} Status: {1}".format(task_id, task_status))
                else:
                    pS("INFO", "Task ID: {0} Status: {1}, Waiting 10 seconds...".format(task_id, task_status))
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
        # Adding section to reboot all vEOS nodes in case 
        # multi-agent needs to initialize on initial deployment
        for eos in eos_info:
            pS("INFO", "Rebooting {0}".format(eos.hostname))
            system("/usr/bin/ssh -f arista@{0} reload now".format(eos.ip))
            pS("OK", "{0} has been rebooted.".format(eos.hostname))
    else:
        pS("ERROR","Couldn't connect to CVP")

if __name__ == '__main__':
    # Open Syslog
    syslog.openlog(logoption=syslog.LOG_PID)
    pS("OK","Starting...")

    atd_yaml = getTopoInfo(topo_file)
    if 'cvp' in atd_yaml['nodes']:
        if not path.exists(CVP_CONFIG_FILE):
            # Start the main Service
            pS("OK","Initial ATD Topo Boot")
            main()
            with open(CVP_CONFIG_FILE,'w') as tf:
                tf.write("CVP_CONFIGURED\n")
            pS("OK","Completed CVP Configuration")
        else:
            pS("OK","CVP is already configured")
    else:
        pS("INFO","CVP is not present in this topology, preventing future run of cvpUpdater")
        with open(CVP_CONFIG_FILE,'w') as tf:
            tf.write("CVP_CONFIGURED\n")
