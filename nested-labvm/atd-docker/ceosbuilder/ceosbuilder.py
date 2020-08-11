#!/usr/bin/env python3

from ruamel.yaml import YAML
from time import sleep
from os.path import exists
import argparse


FILE_TOPO = '/etc/atd/ACCESS_INFO.yaml'
REPO_PATH = '/opt/atd/'
CEOS_PATH = '/opt/ceos/'
CEOS_NODES = CEOS_PATH + 'nodes/'
CEOS_SCRIPTS = CEOS_PATH + 'scripts/'
REPO_TOPO = REPO_PATH + 'topologies/'
AVAIL_TOPO = REPO_TOPO + 'available_topo.yaml'
sleep_delay = 30

VETH_PAIRS = []
CEOS = []


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
            print(str(_vethCheck))
            if _vethCheck['status']:
                pS("OK", "VETH Pair {0} will be created.".format(_vethCheck['name']))
                VETH_PAIRS.append(_vethCheck['name'])
            self.intfs[intf['port']] = {
                ''
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
    while True:
        if exists(FILE_TOPO):
            break
        else:
            sleep(sleep_delay)
    try:
        host_yaml = YAML().load(open(FILE_TOPO, 'r'))
        TOPO_TAG = host_yaml['topology']
    except:
        pS("iBerg", "File not found")
    # Grab topo build file
    FILE_BUILD = YAML().load(open(REPO_TOPO + TOPO_TAG + '/topo_build.yml', 'r'))
    NODES = FILE_BUILD['nodes']
    for vdev in NODES:
        vdevn = list(vdev.keys())[0]
        CEOS[vdevn] = CEOS_NODE(vdevn, vdev[vdevn]['ip_addr'], vdev[vdevn]['neighbors'])



if __name__ == '__main__':
    pS('OK', 'Starting cEOS Builder')
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--tag", type=str, help="Tag name for topology", default=None, required=False)
    parser.add_argument("-f", "--file", type=str, help="Custom Topology build file", default=None, required=False)
    args = parser.parse_args()
    #TODO add in logic to load custom build file. Default to tag's build file
    main(args)
    pS('OK', 'Complete!')
