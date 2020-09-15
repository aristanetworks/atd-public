#!/usr/bin/env python3

from ruamel.yaml import YAML
from time import sleep
from os.path import exists
from os import makedirs
import argparse


FILE_TOPO = '/etc/atd/ACCESS_INFO.yaml'
REPO_PATH = '/opt/atd/'
CEOS_PATH = '/opt/ceos/'
CEOS_NODES = CEOS_PATH + 'nodes'
CEOS_SCRIPTS = CEOS_PATH + 'scripts/'
REPO_TOPO = REPO_PATH + 'topologies/'
AVAIL_TOPO = REPO_TOPO + 'available_topo.yaml'
MGMT_BRIDGE = 'vmgmt'
sleep_delay = 30
CEOS_VERSION = '4.24.1.1F'

VETH_PAIRS = []
CEOS = {}


class CEOS_NODE():
    def __init__(self, node_name, node_ip, node_neighbors):
        self.name = node_name
        self.ip = node_ip
        self.intfs = {}
        self.portMappings(node_neighbors)
    def portMappings(self, node_neighbors):
        """
        Function to create port mappings.
        """
        for intf in node_neighbors:
            lport = parseNames(intf['port'])
            rport = parseNames(intf['neighborPort'])
            rneigh = parseNames(intf['neighborDevice'])
            _vethCheck = checkVETH('{0}{1}'.format(self.name, lport['code']), '{0}{1}'.format(rneigh['name'], rport['code']))
            if _vethCheck['status']:
                pS("OK", "VETH Pair {0} will be created.".format(_vethCheck['name']))
                VETH_PAIRS.append(_vethCheck['name'])
            self.intfs[intf['port']] = {
                'veth': _vethCheck['name'],
                'port': lport['code']
            }

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
    if 'ethernet'in devName.lower():
        dev_name = 'et{0}'.format(numer)
    else:
        dev_name = devName
    devInfo = {
        'name': devName,
        'code': dev_name
    }
    return(devInfo)

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


def createMac(dev_id):
    """
    Function to build dev specific MAC Address.
    """
    if dev_id < 10:
        return('b{0}'.format(dev_id))
    elif dev_id >= 10 and dev_id < 20:
        return('c{0}'.format(dev_id - 10))
    elif dev_id >=20 and dev_id < 30:
        return('d{0}'.format(dev_id - 20))

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
    _CEOS = False
    while True:
        if exists(FILE_TOPO):
            break
        else:
            sleep(sleep_delay)
    try:
        host_yaml = YAML().load(open(FILE_TOPO, 'r'))
        TOPO_TAG = host_yaml['topology']
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
        NODES = FILE_BUILD['nodes']
        for vdev in NODES:
            vdevn = list(vdev.keys())[0]
            CEOS[vdevn] = CEOS_NODE(vdevn, vdev[vdevn]['ip_addr'], vdev[vdevn]['neighbors'])
        # Check for CEOS Scripts Directory
        if checkDir(CEOS_SCRIPTS):
            pS("OK", "Directory is present now.")
        else:
            pS("iBerg", "Error creating directory.")
        create_output.append("#!/bin/bash\n")
        create_output.append("ip netns add atd\n")
        startup_output.append("#!/bin/bash\n")
        startup_output.append("ip netns add atd\n")
        # Get the veths created
        create_output.append("# Creating veths\n")
        for _veth in VETH_PAIRS:
            _v1, _v2 = _veth.split("-")
            create_output.append("ip link add {0} type veth peer name {1}\n".format(_v1, _v2))
            startup_output.append("ip link add {0} type veth peer name {1}\n".format(_v1, _v2))
        create_output.append("#\n#\n# Creating anchor containers\n#\n")
        # Create initial anchor containers
        create_output.append("mdir {0}\n".format(CEOS_NODES))
        create_output.append("cp -r {0}{1}/files/ceos/* {2}/\n".format(REPO_TOPO, TOPO_TAG, CEOS_NODES))
        for _node in CEOS:
            create_output.append("# Getting {0} nodes plubming\n".format(_node))
            create_output.append("docker run -d --restart=always --name={0}-net --net=none busybox /bin/init\n".format(_node))
            create_output.append("{0}pid=$(docker inspect --format '{{{{.State.Pid}}}}' {0}-net)\n".format(_node))
            create_output.append("ln -sf /proc/${{{0}pid}}/ns/net /var/run/netns/{0}\n".format(_node))
            startup_output.append("docker rm {0}\n".format(_node))
            startup_output.append("{0}pid=$(docker inspect --format '{{{{.State.Pid}}}}' {0}-net)\n".format(_node))
            startup_output.append("ln -sf /proc/${{{0}pid}}/ns/net /var/run/netns/{0}\n".format(_node))
            create_output.append("# Connecting containers together\n")
            for _intf in CEOS[_node].intfs:
                _tmp_intf = CEOS[_node].intfs[_intf]
                if _node in  _tmp_intf['veth'].split('-')[0]:
                    create_output.append("ip link set {0} netns {1} name {2} up\n".format(_tmp_intf['veth'].split('-')[0], _node, _tmp_intf['port']))
                    startup_output.append("ip link set {0} netns {1} name {2} up\n".format(_tmp_intf['veth'].split('-')[0], _node, _tmp_intf['port']))
                else:
                    create_output.append("ip link set {0} netns {1} name {2} up\n".format(_tmp_intf['veth'].split('-')[1], _node, _tmp_intf['port']))
                    startup_output.append("ip link set {0} netns {1} name {2} up\n".format(_tmp_intf['veth'].split('-')[1], _node, _tmp_intf['port']))
            # Get MGMT VETHS
            create_output.append("ip link add {0}-eth0 type veth peer name {0}-mgmt\n".format(_node))
            create_output.append("brctl addif {0} {1}-mgmt\n".format(MGMT_BRIDGE, _node))
            create_output.append("ip link set {0}-eth0 netns {0} name eth0 up\n".format(_node))
            create_output.append("ip link set {0}-mgmt up\n".format(_node))
            create_output.append("sleep 1\n")
            create_output.append("docker run -d --name={0} --net=container:{0}-net --ip {1} --privileged -v {2}/{0}:/mnt/flash:Z -e INTFTYPE=et -e MGMT_INTF=eth0 -e ETBA=1 -e SKIP_ZEROTOUCH_BARRIER_IN_SYSDBINIT=1 -e CEOS=1 -e EOS_PLATFORM=ceoslab -e container=docker -i -t ceosimage:{3} /sbin/init systemd.setenv=INTFTYPE=et systemd.setenv=MGMT_INTF=eth0 systemd.setenv=ETBA=1 systemd.setenv=SKIP_ZEROTOUCH_BARRIER_IN_SYSDBINIT=1 systemd.setenv=CEOS=1 systemd.setenv=EOS_PLATFORM=ceoslab systemd.setenv=container=docker\n".format(_node, CEOS[_node].ip, CEOS_NODES, CEOS_VERSION))
            startup_output.append("ip link add {0}-eth0 type veth peer name {0}-mgmt\n".format(_node))
            startup_output.append("brctl addif {0} {1}-mgmt\n".format(MGMT_BRIDGE, _node))
            startup_output.append("ip link set {0}-eth0 netns {0} name eth0 up\n".format(_node))
            startup_output.append("ip link set {0}-mgmt up\n".format(_node))
            startup_output.append("sleep 1\n")
            startup_output.append("docker run -d --name={0} --net=container:{0}-net --ip {1} --privileged -v {2}/{0}:/mnt/flash:Z -e INTFTYPE=et -e MGMT_INTF=eth0 -e ETBA=1 -e SKIP_ZEROTOUCH_BARRIER_IN_SYSDBINIT=1 -e CEOS=1 -e EOS_PLATFORM=ceoslab -e container=docker -i -t ceosimage:{3} /sbin/init systemd.setenv=INTFTYPE=et systemd.setenv=MGMT_INTF=eth0 systemd.setenv=ETBA=1 systemd.setenv=SKIP_ZEROTOUCH_BARRIER_IN_SYSDBINIT=1 systemd.setenv=CEOS=1 systemd.setenv=EOS_PLATFORM=ceoslab systemd.setenv=container=docker\n".format(_node, CEOS[_node].ip, CEOS_NODES, CEOS_VERSION))
        create_output.append('touch {0}.ceos.txt'.format(CEOS_SCRIPTS))
        startup_output.append('rm -- "$0"\n')

        # Create the initial deployment files
        with open(CEOS_SCRIPTS + 'Create.sh', 'w') as cout:
            for _create in create_output:
                cout.write(_create)
        with open(CEOS_SCRIPTS + 'Startup.sh', 'w') as cout:
            for _start in startup_output:
                cout.write(_start)
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
