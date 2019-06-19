#!/usr/bin/env python

from ruamel.yaml import YAML
from rcvpapi.rcvpapi import *
from time import sleep
from sys import exit
import paramiko, argparse, syslog, urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ACCESS = '/etc/ACCESS_INFO.yaml'
CVPINFO = '/home/arista/cvp/cvp_info.yaml'
BARE_CFGS = ['AAA']
pDEBUG = True
# List object to list available devices
dev_list = []
# Dict object to keep track of veos devices
re_veos = {}

# Cmds to copy bare startup to running
dev_cmds = """enable
copy startup-config running-config
"""
# Bare device specific config portion
dev_bare = """hostname {0}
!
interface Management1
   ip address {1}/24
!
management api http-commands
   no shutdown
"""

# Loading ACCESS_INFO
with open(ACCESS,'r') as atdyaml:
    atd_yaml = YAML().load(atdyaml)
    veos_devs = atd_yaml['nodes']['veos']
    TOPO = atd_yaml['topology']

for veos in veos_devs:
    dev_list.append(veos['hostname'])
    re_veos[veos['hostname']] = {'hostname':veos['hostname'],'internal_ip':veos['internal_ip'],'ip':veos['ip'],'cvpobj':""}

# Loading cvp_info.yaml
with open(CVPINFO,'r') as ci:
    cvp_yaml = YAML().load(ci)

def pushBareConfig(veos_host,veos_ip,veos_config):
    veos_ssh = paramiko.SSHClient()
    veos_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    veos_ssh.connect(hostname=veos_ip,username="root",password="",port="22220")
    veos_ssh.exec_command("echo '{0}' | tee /mnt/flash/startup-config".format(veos_config))
    #veos_ssh.exec_command("/sbin/reboot -f > /dev/null 2>&1 &")
    veos_ssh.exec_command('FastCli -c "{0}"'.format(dev_cmds))
    veos_ssh.close()

def conCVP():
    cvp_clnt = False
    for c_login in atd_yaml['login_info']['cvp']['shell']:
        if c_login['user'] == 'arista':
            while not cvp_clnt:
                try:
                    cvp_clnt = CVPCON(atd_yaml['nodes']['cvp'][0]['ip'],c_login['user'],c_login['pw'])
                    pS("OK","Connected to CVP at {0}".format(atd_yaml['nodes']['cvp'][0]['ip']))
                    return(cvp_clnt)
                except:
                    pS("ERROR","CVP is currently unavailable....Retrying in 30 seconds.")
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

def getEosDevice(topo,eosYaml,cvpMapper,veos_reset):
    """
    Function that Parses through the YAML file and creates a CVPSWITCH class object for each EOS device in the topo file.
    Parameters:
    topo = Topology for the ATD (required)
    eosYAML = vEOS portion of the ACCESS_INFO.yaml file (required)
    cvpMapper = Dict that maps EOS device to container (required)
    """
    EOS_DEV = []
    for dev in eosYaml:
        if dev['hostname'] in veos_reset:
            try:
                EOS_DEV.append(CVPSWITCH(dev['hostname'],dev['internal_ip'],cvpMapper[dev['hostname']]))
                checkContainer(cvpMapper[dev['hostname']])
            except:
                EOS_DEV.append(CVPSWITCH(dev['hostname'],dev['internal_ip']))
    return(EOS_DEV)

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

def main(vdevs):
    pS("INFO","Device{0} to be reset: {1}".format("s" if len(vdevs) > 1 else "",", ".join(vdevs)))
    bare_veos = ""
    # Used to store a list of IPs to be used for import into CVP
    tmp_veos_ips = []
    for b_cfg in BARE_CFGS:
        with open('/tmp/atd/topologies/{0}/configlets/{1}'.format(TOPO,b_cfg,'r')) as bcfg:
            bare_veos += bcfg.read()
    # Build device specific bare configurations
    for cur_veos in vdevs:
        tmp_veos_config = bare_veos + dev_bare.format(re_veos[cur_veos]['hostname'],re_veos[cur_veos]['internal_ip'])
        tmp_veos_ips.append(re_veos[cur_veos]['internal_ip'])
        # Push bare config to remote startup-config and reboot device
        pushBareConfig(cur_veos,re_veos[cur_veos]['ip'],tmp_veos_config)
    pS("OK","Configs pushed to: {0}".format(", ".join(vdevs)))
    pS("INFO","Devices Rebooting...This can take several minutes")
    # Create connection to CVP
    cvp_clnt = conCVP()
    eos_cnt_map = eosContainerMapper(cvp_yaml['cvp_info']['containers'])
    eos_info = getEosDevice(atd_yaml['topology'],atd_yaml['nodes']['veos'],eos_cnt_map,vdevs)
    cvp_clnt.addDeviceInventory(tmp_veos_ips)
    for eos in eos_info:
        # Check to see if the device has a target container
        if eos.targetContainerName:
            eos.updateContainer(cvp_clnt)
            if eos.targetContainerName != eos.parentContainer["name"]:
                cvp_clnt.moveDevice(eos) 
                cvp_clnt.genConfigBuilders(eos)
                if eos.hostname in cvp_yaml['cvp_info']['configlets']['netelements'].keys():
                    cvp_clnt.addDeviceConfiglets(eos,cvp_yaml['cvp_info']['configlets']['netelements'][eos.hostname])
                cvp_clnt.applyConfiglets(eos)
            else:
                pS("INFO","No container Move")
                cvp_clnt.genConfigBuilders(eos)
                if eos.hostname in cvp_yaml['cvp_info']['configlets']['netelements'].keys():
                    cvp_clnt.addDeviceConfiglets(eos,cvp_yaml['cvp_info']['configlets']['netelements'][eos.hostname])
                cvp_clnt.applyConfiglets(eos)

    cvp_clnt.saveTopology()
    cvp_clnt.getAllTasks("pending")
    cvp_clnt.execAllTasks("pending")
    
if __name__ == '__main__':
    syslog.openlog(logoption=syslog.LOG_PID)
    pS("OK","Starting...")
    u_opts = argparse.ArgumentParser()
    u_opts.add_argument("-d",type=str,help="List of devies to reset:",choices=dev_list + ['all'],nargs='+',required=True)

    args = u_opts.parse_args()
    vdevs = args.d 
    if 'all' in vdevs:
        res_dev = dev_list
    else:
        res_dev = vdevs
    main(res_dev)