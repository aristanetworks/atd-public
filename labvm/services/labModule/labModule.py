#!/usr/bin/env python3


from ruamel.yaml import YAML
from os import path, system
from time import sleep
import syslog

topo_file = '/etc/ACCESS_INFO.yaml'
CVP_CONFIG_FIILE = '/home/arista/.cvpState.txt'
pDEBUG = True
CONFIGURE_TOPOLOGY = "/usr/local/bin/ConfigureTopology.py"
APP_KEY = 'app'

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
    lab_topo = MODULES[atd_yaml[APP_KEY]]['topo']
    lab_module = MODULES[atd_yaml[APP_KEY]]['module']
    pS("INFO", "Configuring the lab for {0}".format(lab_module))
    system('echo -e "\n" | {0} -t {1} -l {2}'.format(CONFIGURE_TOPOLOGY, lab_topo, lab_module))
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
        if atd_yaml[APP_KEY] != 'none':
            # Check if module is in MODULES
            if atd_yaml[APP_KEY] in MODULES:
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
