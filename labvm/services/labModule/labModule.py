#!/usr/bin/env python3


from ruamel.yaml import YAML
from os import path, system
from time import sleep
from rcvpapi.rcvpapi import *
from subprocess import call, PIPE
import syslog
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from ConfigureTopology.ConfigureTopology import ConfigureTopology

topo_file = '/etc/ACCESS_INFO.yaml'
CVP_CONFIG_FIILE = '/home/arista/.cvpState.txt'
pDEBUG = True
APP_KEY = 'app'
sleep_delay = 30

# Module mapping for default_lab tag to map for use with ConfigureTopology
MODULES = {
    'mlag': {
        'topo': 'Datacenter',
        'module': 'mlag'
    },
    'bgp': {
        'topo': 'Datacenter',
        'module': 'bgp'
    },
    'l3ls': {
        'topo': 'Datacenter',
        'module': 'bgp'
    },
    'vxlan': {
        'topo': 'Datacenter',
        'module': 'vxlan'
    },
    'l2evpn': {
        'topo': 'Datacenter',
        'module': 'l2evpn'
    },
    'l3evpn': {
        'topo': 'Datacenter',
        'module': 'l3evpn'
    },
    'cvp': {
        'topo': 'Datacenter',
        'module': 'cvp'
    }
}

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

def pingHost(host_ip):
    """
    Function to send a single ping to a host to check reachability.
    Parameters:
    host_ip = IP Address for the host (str)
    """
    base_cmds = ['ping', '-c1', '-w1']
    ping_cmds = base_cmds + [host_ip]
    ping_host = call(ping_cmds, stdout=PIPE, stderr=PIPE)
    if ping_host:
        return(False)
    else:
        return(True)

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

def main(atd_yaml):
    """
    Main Function if CVP has been configured, and a default_lab has been
    specified in ACCESS_INFO.yaml.
    Parameters:
    atd_yaml = Ruamel.YAML object container of ACCESS_INFO 
    """
    # Check if CVP is configured in topo, if not perform a different check
    if 'cvp' in atd_yaml['nodes']:
        cvp_clnt = ""
        # Create connection to CVP
        for c_login in atd_yaml['login_info']['cvp']['shell']:
            if c_login['user'] == 'arista':
                while not cvp_clnt:
                    try:
                        cvp_clnt = CVPCON(atd_yaml['nodes']['cvp'][0]['ip'],c_login['user'],c_login['pw'])
                        pS("OK","Connected to CVP at {0}".format(atd_yaml['nodes']['cvp'][0]['ip']))
                    except:
                        pS("ERROR","CVP is currently unavailable....Retrying in {0} seconds.".format(sleep_delay))
                        sleep(sleep_delay)
        # Get CVP Inventory and iterate through all connected devices to verify connectivity
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
                else:
                    sleep(sleep_delay)
    else:
        # Get the current devices from ACCESS_INFO
        for vnode in atd_yaml['nodes']['veos']:
            while True:
                if pingHost(vnode['internal_ip']):
                    pS("OK", "{0} is up and reachable at {1}".format(vnode['hostname'], vnode['internal_ip']))
                    break
                else:
                    pS("INFO", "{0} is NOT reachable at {1}. Sleeping {2} seconds.".format(vnode['hostname'], vnode['internal_ip'], sleep_delay))
                    sleep(sleep_delay)
    pS("OK", "All Devices are registered and reachable.")

    # Continue to configure topology
    lab, mod = atd_yaml[APP_KEY].split('-')
    lab_topo = MODULES[mod]['topo']
    lab_module = MODULES[mod]['module']
    pS("INFO", "Configuring the lab for {0}".format(lab_module))
    ConfigureTopology(selected_menu=lab_topo,selected_lab=lab_module,public_module_flag=True)
    pS("OK", "Lab has been configured.")

if __name__ == '__main__':
    # Open Syslog
    syslog.openlog(logoption=syslog.LOG_PID)
    pS("OK","Starting...")
    # Perform check to see if a module has been assigned
    atd_yaml = getTopoInfo(topo_file)
    # Perform check to see if lab parameter is available
    if APP_KEY in atd_yaml:
        # Check to see if a value has been set for the parameter:
        if '-' in atd_yaml[APP_KEY]:
            # Split out the lab and module from app
            lab, mod = atd_yaml[APP_KEY].split('-')
            # Check if module is in MODULES
            if mod in MODULES:
                # Perform loop check to verify that CVP has been configured and cvpUpdated has completed.
                while not path.exists(CVP_CONFIG_FIILE):
                    # If it check hasn't passed, sleep 10 seconds.
                    sleep(10)
                # CVP has been configured and provisioned, continue on setting up the lab
                main(atd_yaml)
            else:
                pS("iBerg", "Module mapping is not available.")
        else:
            pS("OK","No default lab has been specified, exiting...")
    else:
        pS("OK", "The default_lab parameter was not found in ACCESS_INFO.yaml, exiting...")
