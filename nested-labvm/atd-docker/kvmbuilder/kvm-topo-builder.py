#!/usr/bin/env python3

from ruamel.yaml import YAML
from os.path import isdir, exists, expanduser
from os import mkdir
from time import sleep
import argparse
import xml.etree.ElementTree as ET

FILE_TOPO = '/etc/atd/ACCESS_INFO.yaml'
REPO_PATH = '/tmp/atd/'
REPO_TOPO = REPO_PATH + 'topologies/'
AVAIL_TOPO = REPO_TOPO + 'available_topo.yaml'
DATA_OUTPUT = expanduser('~/kvm/')
BASE_XML_VEOS = expanduser('~/base.xml')

OVS_BRIDGES = []
VEOS_NODES = {}
sleep_delay = 30
KOUT_LINES = ['#!/bin/bash','']


class vNODE():
    def __init__(self, node_name, node_ip, node_neighbors):
        self.name = node_name
        self.name_short = parseNames(node_name)['code']
        self.ip = node_ip
        self.intfs = {}
        self.portMappings(node_neighbors)

    def portMappings(self,node_neighbors):
        """
        Function to create port mappings
        """
        for intf in node_neighbors:
            lport = parseNames(intf['port'])
            rport = parseNames(intf['neighborPort'])
            rneigh = parseNames(intf['neighborDevice'])
            _bridgeCheck = checkBridge(self.name_short + lport['code'], rneigh['code'] + rport['code'])
            if _bridgeCheck['status']:
                _brName = self.name_short + lport['code'] + '-' + rneigh['code'] + rport['code']
                pS("OK","Bridge {0} will be created".format(_brName))
                OVS_BRIDGES.append(_brName)
            else:
                _brName = _bridgeCheck['name']
            self.intfs[intf['port']] = {
                'bridge': _brName,
                'port': lport['code']
            }


def checkBridge(dev1, dev2):
    global OVS_BRIDGES
    _addBr = True
    name_len = len(dev1 + dev2 + '-')
    for _br in OVS_BRIDGES:
        if dev1 in _br and dev2 in _br and len(_br) == name_len:
            _addBr = False
            return({'status': _addBr, 'name': _br})
    return({'status': _addBr, 'name':''})

def parseNames(devName):
    """
    Function to parse and consolidate name
    """
    alpha = ''
    numer = ''
    split_len = 2
    
    for char in devName:
        if char.isalpha():
            alpha += char
        elif char.isdigit():
            numer += char
    if 'ethernet' in devName.lower():
        dev_name = 'X'
    else:
        dev_name = alpha[:split_len]
    devInfo = {
        'name': devName,
        'code': dev_name + numer,
    }
    return(devInfo)

def createOVS(topo_tag):
    """
    Function to output and write to bash script
    to create all OVS-bridges.
    """
    _tag = topo_tag[0]
    destinationValidate(topo_tag)
    with open(DATA_OUTPUT + topo_tag + '-ovs-create.sh', 'w') as dout:
        dout.write("#!/bin/bash\n\n")
        for br in OVS_BRIDGES:
            dout.write("sudo ovs-vsctl add-br {0}\n".format(br))
            dout.write("sudo ovs-vsctl set bridge {0} other-config:forward-bpdu=true\n".format(br))

def destinationValidate(topo_tag):
    """
    Function to check and create destination directory.
    """
    if not exists(DATA_OUTPUT):
        mkdir(DATA_OUTPUT)

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

def main(uargs):
    global DATA_OUTPUT
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
    FILE_BUILD = YAML().load(open(REPO_TOPO + TOPO_TAG + '/topo_build.yml', 'r'))
    NODES = FILE_BUILD['nodes']
    DATA_OUTPUT += TOPO_TAG + "/"
    # Start to build out Node create and Network creation
    for vdev in NODES:
        vdevn = list(vdev.keys())[0]
        VEOS_NODES[vdevn] = vNODE(vdevn, vdev[vdevn]['ip_addr'], vdev[vdevn]['neighbors'])
    # Output as script OVS Bridge creation
    createOVS(TOPO_TAG)
    # Create xml files for KVM
    node_counter = 0
    for vdev in VEOS_NODES:
        # Open base XML file
        tree = ET.parse(BASE_XML_VEOS)
        root = tree.getroot()
        # Get to the device section and add interfaces
        xdev = root.find('./devices')
        # Add name item for KVM domain
        vname = ET.SubElement(root, 'name')
        vname.text = vdev
        # Add/Create disk location for xml
        tmp_disk = ET.SubElement(xdev, 'disk', attrib={
            'type': 'file',
            'device': 'disk'
        })
        ET.SubElement(tmp_disk, 'driver', attrib={
            'name': 'qemu',
            'type': 'qcow2',
            'cache': 'directsync',
            'io': 'native'
        })
        ET.SubElement(tmp_disk, 'source', attrib={'file': '/var/lib/libvirt/images/veos/{0}.qcow2'.format(vdev)})
        ET.SubElement(tmp_disk, 'target', attrib={
            'dev': 'hda',
            'bus': 'ide'
        })
        ET.SubElement(tmp_disk, 'alias', attrib={'name': 'ide0-0-0'})
        # Starting interface section
        tmp_int = ET.SubElement(xdev, 'interface', attrib={'type': 'bridge'})
        ET.SubElement(tmp_int, 'source', attrib={'bridge': 'vmgmt'})
        ET.SubElement(tmp_int, 'mac', attrib={'address': '00:1c:73:{0}:c6:01'.format(createMac(node_counter))})
        ET.SubElement(tmp_int, 'target', attrib={'dev': vdev})
        ET.SubElement(tmp_int, 'model', attrib={'type': 'virtio'})
        ET.SubElement(tmp_int, 'address', attrib={
            'type': 'pci',
            'domain': '0x0000',
            'bus': '0x00',
            'slot': '0x03',
            'function': '0x0'
        })
        # Interface specific links
        d_intf_counter = 1
        for vintf in VEOS_NODES[vdev].intfs:
            tmp_dev = VEOS_NODES[vdev].intfs[vintf]
            tmp_int = ET.SubElement(xdev, 'interface', attrib={'type': 'bridge'})
            ET.SubElement(tmp_int, 'source', attrib={'bridge': tmp_dev['bridge']})
            ET.SubElement(tmp_int, 'target', attrib={'dev': '{0}x{1}'.format(vdev, tmp_dev['port'].replace('X',''))})
            ET.SubElement(tmp_int, 'model', attrib={'type': 'virtio'})
            ET.SubElement(tmp_int, 'virtualport', attrib={'type': 'openvswitch'})
            ET.SubElement(tmp_int, 'address', attrib={
                'type': 'pci',
                'domain': '0x0000',
                'bus': '0x00',
                'slot': '0x03',
                'function': '0x{0}'.format(d_intf_counter)
            })
            # Increment the counter
            d_intf_counter += 1
        # TODO add in export/write of xml for node
        tree.write(DATA_OUTPUT + '{0}.xml'.format(vdev))
        KOUT_LINES.append("sudo cp /var/lib/libvirt/images/veos/base/veos.qcow2 /var/lib/libvirt/images/veos/{0}.qcow2".format(vdev))
        KOUT_LINES.append("sudo virsh define {0}.xml".format(vdev))
        KOUT_LINES.append("sudo virsh start {0}".format(vdev))
        KOUT_LINES.append("sudo virsh autostart {0}".format(vdev))
        pS("OK", "Created Virsh commands for {0}".format(vdev))
        # Increment the node counter
        node_counter += 1
    with open(DATA_OUTPUT + TOPO_TAG + '-kvm-create.sh', 'w') as kout:
        for kli in KOUT_LINES:
            kout.write("{0}\n".format(kli))
    
    
if __name__ == '__main__':
    print('Starting KMV Builder')
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--tag", type=str, help="Tag name for topology", default=None, required=False)
    parser.add_argument("-f", "--file", type=str, help="Custom Topology build file", default=None, required=False)
    args = parser.parse_args()
    #TODO add in logic to load custom build file. Default to tag's build file
    main(args)
    print('Complete!')
