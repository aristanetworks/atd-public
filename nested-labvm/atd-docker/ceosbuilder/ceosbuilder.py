#!/usr/bin/env python3

from ruamel.yaml import YAML
from time import sleep
from os.path import exists
from os import makedirs
import argparse
import random
import secrets


FILE_TOPO = '/etc/atd/ACCESS_INFO.yaml'
REPO_PATH = '/opt/atd/'
CEOS_PATH = '/opt/ceos/'
CEOS_NODES = CEOS_PATH + 'nodes'
CEOS_SCRIPTS = CEOS_PATH + 'scripts/'
REPO_TOPO = REPO_PATH + 'topologies/'
AVAIL_TOPO = REPO_TOPO + 'available_topo.yaml'
MGMT_BRIDGE = 'vmgmt'
sleep_delay = 30
STOP_WAIT = 0
NOTIFY_BASE = 1250
CEOS_VERSION = '4.30.1F'
REGIS_PATH = 'us.gcr.io/beta-atds'
MTU = 10000
VETH_PAIRS = []
CEOS = {}
HOSTS = {}

ALL_MACS = []
CEOS_IDS = []
CEOS_MAPPER = {}
CEOS_LINKS = {}

DEVICE_INFO = ["\n# Device Info Mapping\n# =====================\n"]
NOTIFY_ADJUST = """
echo "fs.inotify.max_user_instances = {notify_instances}" > /etc/sysctl.d/99-zatd.conf
sysctl -w fs.inotify.max_user_instances={notify_instances}
"""


class CEOS_NODE():
    def __init__(self, node_name, node_ip, node_mac, node_neighbors, _tag, image, mgmt_mac=False):
        self.name = node_name
        self.ip = node_ip
        self.tag = _tag.lower()
        self.image = image
        self.ceos_name = self.tag + self.name
        self.intfs = {}
        self.dev_id = CEOS_MAPPER[self.name]
        self.portMappings(node_neighbors)
        if mgmt_mac:
            self.mgmt_mac = node_mac
            self.system_mac = generateMac()
        else:
            self.mgmt_mac = generateMac()
            self.system_mac = node_mac

    def portMappings(self, node_neighbors):
        """
        Function to create port mappings.
        """
        for intf in node_neighbors:
            lport = intf['port'].replace('/', '_')
            rport = intf['neighborPort'].replace('/', '_')
            rneigh = f"{self.tag}{CEOS_MAPPER[intf['neighborDevice']]}"
            _vethCheck = checkVETH(f"{self.tag}{self.dev_id}{lport}", f"{rneigh}{rport}")
            if _vethCheck['status']:
                pS("OK", f"Found Patch Cable for {self.name} {lport} to {intf['neighborDevice']} {rport} will be created.")
                VETH_PAIRS.append(_vethCheck['name'])
            self.intfs[intf['port']] = {
                'veth': _vethCheck['name'],
                'port': lport
            }

class HOST_NODE():
    def __init__(self, node_name, node_ip, node_mask, node_gw, node_neighbors, _tag, image):
        self.name = node_name
        self.ip = node_ip
        self.mask = node_mask
        self.gw = node_gw
        self.tag = _tag.lower()
        self.c_name = self.tag + self.name
        self.image = image
        self.ceos_name = self.tag + self.name
        self.intfs = {}
        self.dev_id = CEOS_MAPPER[self.name]
        self.portMappings(node_neighbors)

    def portMappings(self, node_neighbors):
        """
        Function to create port mappings.
        """
        for intf in node_neighbors:
            lport = intf['port'].replace('/', '_')
            rport = intf['neighborPort'].replace('/', '_')
            rneigh = f"{self.tag}{CEOS_MAPPER[intf['neighborDevice']]}"
            _vethCheck = checkVETH(f"{self.tag}{self.dev_id}{lport}", f"{rneigh}{rport}")
            if _vethCheck['status']:
                pS("OK", f"Found Patch Cable for {self.name} {lport} to {intf['neighborDevice']} {rport} will be created.")
                VETH_PAIRS.append(_vethCheck['name'])
            self.intfs[intf['port']] = {
                'veth': _vethCheck['name'],
                'port': lport
            }

def generateMac():
    """
    Function to generate a unique MAC Address.
    This would be used to create a unique system MAC in a topology.
    """
    _tmp_mac = f"00:1c:73:{hex(random.randint(0, 255))[2:]}:{hex(random.randint(0, 255))[2:]}:{hex(random.randint(0, 255))[2:]}"
    while True:
        if _tmp_mac not in ALL_MACS:
            ALL_MACS.append(_tmp_mac)
            return(_tmp_mac)
        else:
            print("Duplicate")
            _tmp_mac = f"00:1c:73:{hex(random.randint(0, 255))[2:]}:{hex(random.randint(0, 255))[2:]}:{hex(random.randint(0, 255))[2:]}"

def parseNames(devName):
    """
    Function to parse and consolidate name.
    """
    alpha = ''
    numer = ''
    for char in devName:
        if char.isalpha():
            alpha += char
        elif char.isdigit():
            numer += char
        elif char == "/":
            numer += "_"
    if 'ethernet'in devName.lower():
        dev_name = 'et{0}'.format(numer)
    else:
        dev_name = devName
    devInfo = {
        'name': devName,
        'code': dev_name
    }
    return(devInfo)

def getDevID():
    """
    Function to generate and set a unique device ID for veth pair usage
    """
    while True:
        _tmp_uuid = secrets.token_hex(2)
        if _tmp_uuid not in CEOS_IDS:
            return(_tmp_uuid)

def checkVETH(dev1, dev2):
    """
    Function to check veth pairs
    """
    global VETH_PAIRS
    _addVETH = True
    veth_name = '{0}-{1}'.format(dev1, dev2)
    for _veth in VETH_PAIRS:
        if dev1 in _veth and dev2 in _veth:
            _addVETH = False
            return({
                'status': _addVETH,
                'name': _veth
            })
    return({
        'status': _addVETH,
        'name': veth_name
    })
        
def checkDir(path):
    """
    Function to check if a destination directory exists.
    """
    if not exists(path):
        try:
            makedirs(path)
            return(True)
        except:
            return(False)
    else:
        return(True)

def generateMac():
    """
    Function to generate a unique MAC Address.
    This would be used to create a unique system MAC in a topology.
    """
    _tmp_mac = f"00:1c:73:{hex(random.randint(0, 255))[2:]}:{hex(random.randint(0, 255))[2:]}:{hex(random.randint(0, 255))[2:]}"
    while True:
        if _tmp_mac not in ALL_MACS:
            ALL_MACS.append(_tmp_mac)
            return(_tmp_mac)
        else:
            print("Duplicate")
            _tmp_mac = f"00:1c:73:{hex(random.randint(0, 255))[2:]}:{hex(random.randint(0, 255))[2:]}:{hex(random.randint(0, 255))[2:]}"

def createMac(dev_id):
    """
    Function to build dev specific MAC Address.
    """
    base = "00:1c:73:{0}:c6:01"
    if dev_id < 10:
        dev_mac = 'b{0}'.format(dev_id)
    elif dev_id >= 10 and dev_id < 20:
        dev_mac = 'c{0}'.format(dev_id - 10)
    elif dev_id >=20 and dev_id < 30:
        dev_mac = 'd{0}'.format(dev_id - 20)
    elif dev_id >=30 and dev_id < 40:
        dev_mac = 'e{0}'.format(dev_id - 30)
    elif dev_id >=40 and dev_id < 50:
        dev_mac = 'f{0}'.format(dev_id - 40)
    return(base.format(dev_mac))

def pS(mstat,mtype):
    """
    Function to send output from service file to Syslog
    """
    mmes = "\t" + mtype
    print("[{0}] {1}".format(mstat,mmes.expandtabs(7 - len(mstat))))

def main(args):
    """
    Main Function to build out cEOS files.
    """
    create_output = []
    startup_output = []
    stop_output = []
    delete_output = []
    delete_net_output = []
    upgrade_output = []
    
    # ==========================
    # rLab specific Var
    # ==========================
    container_runtime = "docker"
    registry_cmd = f"{REGIS_PATH}/"

    # Perform check on Container Runtime
    if container_runtime == "docker":
        pS("INFO", "Docker will be orchestrating the cEOS topology")
        cnt_cmd = "docker"
        cnt_log = "--log-driver local --log-opt max-size="
    else:
        pS("INFO", "Podman will be orchestrating the cEOS topology")
        cnt_cmd = "sudo podman"
        cnt_log = "--log-opt max-size="
        
    # ==========================
    # Existing VARs
    # ==========================

    _CEOS = False
    while True:
        if exists(FILE_TOPO):
            break
        else:
            sleep(sleep_delay)
    try:
        host_yaml = YAML().load(open(FILE_TOPO, 'r'))
        TOPO_TAG = host_yaml['topology']
        _tmp = TOPO_TAG.split('-')
        _tag = ""
        for _char in _tmp:
            _tag += _char[0].lower()
    except:
        print("File not found")
    if 'eos_type' in host_yaml:
        if host_yaml['eos_type'] == 'ceos':
            _CEOS = True

    if _CEOS:
        try:
            CEOS_VERSION = host_yaml['version'].upper()
        except:
            pS("INFO", "Version parameter not found.")
        if args.topo:
            FILE_BUILD = YAML().load(open(REPO_TOPO + TOPO_TAG + '/topo_build.yml', 'r'))
        else:
            FILE_BUILD = YAML().load(open('ceos_build.yml', 'r'))
        
        # Grab Topo information

        LINKS = FILE_BUILD['links']
        NODES = FILE_BUILD['nodes']
        if 'hosts' in FILE_BUILD:
            hosts = FILE_BUILD['hosts']
        else:
            hosts = []
        # Check for 32 or 64 bit EOS image to use
        try:
            if FILE_BUILD["images"]["64-bit"]:
                ceos_build = "ceosimage-64"
            else:
                ceos_build = "ceosimage"
        except:
            ceos_build = "ceosimage"

        # Load and Gather network Link information
        pS("INFO", "Gathering patch cable lengths and quantities...")
        for _link in LINKS:
            # Map out links
            _sideA = _link[0][0]
            _portA = _link[0][1]
            _sideB = _link[1][0]
            _portB = _link[1][1]
            if _sideA in CEOS_LINKS:
                CEOS_LINKS[_sideA].append({
                    'port': _portA,
                    'neighborPort': _portB,
                    'neighborDevice': _sideB
                })
            else:
                CEOS_LINKS[_sideA] = [{
                    'port': _portA,
                    'neighborPort': _portB,
                    'neighborDevice': _sideB
                }]
            if _sideB in CEOS_LINKS:
                CEOS_LINKS[_sideB].append({
                    'port': _portB,
                    'neighborPort': _portA,
                    'neighborDevice': _sideA
                })
            else:
                CEOS_LINKS[_sideB] = [{
                    'port': _portB,
                    'neighborPort': _portA,
                    'neighborDevice': _sideA
                }]

        # Generate Unique IDs for container hosts
        pS("INFO", "Examining devices for topology")
        if hosts:
            for _container_node in (NODES + hosts):
                _node_name = list(_container_node.keys())[0]
                _container_uid = getDevID()
                CEOS_IDS.append(_container_uid)
                CEOS_MAPPER[_node_name] = _container_uid
        else:
            for _container_node in NODES:
                _node_name = list(_container_node.keys())[0]
                _container_uid = getDevID()
                CEOS_IDS.append(_container_uid)
                CEOS_MAPPER[_node_name] = _container_uid

        # Load cEOS nodes specific information
        for _node in NODES:
            try:
                _node_ip = _node['ip_addr']
            except KeyError:
                _node_ip = ""
            _node_name = list(_node.keys())[0]
            CEOS[_node_name] = CEOS_NODE(_node_name, _node_ip, _node['mac'], CEOS_LINKS[_node_name], _tag, CEOS_VERSION)
            DEVICE_INFO.append(f"# {_node_name} = {CEOS[_node_name].tag}{CEOS[_node_name].dev_id}\n")
        # Load Host nodes specific information
        if hosts:
            for _host in hosts:
                _host_name = list(_host.keys())[0]
                HOSTS[_host_name] = HOST_NODE(_host_name, _host['ip_addr'], _host['mask'], _host['gateway'], CEOS_LINKS[_host_name], _tag, host_image)
                DEVICE_INFO.append(f"# {_host_name} = {HOSTS[_host_name].tag}{HOSTS[_host_name].dev_id}\n")

        # Update NOTIFY adjust for instances
        NOTIFY_ADD = NOTIFY_ADJUST.format(
            notify_instances = NOTIFY_BASE * len(NODES)
        )
        # Check for CEOS Scripts Directory
        if checkDir(CEOS_SCRIPTS):
            pS("OK", "Directory is present now.")
        else:
            pS("iBerg", "Error creating directory.")
        
        create_output.append("#!/bin/bash\n")
        create_output += DEVICE_INFO
        create_output.append(NOTIFY_ADD)
        create_output.append(f"sudo ip netns add {_tag}\n")
        startup_output.append("#!/bin/bash\n")
        startup_output += DEVICE_INFO
        startup_output.append(NOTIFY_ADD)
        stop_output.append("#!/bin/bash\n")
        stop_output += DEVICE_INFO
        delete_output.append("#!/bin/bash\n")
        delete_output += DEVICE_INFO
        startup_output.append(f"sudo ip netns add {_tag} 1> /dev/null 2> /dev/null\n")
        delete_net_output.append(f"sudo ip netns delete {_tag} 1> /dev/null 2> /dev/null\n")
        # Get the veths created
        create_output.append("# Creating veths\n")
        upgrade_output.append("#!/bin/bash\n")
        upgrade_output.append("EOS_TYPE=$(cat /etc/atd/ACCESS_INFO.yaml | python3 -m shyaml get-value version)\n")

        for _veth in VETH_PAIRS:
            _v1, _v2 = _veth.split("-")
            create_output.append(f"sudo ip link add {_v1} type veth peer name {_v2}\n")
            startup_output.append(f"sudo ip link add {_v1} type veth peer name {_v2}\n")
            # delete_output.append(f"sudo ip link delete {_v1} type veth peer name {_v2}\n")
        create_output.append("#\n#\n# Creating anchor containers\n#\n")
        # Create initial cEOS anchor containers
        create_output.append("# Checking to make sure topo config directory exists\n")
        create_output.append(f'if ! [ -d "{CEOS_NODES}" ]; then mkdir {CEOS_NODES}; fi\n')
        for _node in CEOS:
            # Add in code to perform check in configs directory and create a basis for ceos-config
            create_output.append(f"echo \"Racking and Stacking {_node}\"\n")
            create_output.append("# Checking for configs directory for each cEOS node\n")
            create_output.append(f'if ! [ -d "{CEOS_NODES}/{_node}" ]; then mkdir {CEOS_NODES}/{_node}; fi\n')
            create_output.append(f'if ! [ -f "{CEOS_NODES}/{_node}/ceos-config" ]; then ')
            create_output.append("# Creating the ceos-config file.\n")
            create_output.append(f'echo "SERIALNUMBER={CEOS[_node].ceos_name}" > {CEOS_NODES}/{_node}/ceos-config\n')
            create_output.append(f'echo "SYSTEMMACADDR={CEOS[_node].system_mac}" >> {CEOS_NODES}/{_node}/ceos-config\n')
            create_output.append('fi\n')
            # Creating anchor containers
            _dev_name_adusted = CEOS[_node].ceos_name.replace("-", "_")
            create_output.append(f"echo \"Gathering patch cables for {_node}\"\n")
            create_output.append("# Getting {0} nodes plumbing\n".format(_node))
            create_output.append(f"{cnt_cmd} run -d --restart=always {cnt_log}10k --name={CEOS[_node].ceos_name}-net --net=none busybox /bin/init 1> /dev/null 2> /dev/null\n")
            startup_output.append(f"{cnt_cmd} start {CEOS[_node].ceos_name}-net 1> /dev/null 2> /dev/null\n")
            create_output.append(f"{_dev_name_adusted}pid=$({cnt_cmd} inspect --format '{{{{.State.Pid}}}}' {CEOS[_node].ceos_name}-net)\n")
            create_output.append(f"sudo ln -sf /proc/${{{_dev_name_adusted}pid}}/ns/net /var/run/netns/{CEOS[_node].tag}{CEOS[_node].dev_id}\n")
            # Stop cEOS containers
            delete_output.append(f"echo \"Pulling power and removing patch cables from {_node}\"\n")
            stop_output.append(f"echo \"Pulling power from {_node}\"\n")
            startup_output.append(f"{cnt_cmd} stop -t {STOP_WAIT} {CEOS[_node].ceos_name} 1> /dev/null 2> /dev/null\n")
            stop_output.append(f"{cnt_cmd} stop -t {STOP_WAIT} {CEOS[_node].ceos_name} 1> /dev/null 2> /dev/null\n")
            stop_output.append(f"{cnt_cmd} stop -t {STOP_WAIT} {CEOS[_node].ceos_name}-net 1> /dev/null 2> /dev/null\n")
            delete_output.append(f"{cnt_cmd} stop -t {STOP_WAIT} {CEOS[_node].ceos_name} 1> /dev/null 2> /dev/null\n")
            delete_output.append(f"{cnt_cmd} stop -t {STOP_WAIT} {CEOS[_node].ceos_name}-net 1> /dev/null 2> /dev/null\n")
            # Remove cEOS containers
            startup_output.append(f"{cnt_cmd} rm {CEOS[_node].ceos_name} 1> /dev/null 2> /dev/null\n")
            delete_output.append(f"{cnt_cmd} rm {CEOS[_node].ceos_name} 1> /dev/null 2> /dev/null\n")
            delete_output.append(f"{cnt_cmd} rm {CEOS[_node].ceos_name}-net 1> /dev/null 2> /dev/null\n")
            delete_net_output.append(f"sudo rm -rf /var/run/netns/{CEOS[_node].tag}{CEOS[_node].dev_id}\n")
            startup_output.append(f"{_dev_name_adusted}pid=$({cnt_cmd} inspect --format '{{{{.State.Pid}}}}' {CEOS[_node].ceos_name}-net)\n")
            startup_output.append(f"sudo ln -sf /proc/${{{_dev_name_adusted}pid}}/ns/net /var/run/netns/{CEOS[_node].tag}{CEOS[_node].dev_id}\n")
            create_output.append(f"# Connecting cEOS containers together\n")
            # Output veth commands
            for _intf in CEOS[_node].intfs:
                _tmp_intf = CEOS[_node].intfs[_intf]
                if CEOS[_node].dev_id in  _tmp_intf['veth'].split('-')[0]:
                    create_output.append(f"echo \"Plugged patch cable into {_node} port {_tmp_intf['port']}\"\n")
                    create_output.append(f"sudo ip link set {_tmp_intf['veth'].split('-')[0]} netns {CEOS[_node].tag}{CEOS[_node].dev_id} name {_tmp_intf['port']} up\n")
                    startup_output.append(f"sudo ip link set {_tmp_intf['veth'].split('-')[0]} netns {CEOS[_node].tag}{CEOS[_node].dev_id} name {_tmp_intf['port']} up\n")
                else:
                    create_output.append(f"echo \"Plugged patch cable into {_node} port {_tmp_intf['port']}\"\n")
                    create_output.append(f"sudo ip link set {_tmp_intf['veth'].split('-')[1]} netns {CEOS[_node].tag}{CEOS[_node].dev_id} name {_tmp_intf['port']} up\n")
                    startup_output.append(f"sudo ip link set {_tmp_intf['veth'].split('-')[1]} netns {CEOS[_node].tag}{CEOS[_node].dev_id} name {_tmp_intf['port']} up\n")
            # Get MGMT VETHS
            create_output.append(f"sudo ip link add {CEOS[_node].tag}{CEOS[_node].dev_id}-eth0 type veth peer name {CEOS[_node].tag}{CEOS[_node].dev_id}-mgmt\n")
            create_output.append(f"sudo ip link set {CEOS[_node].tag}{CEOS[_node].dev_id}-eth0 netns {CEOS[_node].tag}{CEOS[_node].dev_id} name eth0 up\n")
            # create_output.append(f"sudo ip netns exec {CEOS[_node].tag}{CEOS[_node].dev_id} ip link set dev eth0 down\n")
            # create_output.append(f"sudo ip netns exec {CEOS[_node].tag}{CEOS[_node].dev_id} ip link set dev eth0 address {CEOS[_node].mgmt_mac}\n")
            create_output.append(f"sudo ip netns exec {CEOS[_node].tag}{CEOS[_node].dev_id} ip link set dev eth0 up\n")
            create_output.append(f"sudo ip link set {CEOS[_node].tag}{CEOS[_node].dev_id}-mgmt up\n")
            create_output.append("sleep 1\n")
            startup_output.append(f"sudo ip link add {CEOS[_node].tag}{CEOS[_node].dev_id}-eth0 type veth peer name {CEOS[_node].tag}{CEOS[_node].dev_id}-mgmt\n")
            startup_output.append(f"sudo ip link set {CEOS[_node].tag}{CEOS[_node].dev_id}-eth0 netns {CEOS[_node].tag}{CEOS[_node].dev_id} name eth0 up\n")
            # startup_output.append(f"sudo ip netns exec {CEOS[_node].tag}{CEOS[_node].dev_id} ip link set dev eth0 down\n")
            # startup_output.append(f"sudo ip netns exec {CEOS[_node].tag}{CEOS[_node].dev_id} ip link set dev eth0 address {CEOS[_node].mgmt_mac}\n")
            startup_output.append(f"sudo ip netns exec {CEOS[_node].tag}{CEOS[_node].dev_id} ip link set dev eth0 up\n")
            startup_output.append(f"sudo ip link set {CEOS[_node].tag}{CEOS[_node].dev_id}-mgmt up\n")
            startup_output.append("sleep 1\n")
            # Perform check if mgmt network is available
            if MGMT_BRIDGE:
                create_output.append(f"sudo brctl addif {MGMT_BRIDGE} {CEOS[_node].tag}{CEOS[_node].dev_id}-mgmt\n")
                startup_output.append(f"sudo brctl addif {MGMT_BRIDGE} {CEOS[_node].tag}{CEOS[_node].dev_id}-mgmt\n")
                create_output.append(f"echo \"Powering on {_node}\"\n")
                startup_output.append(f"echo \"Powering on {_node}\"\n")
                upgrade_output.append(f"echo \"Upgrading {_node}\"\n")
                upgrade_output.append(f"{cnt_cmd} stop {_node}\n")
                upgrade_output.append(f"{cnt_cmd} rm {_node}\n")
                if container_runtime == "docker":
                    create_output.append(f"{cnt_cmd} run -d --name={CEOS[_node].ceos_name} {cnt_log}1m --net=container:{CEOS[_node].ceos_name}-net --ip {CEOS[_node].ip} --privileged -v /etc/sysctl.d/99-zceos.conf:/etc/sysctl.d/99-zceos.conf:ro -v {CEOS_NODES}/{_node}:/mnt/flash:Z -e INTFTYPE=et -e MGMT_INTF=eth0 -e ETBA=1 -e CEOS=1 -e EOS_PLATFORM=ceoslab -e container=docker -i -t {registry_cmd}{ceos_build}:{CEOS[_node].image} /sbin/init systemd.setenv=INTFTYPE=et systemd.setenv=MGMT_INTF=eth0 systemd.setenv=ETBA=1 systemd.setenv=CEOS=1 systemd.setenv=EOS_PLATFORM=ceoslab systemd.setenv=container=docker 1> /dev/null 2> /dev/null\n")
                    startup_output.append(f"{cnt_cmd} run -d --name={CEOS[_node].ceos_name} {cnt_log}1m --net=container:{CEOS[_node].ceos_name}-net --ip {CEOS[_node].ip} --privileged -v /etc/sysctl.d/99-zceos.conf:/etc/sysctl.d/99-zceos.conf:ro -v {CEOS_NODES}/{_node}:/mnt/flash:Z -e INTFTYPE=et -e MGMT_INTF=eth0 -e ETBA=1 -e CEOS=1 -e EOS_PLATFORM=ceoslab -e container=docker -i -t {registry_cmd}{ceos_build}:{CEOS[_node].image} /sbin/init systemd.setenv=INTFTYPE=et systemd.setenv=MGMT_INTF=eth0 systemd.setenv=ETBA=1 systemd.setenv=CEOS=1 systemd.setenv=EOS_PLATFORM=ceoslab systemd.setenv=container=docker 1> /dev/null 2> /dev/null\n")
                    upgrade_output.append(f"{cnt_cmd} run -d --name={CEOS[_node].ceos_name} {cnt_log}1m --net=container:{CEOS[_node].ceos_name}-net --ip {CEOS[_node].ip} --privileged -v /etc/sysctl.d/99-zceos.conf:/etc/sysctl.d/99-zceos.conf:ro -v {CEOS_NODES}/{_node}:/mnt/flash:Z -e INTFTYPE=et -e MGMT_INTF=eth0 -e ETBA=1 -e CEOS=1 -e EOS_PLATFORM=ceoslab -e container=docker -i -t {registry_cmd}{ceos_build}:{CEOS[_node].image} /sbin/init systemd.setenv=INTFTYPE=et systemd.setenv=MGMT_INTF=eth0 systemd.setenv=ETBA=1 systemd.setenv=CEOS=1 systemd.setenv=EOS_PLATFORM=ceoslab systemd.setenv=container=docker 1> /dev/null 2> /dev/null\n")
                else:
                    create_output.append(f"{cnt_cmd} run -d --name={CEOS[_node].ceos_name} {cnt_log}1m --net=container:{CEOS[_node].ceos_name}-net --privileged -v /etc/sysctl.d/99-zceos.conf:/etc/sysctl.d/99-zceos.conf:ro -v {CEOS_NODES}/{_node}:/mnt/flash:Z -e INTFTYPE=et -e MGMT_INTF=eth0 -e ETBA=1 -e CEOS=1 -e EOS_PLATFORM=ceoslab -e container=docker -i -t {registry_cmd}{ceos_build}:{CEOS[_node].image} /sbin/init systemd.setenv=INTFTYPE=et systemd.setenv=MGMT_INTF=eth0 systemd.setenv=ETBA=1 systemd.setenv=CEOS=1 systemd.setenv=EOS_PLATFORM=ceoslab systemd.setenv=container=docker 1> /dev/null 2> /dev/null\n")
                    startup_output.append(f"{cnt_cmd} run -d --name={CEOS[_node].ceos_name} {cnt_log}1m --net=container:{CEOS[_node].ceos_name}-net --privileged -v /etc/sysctl.d/99-zceos.conf:/etc/sysctl.d/99-zceos.conf:ro -v {CEOS_NODES}/{_node}:/mnt/flash:Z -e INTFTYPE=et -e MGMT_INTF=eth0 -e ETBA=1 -e CEOS=1 -e EOS_PLATFORM=ceoslab -e container=docker -i -t {registry_cmd}{ceos_build}:{CEOS[_node].image} /sbin/init systemd.setenv=INTFTYPE=et systemd.setenv=MGMT_INTF=eth0 systemd.setenv=ETBA=1 systemd.setenv=CEOS=1 systemd.setenv=EOS_PLATFORM=ceoslab systemd.setenv=container=docker 1> /dev/null 2> /dev/null\n")                    
                    upgrade_output.append(f"{cnt_cmd} run -d --name={CEOS[_node].ceos_name} {cnt_log}1m --net=container:{CEOS[_node].ceos_name}-net --privileged -v /etc/sysctl.d/99-zceos.conf:/etc/sysctl.d/99-zceos.conf:ro -v {CEOS_NODES}/{_node}:/mnt/flash:Z -e INTFTYPE=et -e MGMT_INTF=eth0 -e ETBA=1 -e CEOS=1 -e EOS_PLATFORM=ceoslab -e container=docker -i -t {registry_cmd}{ceos_build}:{CEOS[_node].image} /sbin/init systemd.setenv=INTFTYPE=et systemd.setenv=MGMT_INTF=eth0 systemd.setenv=ETBA=1 systemd.setenv=CEOS=1 systemd.setenv=EOS_PLATFORM=ceoslab systemd.setenv=container=docker 1> /dev/null 2> /dev/null\n")                    
            else:
                create_output.append(f"{cnt_cmd} run -d --name={CEOS[_node].ceos_name} {cnt_log}1m --net=container:{CEOS[_node].ceos_name}-net --privileged -v /etc/sysctl.d/99-zceos.conf:/etc/sysctl.d/99-zceos.conf:ro -v {CEOS_NODES}/{_node}:/mnt/flash:Z -e INTFTYPE=et -e MGMT_INTF=eth0 -e ETBA=1 -e CEOS=1 -e EOS_PLATFORM=ceoslab -e container=docker -i -t {registry_cmd}{ceos_build}:{CEOS[_node].image} /sbin/init systemd.setenv=INTFTYPE=et systemd.setenv=MGMT_INTF=eth0 systemd.setenv=ETBA=1 systemd.setenv=CEOS=1 systemd.setenv=EOS_PLATFORM=ceoslab systemd.setenv=container=docker 1> /dev/null 2> /dev/null\n")
                startup_output.append(f"{cnt_cmd} run -d --name={CEOS[_node].ceos_name} {cnt_log}1m --net=container:{CEOS[_node].ceos_name}-net --privileged -v /etc/sysctl.d/99-zceos.conf:/etc/sysctl.d/99-zceos.conf:ro -v {CEOS_NODES}/{_node}:/mnt/flash:Z -e INTFTYPE=et -e MGMT_INTF=eth0 -e ETBA=1 -e CEOS=1 -e EOS_PLATFORM=ceoslab -e container=docker -i -t {registry_cmd}{ceos_build}:{CEOS[_node].image} /sbin/init systemd.setenv=INTFTYPE=et systemd.setenv=MGMT_INTF=eth0 systemd.setenv=ETBA=1 systemd.setenv=CEOS=1 systemd.setenv=EOS_PLATFORM=ceoslab systemd.setenv=container=docker 1> /dev/null 2> /dev/null\n")
                upgrade_output.append(f"echo \"Upgrading {_node}\"\n")
                upgrade_output.append(f"{cnt_cmd} stop {_node}\n")
                upgrade_output.append(f"{cnt_cmd} rm {_node}\n")
                upgrade_output.append(f"{cnt_cmd} run -d --name={CEOS[_node].ceos_name} {cnt_log}1m --net=container:{CEOS[_node].ceos_name}-net --privileged -v /etc/sysctl.d/99-zceos.conf:/etc/sysctl.d/99-zceos.conf:ro -v {CEOS_NODES}/{_node}:/mnt/flash:Z -e INTFTYPE=et -e MGMT_INTF=eth0 -e ETBA=1 -e CEOS=1 -e EOS_PLATFORM=ceoslab -e container=docker -i -t {registry_cmd}{ceos_build}:{CEOS[_node].image} /sbin/init systemd.setenv=INTFTYPE=et systemd.setenv=MGMT_INTF=eth0 systemd.setenv=ETBA=1 systemd.setenv=CEOS=1 systemd.setenv=EOS_PLATFORM=ceoslab systemd.setenv=container=docker 1> /dev/null 2> /dev/null\n")
        # Create initial host anchor containers
        create_output.append(f"echo \"Waiting on the server team to get their servers up and running...\"\n")
        startup_output.append(f"echo \"Waiting on the server team to get their servers up and running...\"\n")
        for _host in HOSTS:
            create_output.append(f"# Getting {_host} nodes plumbing\n")
            create_output.append(f"{cnt_cmd} run -d --restart=always {cnt_log}10k --name={HOSTS[_host].c_name}-net --net=none busybox /bin/init 1> /dev/null 2> /dev/null\n")
            startup_output.append(f"{cnt_cmd} start {HOSTS[_host].c_name}-net 1> /dev/null 2> /dev/null\n")
            create_output.append(f"{HOSTS[_host].c_name}pid=$({cnt_cmd} inspect --format '{{{{.State.Pid}}}}' {HOSTS[_host].c_name}-net)\n")
            create_output.append(f"sudo ln -sf /proc/${{{HOSTS[_host].c_name}pid}}/ns/net /var/run/netns/{HOSTS[_host].tag}{HOSTS[_host].dev_id}\n")
            # Stop host containers
            delete_output.append(f"echo \"Pulling power and removing patch cables from {_host}\"\n")
            stop_output.append(f"echo \"Pulling power from {_host}\"\n")
            startup_output.append(f"{cnt_cmd} stop -t {STOP_WAIT} {HOSTS[_host].c_name} 1> /dev/null 2> /dev/null\n")
            stop_output.append(f"{cnt_cmd} stop -t {STOP_WAIT} {HOSTS[_host].c_name} 1> /dev/null 2> /dev/null\n")
            stop_output.append(f"{cnt_cmd} stop -t {STOP_WAIT} {HOSTS[_host].c_name}-net 1> /dev/null 2> /dev/null\n")
            delete_output.append(f"{cnt_cmd} stop -t {STOP_WAIT} {HOSTS[_host].c_name} 1> /dev/null 2> /dev/null\n")
            delete_output.append(f"{cnt_cmd} stop -t {STOP_WAIT} {HOSTS[_host].c_name}-net 1> /dev/null 2> /dev/null\n")
            # Remove host containers
            startup_output.append(f"{cnt_cmd} rm {HOSTS[_host].c_name} 1> /dev/null 2> /dev/null\n")
            delete_output.append(f"{cnt_cmd} rm {HOSTS[_host].c_name} 1> /dev/null 2> /dev/null\n")
            delete_output.append(f"{cnt_cmd} rm {HOSTS[_host].c_name}-net 1> /dev/null 2> /dev/null\n")
            delete_net_output.append(f"sudo rm -rf /var/run/netns/{HOSTS[_host].tag}{HOSTS[_host].dev_id}\n")
            startup_output.append(f"{HOSTS[_host].c_name}pid=$({cnt_cmd} inspect --format '{{{{.State.Pid}}}}' {HOSTS[_host].c_name}-net) 1> /dev/null 2> /dev/null\n")
            startup_output.append(f"sudo ln -sf /proc/${{{HOSTS[_host].c_name}pid}}/ns/net /var/run/netns/{HOSTS[_host].tag}{HOSTS[_host].dev_id} 1> /dev/null 2> /dev/null\n")
            create_output.append("# Connecting host containers together\n")
            # Output veth commands
            for _intf in HOSTS[_host].intfs:
                _tmp_intf = HOSTS[_host].intfs[_intf]
                if HOSTS[_host].dev_id in  _tmp_intf['veth'].split('-')[0]:
                    create_output.append(f"echo \"Plugged patch cable into {_host} port {_tmp_intf['port']}\"\n")
                    create_output.append(f"sudo ip link set {_tmp_intf['veth'].split('-')[0]} netns {HOSTS[_host].tag}{HOSTS[_host].dev_id} name {_tmp_intf['port']} up\n")
                    startup_output.append(f"sudo ip link set {_tmp_intf['veth'].split('-')[0]} netns {HOSTS[_host].tag}{HOSTS[_host].dev_id} name {_tmp_intf['port']} up\n")
                else:
                    create_output.append(f"echo \"Plugged patch cable into {_host} port {_tmp_intf['port']}\"\n")
                    create_output.append(f"sudo ip link set {_tmp_intf['veth'].split('-')[1]} netns {HOSTS[_host].tag}{HOSTS[_host].dev_id} name {_tmp_intf['port']} up\n")
                    startup_output.append(f"sudo ip link set {_tmp_intf['veth'].split('-')[1]} netns {HOSTS[_host].tag}{HOSTS[_host].dev_id} name {_tmp_intf['port']} up\n")
            create_output.append(f"echo \"Powering on {_host}\"\n")
            startup_output.append(f"echo \"Powering on {_host}\"\n")
            create_output.append("sleep 1\n")
            create_output.append(f"{cnt_cmd} run -d --name={HOSTS[_host].c_name} --privileged {cnt_log}1m --net=container:{HOSTS[_host].c_name}-net -e HOSTNAME={HOSTS[_host].c_name} -e HOST_IP={HOSTS[_host].ip} -e HOST_MASK={HOSTS[_host].mask} -e HOST_GW={HOSTS[_host].gw} {registry_cmd}chost:{HOSTS[_host].image} ipnet 1> /dev/null 2> /dev/null\n")
            startup_output.append("sleep 1\n")
            startup_output.append(f"{cnt_cmd} run -d --name={HOSTS[_host].c_name} --privileged {cnt_log}1m --net=container:{HOSTS[_host].c_name}-net -e HOSTNAME={HOSTS[_host].c_name} -e HOST_IP={HOSTS[_host].ip} -e HOST_MASK={HOSTS[_host].mask} -e HOST_GW={HOSTS[_host].gw} {registry_cmd}chost:{HOSTS[_host].image} ipnet 1> /dev/null 2> /dev/null\n")

        create_output.append('touch {0}.ceos.txt'.format(CEOS_SCRIPTS))
        # startup_output.append('rm -- "$0"\n')

        # Create the initial deployment files
        with open(CEOS_SCRIPTS + 'Create.sh', 'w') as cout:
            for _create in create_output:
                cout.write(_create)
        with open(CEOS_SCRIPTS + 'Startup.sh', 'w') as cout:
            for _start in startup_output:
                cout.write(_start)
        with open(CEOS_SCRIPTS + 'Upgrade.sh', 'w') as cout:
            for _upgrade in upgrade_output:
                cout.write(_upgrade)
        with open(CEOS_SCRIPTS + 'Stop.sh', 'w') as cout:
            for _stop in stop_output:
                cout.write(_stop)
        with open(CEOS_SCRIPTS + 'Delete.sh', 'w') as cout:
            for _delete in delete_output:
                cout.write(_delete)
            for _delete in delete_net_output:
                cout.write(_delete)
    else:
        pS("OK", "Exiting as it is a non-cEOS topology.")

if __name__ == '__main__':
    pS('OK', 'Starting cEOS Builder')
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--topo", action="store_true", help="Use Topo of topology", default=False, required=False)
    parser.add_argument("-f", "--file", type=str, help="Custom Topology build file", default=None, required=False)
    args = parser.parse_args()
    #TODO add in logic to load custom build file. Default to tag's build file
    main(args)
    pS('OK', 'Complete!')
