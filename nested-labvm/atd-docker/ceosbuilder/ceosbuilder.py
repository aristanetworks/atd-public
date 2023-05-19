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
NOTIFY_BASE = 1250
CEOS_VERSION = '4.24.1.1F'
REGIS_PATH = 'us.gcr.io/beta-atds'
MTU = 10000
VETH_PAIRS = []
CEOS = {}

NOTIFY_ADJUST = """
echo "fs.inotify.max_user_instances = {notify_instances}" > /etc/sysctl.d/99-zatd.conf
sysctl -w fs.inotify.max_user_instances={notify_instances}
"""

class CEOS_NODE():
    def __init__(self, node_name, node_ip, node_neighbors, mac_addr):
        self.name = node_name
        self.name_short = parseNames(node_name)['code']
        self.ip = node_ip
        self.system_mac = mac_addr
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
            _vethCheck = checkVETH('{0}{1}'.format(self.name_short, lport['code']), '{0}{1}'.format(rneigh['code'], rport['code']))
            if _vethCheck['status']:
                pS("OK", "VETH Pair {0} will be created.".format(_vethCheck['name']))
                VETH_PAIRS.append(_vethCheck['name'])
            self.intfs[intf['port']] = {
                'veth': _vethCheck['name'],
                'port': lport['code']
            }

def parseNames(devName):
    """
    Function to parse and consolidate name
    """
    alpha = ''
    numer = ''
    split_len = 2
    devDC = False
    devCORE = False
    tmp_devName = ""
    if ('s1-' or 's2-') in devName.lower():
        _tmp = devName.split('-')
        tmp_devName = _tmp[1]
        if 's1' or 's2' in _tmp[0].lower():
            devDC = _tmp[0]
        for char in tmp_devName:
            if char.isalpha():
                alpha += char
            elif char.isdigit():
                numer += char
    elif '-dc' in devName.lower() and 'dci' != devName.lower():
        _tmp = devName.split('-')
        tmp_devName = _tmp[0]
        if 'dc' in _tmp[1].lower():
            devDC = _tmp[1]
        for char in tmp_devName:
            if char.isalpha():
                alpha += char
            elif char.isdigit():
                numer += char
    elif '-core' in devName.lower():
        _tmp = devName.split('-')
        tmp_devName = _tmp[0]
        devCORE = _tmp[1]
        for char in tmp_devName:
            if char.isalpha():
                alpha += char
            elif char.isdigit():
                numer += char
    else:
        for char in devName:
            if char.isalpha():
                alpha += char
            elif char.isdigit():
                numer += char
    if 'ethernet'in devName.lower():
        dev_name = 'et'
    else:
        dev_name = alpha[:split_len]
    if devDC:
        dev_code = devDC.lower().replace('c','')
    elif devCORE:
        dev_code = devCORE.lower().replace('ore','')
    else:
        dev_code = ""
    devInfo = {
        'name': devName,
        'code': dev_name + numer + dev_code,
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
    elif dev_id >=30 and dev_id < 40:
        return('e{0}'.format(dev_id - 30))
    elif dev_id >=40 and dev_id < 50:
        return('f{0}'.format(dev_id - 40))

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
    upgrade_output = []
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
            _index = NODES.index(vdev)
            _node_mac = createMac(_index)
            CEOS[vdevn] = CEOS_NODE(vdevn, vdev[vdevn]['ip_addr'], vdev[vdevn]['neighbors'], _node_mac)
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
        create_output.append(NOTIFY_ADD)
        create_output.append("ip netns add atd\n")
        startup_output.append("#!/bin/bash\n")
        startup_output.append(NOTIFY_ADD)
        startup_output.append("ip netns add atd\n")
        upgrade_output.append("#!/bin/bash\n")
        upgrade_output.append("EOS_TYPE=$(cat /etc/atd/ACCESS_INFO.yaml | python3 -m shyaml get-value version)\n")
        # Get the veths created
        create_output.append("# Creating veths\n")
        for _veth in VETH_PAIRS:
            _v1, _v2 = _veth.split("-")
            create_output.append("ip link add {0} type veth peer name {1}\n".format(_v1, _v2))
            startup_output.append("ip link add {0} type veth peer name {1}\n".format(_v1, _v2))
        create_output.append("#\n#\n# Creating anchor containers\n#\n")
        # Create initial anchor containers
        create_output.append("mkdir {0}\n".format(CEOS_NODES))
        # create_output.append("cp -r {0}{1}/files/ceos/* {2}/\n".format(REPO_TOPO, TOPO_TAG, CEOS_NODES))
        for _node in CEOS:
            create_output.append(f"echo \"SERIALNUMBER={_node}\" > /opt/ceos/node/{_node}/ceos-config\n")
            create_output.append(f"echo \"SYSTEMMACADDR={CEOS[_node].system_mac}\" >> /opt/ceos/node/{_node}/ceos-config\n")
            create_output.append(f"echo \"DISABLE=False\" > /opt/ceos/nodes/{_node}/zerotouch-config\n")
            create_output.append("# Getting {0} nodes plubming\n".format(_node))
            create_output.append("docker run -d --restart=always --log-opt max-size=10k --name={0}-net --net=none busybox /bin/init\n".format(_node))
            create_output.append("{0}pid=$(docker inspect --format '{{{{.State.Pid}}}}' {1}-net)\n".format(_node.replace('-',''), _node))
            create_output.append("ln -sf /proc/${{{0}pid}}/ns/net /var/run/netns/{1}\n".format(_node.replace('-',''), _node))
            startup_output.append("docker stop {0}\n".format(_node))
            startup_output.append("docker rm {0}\n".format(_node))
            startup_output.append("{0}pid=$(docker inspect --format '{{{{.State.Pid}}}}' {1}-net)\n".format(_node.replace('-',''), _node))
            startup_output.append("ln -sf /proc/${{{0}pid}}/ns/net /var/run/netns/{1}\n".format(_node.replace('-',''), _node))
            create_output.append("# Connecting containers together\n")
            for _intf in CEOS[_node].intfs:
                _tmp_intf = CEOS[_node].intfs[_intf]
                if CEOS[_node].name_short in  _tmp_intf['veth'].split('-')[0]:
                    create_output.append("ip link set {0} mtu {3} netns {1} name {2} up\n".format(_tmp_intf['veth'].split('-')[0], _node, _tmp_intf['port'], MTU))
                    startup_output.append("ip link set {0} mtu {3} netns {1} name {2} up\n".format(_tmp_intf['veth'].split('-')[0], _node, _tmp_intf['port'], MTU))
                else:
                    create_output.append("ip link set {0} mtu {3} netns {1} name {2} up\n".format(_tmp_intf['veth'].split('-')[1], _node, _tmp_intf['port'], MTU))
                    startup_output.append("ip link set {0} mtu {3} netns {1} name {2} up\n".format(_tmp_intf['veth'].split('-')[1], _node, _tmp_intf['port'], MTU))
            # Get MGMT VETHS
            create_output.append("ip link add {0}-eth0 type veth peer name {0}-mgmt\n".format(CEOS[_node].name_short))
            create_output.append("brctl addif {0} {1}-mgmt\n".format(MGMT_BRIDGE, CEOS[_node].name_short))
            create_output.append("ip link set {0}-eth0 netns {1} name eth0 up\n".format(CEOS[_node].name_short, _node))
            create_output.append("ip link set {0}-mgmt up\n".format(CEOS[_node].name_short))
            create_output.append("sleep 1\n")
            create_output.append(f"docker run -d --name={_node} --log-opt max-size=1m --net=container:{_node}-net --privileged -v /etc/sysctl.d/99-zatd.conf:/etc/sysctl.d/99-zatd.conf:ro -v {CEOS_NODES}/{_node}:/mnt/flash:Z -e INTFTYPE=et -e MGMT_INTF=eth0 -e ETBA=1 -e CEOS=1 -e EOS_PLATFORM=ceoslab -e container=docker -i -t {REGIS_PATH}/ceosimage:{CEOS_VERSION} /sbin/init systemd.setenv=INTFTYPE=et systemd.setenv=MGMT_INTF=eth0 systemd.setenv=ETBA=1 systemd.setenv=CEOS=1 systemd.setenv=EOS_PLATFORM=ceoslab systemd.setenv=container=docker\n")
            startup_output.append("ip link add {0}-eth0 type veth peer name {0}-mgmt\n".format(CEOS[_node].name_short))
            startup_output.append("brctl addif {0} {1}-mgmt\n".format(MGMT_BRIDGE, CEOS[_node].name_short))
            startup_output.append("ip link set {0}-eth0 netns {1} name eth0 up\n".format(CEOS[_node].name_short, _node))
            startup_output.append("ip link set {0}-mgmt up\n".format(CEOS[_node].name_short))
            startup_output.append("sleep 1\n")
            startup_output.append(f"docker run -d --name={_node} --log-opt max-size=1m --net=container:{_node}-net --privileged -v /etc/sysctl.d/99-zatd.conf:/etc/sysctl.d/99-zatd.conf:ro -v {CEOS_NODES}/{_node}:/mnt/flash:Z -e INTFTYPE=et -e MGMT_INTF=eth0 -e ETBA=1 -e CEOS=1 -e EOS_PLATFORM=ceoslab -e container=docker -i -t {REGIS_PATH}/ceosimage:{CEOS_VERSION} /sbin/init systemd.setenv=INTFTYPE=et systemd.setenv=MGMT_INTF=eth0 systemd.setenv=ETBA=1 systemd.setenv=CEOS=1 systemd.setenv=EOS_PLATFORM=ceoslab systemd.setenv=container=docker\n")
            upgrade_output.append(f"docker stop {_node}\n")
            upgrade_output.append(f"docker rm {_node}\n")
            upgrade_output.append(f"docker run -d --name={_node} --log-opt max-size=1m --net=container:{_node}-net --privileged -v /etc/sysctl.d/99-zatd.conf:/etc/sysctl.d/99-zatd.conf:ro -v {CEOS_NODES}/{_node}:/mnt/flash:Z -e INTFTYPE=et -e MGMT_INTF=eth0 -e ETBA=1 -e CEOS=1 -e EOS_PLATFORM=ceoslab -e container=docker -i -t {REGIS_PATH}/ceosimage:$EOS_TYPE /sbin/init systemd.setenv=INTFTYPE=et systemd.setenv=MGMT_INTF=eth0 systemd.setenv=ETBA=1 systemd.setenv=CEOS=1 systemd.setenv=EOS_PLATFORM=ceoslab systemd.setenv=container=docker\n")
        create_output.append('touch {0}.ceos.txt'.format(CEOS_SCRIPTS))
        startup_output.append('rm -- "$0"\n')

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
