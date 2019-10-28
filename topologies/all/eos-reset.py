#!/usr/bin/env python
"""
Script that will reset any or all EOS devices
and CVP back to original state.
"""

from time import sleep
from os import path, listdir
import argparse
import syslog
import warnings
import urllib3
import paramiko
from rcvpapi.rcvpapi import *
from ruamel.yaml import YAML

warnings.filterwarnings(action='ignore', module='.*paramiko.*')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ACCESS = '/etc/ACCESS_INFO.yaml'
CVPINFO = '/home/arista/cvp/cvp_info.yaml'
BARE_CFGS = ['AAA']
CVP_CONTAINERS = []
PDEBUG = True
DELAYTIMER = 30
# List object to list available devices
dev_list = []
# Dict object to keep track of veos devices
re_veos = {}

# Cmds to copy bare startup to running
dev_cmds = """enable
copy startup-config running-config
"""
# Cmds to grab ZTP status
ztp_cmds = """enable
show zerotouch | grep ZeroTouch
"""
# Cancel ZTP
ztp_cancel = """enable
zerotouch cancel
"""
# Bare device specific config portion
dev_bare = """hostname {0}
!
ip route 0.0.0.0/0 192.168.0.254
!
interface Management1
   ip address {1}/24
   no lldp transmit
   no lldp receive
!
ip routing
!
management api http-commands
   no shutdown
"""

# Loading ACCESS_INFO
with open(ACCESS, 'r') as atdyaml:
    atd_yaml = YAML().load(atdyaml)
    veos_devs = atd_yaml['nodes']['veos']
    TOPO = atd_yaml['topology']

for veos in veos_devs:
    if 'host' not in veos['hostname']:
        dev_list.append(veos['hostname'])
        re_veos[veos['hostname']] = {'hostname':veos['hostname'], 'internal_ip':veos['internal_ip'], 'ip':veos['ip'], 'cvpobj':""}

# Loading cvp_info.yaml
with open(CVPINFO, 'r') as ci:
    cvp_yaml = YAML().load(ci)

def pushBareConfig(veos_host, veos_ip, veos_config):
    """
    Pushes a bare config to the EOS device.
    """
    DEVREBOOT = False
    veos_ssh = paramiko.SSHClient()
    veos_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    veos_ssh.connect(hostname=veos_ip, username="root", password="", port="22220")
    veos_ssh.exec_command("echo '{0}' | tee /mnt/flash/startup-config".format(veos_config))
    veos_ssh.exec_command('FastCli -c "{0}"'.format(dev_cmds))
    stdin, stdout, stderr = veos_ssh.exec_command('FastCli -c "{0}"'.format(ztp_cmds))
    ztp_out = stdout.readlines()
    if 'Active' in ztp_out[0]:
        DEVREBOOT = True
        pS("INFO", "Rebooting {0}...This will take a couple minutes to come back up".format(veos_host))
        #veos_ssh.exec_command("/sbin/reboot -f > /dev/null 2>&1 &")
        veos_ssh.exec_command('FastCli -c "{0}"'.format(ztp_cancel))
    veos_ssh.close()
    return(DEVREBOOT)

def conCVP():
    """
    create connection to CVP.
    """
    cvp_clnt = False
    for c_login in atd_yaml['login_info']['cvp']['shell']:
        if c_login['user'] == 'arista':
            while not cvp_clnt:
                try:
                    cvp_clnt = CVPCON(atd_yaml['nodes']['cvp'][0]['internal_ip'], c_login['user'], c_login['pw'])
                    pS("OK", "Connected to CVP at {0}".format(atd_yaml['nodes']['cvp'][0]['internal_ip']))
                    return(cvp_clnt)
                except:
                    pS("ERROR", "CVP is currently unavailable....Retrying in 30 seconds.")
                    sleep(30)

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

def checkContainer(cnt):
    """
    Function to check and see if the supplied container is already in the global container list.
    Parameters:
    cnt = Container to add if it does not exist in the list (required)
    """
    if cnt not in CVP_CONTAINERS:
        CVP_CONTAINERS.append(cnt)

def getEosDevice(topo, eosYaml, cvpMapper, veos_reset):
    """
    Function that Parses through the YAML file and creates a CVPSWITCH class object for each EOS device in the topo file.
    Parameters:
    topo = Topology for the ATD (required)
    eosYAML = vEOS portion of the ACCESS_INFO.yaml file (required)
    cvpMapper = Dict that maps EOS device to container (required)
    veos_reset = List of devices to be reset (required)
    """
    EOS_DEV = []
    for dev in eosYaml:
        if dev['hostname'] in veos_reset:
            try:
                EOS_DEV.append(CVPSWITCH(dev['hostname'], dev['internal_ip'], cvpMapper[dev['hostname']]))
                checkContainer(cvpMapper[dev['hostname']])
            except:
                EOS_DEV.append(CVPSWITCH(dev['hostname'], dev['internal_ip']))
    return(EOS_DEV)

def restoreConfiglets(cvp_clnt, configlet_location):
    """
    Restores all configlets back to CVP.
    """
    if path.exists(configlet_location):
        pS("OK", "Configlet directory exists")
        pro_cfglt = listdir(configlet_location)
        pS("OK", "Restoring all Configlets in CVP")
        for tmp_cfg in pro_cfglt:
            if '.py' in tmp_cfg:
                cbname = tmp_cfg.replace('.py', '')
                # !!! Add section to check for .form file to import form list options
                with open(configlet_location + tmp_cfg, 'r') as cfglt:
                    cvp_clnt.impConfiglet('builder', cbname, cfglt.read())
            elif '.form' in tmp_cfg:
                # Ignoring .form files here
                pass
            else:
                with open(configlet_location + tmp_cfg, 'r') as cfglt:
                    cvp_clnt.impConfiglet('static', tmp_cfg, cfglt.read())
    else:
        pS("INFO", "No Configlet directory found")

def restoreContainers(cvp_clnt):
    """
    Function to restore all containers into CVP and to re-apply and applied configlets
    """
    cvp_clnt.getAllContainers()
    for p_cnt in cvp_yaml['cvp_info']['containers'].keys():
        if p_cnt not in cvp_clnt.containers.keys():
            cvp_clnt.addContainer(p_cnt, "Tenant")
            cvp_clnt.saveTopology()
            cvp_clnt.getAllContainers()
            pS("OK", "Added {0} container".format(p_cnt))
        else:
            pS("INFO", "{0} container already exists....skipping".format(p_cnt))
        # Check and add configlets to containers
        if p_cnt in cvp_yaml['cvp_info']['configlets']['containers'].keys():
            pS("OK", "Configlets found for {0} container.  Will apply".format(p_cnt))
            cvp_clnt.addContainerConfiglets(p_cnt, cvp_yaml['cvp_info']['configlets']['containers'][p_cnt])
            cvp_clnt.applyConfigletsContainers(p_cnt)
            cvp_clnt.saveTopology()

def provisionDevice(cvp_clnt, eos):
    """
    Function to provision an EOS devices.
    """
    # Check to see if the device has a target container
    if eos.targetContainerName:
        # Update EOS Object with container information
        eos.updateContainer(cvp_clnt)
        # Check if device is in target container
        if eos.targetContainerName != eos.parentContainer["name"]:
            # Move device to target container, generate and apply any configlets
            cvp_clnt.moveDevice(eos)
            cvp_clnt.genConfigBuilders(eos)
            if eos.hostname in cvp_yaml['cvp_info']['configlets']['netelements'].keys():
                cvp_clnt.addDeviceConfiglets(eos, cvp_yaml['cvp_info']['configlets']['netelements'][eos.hostname])
            cvp_clnt.applyConfiglets(eos)
        else:
            # If already in target container, generate any configlets and apply configlets
            cvp_clnt.genConfigBuilders(eos)
            if eos.hostname in cvp_yaml['cvp_info']['configlets']['netelements'].keys():
                cvp_clnt.addDeviceConfiglets(eos, cvp_yaml['cvp_info']['configlets']['netelements'][eos.hostname])
            cvp_clnt.applyConfiglets(eos)
    else:
        pS("iBerg", "No target container found for {0}".format(eos.hostname))

def pS(mstat, mtype):
    """
    Function to send output from service file to Syslog
    Parameters:
    mstat = Message Status, ie "OK", "INFO" (required)
    mtype = Message to be sent/displayed (required)
    """
    mmes = "\t" + mtype
    syslog.syslog("[{0}] {1}".format(mstat, mmes.expandtabs(7 - len(mstat))))
    if PDEBUG:
        print("[{0}] {1}".format(mstat, mmes.expandtabs(7 - len(mstat))))

def main(vdevs):
    """
    Main func.
    """
    DEVREBOOT = False
    pS("INFO", "Device{0} to be reset: {1}".format("s" if len(vdevs) > 1 else "", ", ".join(vdevs)))
    bare_veos = ""
    dev_reboot_status = {}
    configlet_location = '/tmp/atd/topologies/{0}/configlets/'.format(atd_yaml['topology'])
    # Used to store a list of IPs to be used for import into CVP
    tmp_veos_ips = []
    for b_cfg in BARE_CFGS:
        with open('/tmp/atd/topologies/{0}/configlets/{1}'.format(TOPO, b_cfg), 'r') as bcfg:
            bare_veos += bcfg.read()
    # Build device specific bare configurations
    for cur_veos in vdevs:
        tmp_veos_config = bare_veos + dev_bare.format(re_veos[cur_veos]['hostname'], re_veos[cur_veos]['internal_ip'])
        tmp_veos_ips.append(re_veos[cur_veos]['internal_ip'])
        # Push bare config to remote startup-config and reboot device
        if pushBareConfig(cur_veos, re_veos[cur_veos]['ip'], tmp_veos_config):
            DEVREBOOT = True
            dev_reboot_status[cur_veos] = {"status":False, "IP":re_veos[cur_veos]['internal_ip']}
    pS("OK", "Configs pushed to: {0}".format(", ".join(vdevs)))
    if DEVREBOOT:
        pS("INFO", "Devices rebooting, waiting for devices to come back online")
    # Create connection to CVP
    cvp_clnt = conCVP()
    # Restore CVP Configlets back to repo base
    restoreConfiglets(cvp_clnt, configlet_location)
    restoreContainers(cvp_clnt)
    cvp_clnt.saveTopology()
    # Check for any pending tasks from configlet restore
    cvp_clnt.getAllTasks("pending")
    if cvp_clnt.tasks['pending']:
        pS("OK", "Executing all tasks")
        cvp_clnt.execAllTasks("pending")
        pS("OK", "Tasks executed")
    # Check for failed tasks and cancel them.
    cvp_clnt.getAllTasks("failed")
    if cvp_clnt.tasks['failed']:
        pS("OK", "Cancelling previously failed tasks")
        cvp_clnt.cancelTasks("failed")
    # Check to verify all devices to be reset have booted up
    for vdevR in dev_reboot_status:
        while not dev_reboot_status[vdevR]['status']:
            ip_res = cvp_clnt.ipConnectivityTest(dev_reboot_status[vdevR]['IP'])
            if 'data' in ip_res:
                pS("OK", "{0} is back online".format(vdevR))
                dev_reboot_status[vdevR]['status'] = True
            else:
                pS("INFO", "Waiting for {0} to comeback online... Checking again in {1} seconds.".format(vdevR, DELAYTIMER))
                sleep(DELAYTIMER)
    # Grab container mappings
    eos_cnt_map = eosContainerMapper(cvp_yaml['cvp_info']['containers'])
    # Get EOS info for devices needing to be updated
    eos_info = getEosDevice(atd_yaml['topology'], atd_yaml['nodes']['veos'], eos_cnt_map, vdevs)
    # Add all devices to be reset into CVP
    cvp_clnt.addDeviceInventory(tmp_veos_ips)
    # Iterate through EOS Objects that need to be reset
    for eos in eos_info:
        provisionDevice(cvp_clnt, eos)
    cvp_clnt.saveTopology()
    cvp_clnt.getAllTasks("pending")
    pS("OK", "Executing all tasks")
    cvp_clnt.execAllTasks("pending")
    pS("OK", "Tasks executed")
    sleep(5)
    # All tasks should complete successfully, but need to check for failed tasks
    f_vdevs = [] # List to contain failed devices
    cvp_clnt.getAllTasks("failed")
    pS("OK", "Checking for failed tasks")
    if cvp_clnt.tasks['failed']:
        pS("INFO", "Found failed tasks")
        tmp_veos_ips = []
        # Iterate through list of failed tasks, remove device and add hostname to f_vdevs for re-provisioning
        for ftask in cvp_clnt.tasks['failed']:
            f_hostname = ftask['workOrderDetails']['netElementHostName'].split('.')[0]
            if f_hostname in vdevs:
                cvp_clnt.deleteDevices(ftask['netElementId'])
                f_vdevs.append(f_hostname)
                tmp_veos_ips.append(re_veos[f_hostname]['internal_ip'])
        cvp_clnt.cancelTasks("failed")
        pS("INFO", "Tasks failed for the following devices: {0}...Retrying".format(", ".join(f_vdevs)))
        cvp_clnt.saveTopology()
        # Get EOS info for devices needing to be re-added
        eos_info = getEosDevice(atd_yaml['topology'], atd_yaml['nodes']['veos'], eos_cnt_map, f_vdevs)
        # Re-Add all devices that previously failed back into CVP
        cvp_clnt.addDeviceInventory(tmp_veos_ips)
        # Iterate through EOS Objects that need to be re-added
        for eos in eos_info:
            provisionDevice(cvp_clnt, eos)
        cvp_clnt.saveTopology()
        cvp_clnt.getAllTasks("pending")
        cvp_clnt.execAllTasks("pending")
    else:
        pS("OK", "No failed tasks found.")
    cvp_clnt.execLogout()
    pS("OK", "Closed connection to CVP")

if __name__ == '__main__':
    syslog.openlog(logoption=syslog.LOG_PID)
    pS("OK", "Starting...")
    u_opts = argparse.ArgumentParser()
    u_opts.add_argument("-d", type=str, help="List of devies to reset:", choices=dev_list + ['all'], nargs='+', required=True)

    args = u_opts.parse_args()
    vdevs = args.d
    if 'all' in vdevs:
        res_dev = dev_list
    else:
        res_dev = vdevs
    main(res_dev)
    pS("OK", "Restore completed for {0}".format(", ".join(res_dev)))
