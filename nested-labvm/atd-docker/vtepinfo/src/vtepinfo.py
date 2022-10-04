#!/usr/bin/env python3

from datetime import datetime
from os.path import exists
from time import sleep
from ruamel.yaml import YAML
import requests


# =====================================
# Global Variables
# =====================================

SLEEP_DELAY = 10
COUNTER_THRESHOLD = 10
ATD_ACCESS_PATH = '/etc/atd/ACCESS_INFO.yaml'
VTEP_SCRIPT_PATH = '/etc/atd/.vtep.sh'
FUNC_STATE = 'https://us-central1-{0}.cloudfunctions.net/atd-state'

CMD_OUT = ["#!/bin/bash\n"]

def openYAML(fpath):
    """
    Function to open and read yaml file contents.
    """
    try:
        host_yaml = YAML().load(open(fpath, 'r'))
        return(host_yaml)
    except:
        return("File not available")

def checkProvisioned(full_file_path):
    if exists(full_file_path):
        return('init')
    else:
        return('post')

def pS(mtype):
    """
    Function to send output from service file to Syslog
    """
    cur_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mmes = "\t" + mtype
    print("[{0}] {1}".format(cur_dt, mmes.expandtabs(7 - len(cur_dt))))

def main():
    # Check if in init boot
    if checkProvisioned('/etc/atd/.init') == 'init':
        pS("Initial boot, will gather VTEP info")
        while True:
            access_yaml = openYAML(ATD_ACCESS_PATH)
            if 'project' and 'zone' and 'name' and 'atd_role' in access_yaml:
                pS("Necessary parameters exist, continuing")
                break
            else:
                pS("Necessary parameters do not exist")
                sleep(SLEEP_DELAY)
        # Gather topo variables
        project = access_yaml['project']
        name = access_yaml['name']
        zone = access_yaml['zone']
        atd_role = access_yaml['atd_role']
        function_state_url = FUNC_STATE.format(project)
        if atd_role == 'nodes':
            _self_state_url = f"{function_state_url}?function=state&instance={name}-eos&zone={zone}"
            _peer_state_url = f"{function_state_url}?function=state&instance={name}-cvp&zone={zone}"
        else:
            _self_state_url = f"{function_state_url}?function=state&instance={name}-cvp&zone={zone}"
            _peer_state_url = f"{function_state_url}?function=state&instance={name}-eos&zone={zone}"
        # Perform loop until Private IP is available
        while True:
            response_self = requests.get(_self_state_url)
            json_self = response_self.json()
            try:
                self_ip = json_self['privateIP']
                if self_ip and type(self_ip) == str:
                    break
                else:
                    pS(f"Did not get self_ip: {json_peer}")
            except:
                pS("Unable to get self IP")
            sleep(SLEEP_DELAY)
        pS("Received local IP")
        while True:
            response_peer = requests.get(_peer_state_url)
            json_peer = response_peer.json()
            try:
                peer_ip = json_peer['privateIP']
                if peer_ip and type(peer_ip) == str:
                    break
                else:
                    pS(f"Did not get peer_ip: {json_peer}")
            except:
                pS("Unable to get Peer IP")
            sleep(SLEEP_DELAY)
        pS("Received Peer IP")
        access_yaml['vtep_local'] = self_ip
        access_yaml['vtep_remote'] = peer_ip
        # Set commands
        CMD_OUT.append(f"ip link add vxlan10 type vxlan id 10  local {self_ip} remote {peer_ip}\n")
        CMD_OUT.append("brctl addif vmgmt vxlan10\n")
        CMD_OUT.append("ip link set vxlan10 up\n")
        YAML().dump(access_yaml, open(ATD_ACCESS_PATH, 'w'))
        with open(VTEP_SCRIPT_PATH, 'w') as vout:
            vout.writelines(CMD_OUT)
    else:
        pS("Post deploy, exiting")

if __name__ == "__main__":
    main()