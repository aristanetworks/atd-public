#!/usr/bin/env python3

from ruamel.yaml import YAML
from os.path import isdir, exists, expanduser
from os import mkdir
from time import sleep
import argparse
import xml.etree.ElementTree as ET
import psutil

FILE_TOPO = '/etc/atd/ACCESS_INFO.yaml'
REPO_PATH = '/opt/atd/'
REPO_TOPO = REPO_PATH + 'topologies/'
AVAIL_TOPO = REPO_TOPO + 'available_topo.yaml'
DATA_OUTPUT = expanduser('~/kvm/')
BASE_XML_VEOS = expanduser('~/base.xml')
BASE_XML_CLOUDEOS64 = expanduser('~/base64.xml')
BASE_XML_CVP = expanduser('~/base_cvp.xml')

OVS_BRIDGES = []
VEOS_NODES = {}
sleep_delay = 30
KOUT_LINES = ['#!/bin/bash','']


class vNODE():
    def __init__(self, node_name, node_ip, node_mac, node_neighbors, node_type):
        self.name = node_name
        self.name_short = parseNames(node_name)['code']
        self.ip = node_ip
        self.sys_mac = node_mac
        self.intfs = {}
        self.portMappings(node_neighbors)
        self.type = node_type

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
    devDC = False
    devSITE = False
    devCLOUD = False
    devCORE = False
    tmp_devName = ""
    if '-dc' in devName.lower() and 'dci' != devName.lower():
        _tmp = devName.split('-')
        tmp_devName = _tmp[0]
        if 'dc' in _tmp[1].lower():
            devDC = _tmp[1]
        for char in tmp_devName:
            if char.isalpha():
                alpha += char
            elif char.isdigit():
                numer += char
    elif '-site' in devName.lower():
        _tmp = devName.split('-')
        tmp_devName = _tmp[0]
        devSITE = _tmp[1]
        for char in tmp_devName:
            if char.isalpha():
                alpha += char
            elif char.isdigit():
                numer += char
    elif '-cloud' in devName.lower():
        _tmp = devName.split('-')
        tmp_devName = _tmp[0]
        devCLOUD = _tmp[1]
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
        dev_name = ''
    else:
        dev_name = alpha[:split_len]
    if devDC:
        dev_code = devDC.lower().replace('c','')
    elif devSITE:
        dev_code = devSITE.lower().replace('ite','')
    elif devCLOUD:
        dev_code = devCLOUD.lower().replace('oud','')
    elif devCORE:
        dev_code = devCORE.lower().replace('ore','')
    else:
        dev_code = ""
    devInfo = {
        'name': devName,
        'code': dev_name + numer + dev_code,
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

def deleteOVS(topo_tag):
    """
    Function to output and write to bash script
    to delete all OVS-bridges.
    """
    _tag = topo_tag[0]
    destinationValidate(topo_tag)
    with open(DATA_OUTPUT + topo_tag + '-ovs-delete.sh', 'w') as dout:
        dout.write("#!/bin/bash\n\n")
        for br in OVS_BRIDGES:
            dout.write("sudo ovs-vsctl del-br {0}\n".format(br))

def destinationValidate(topo_tag):
    """
    Function to check and create destination directory.
    """
    if not exists(DATA_OUTPUT):
        mkdir(DATA_OUTPUT)

def createMac(dev_type, dev_id):
    """
    Function to build dev specific MAC Address.
    """
    if dev_type == 'cvp':
        return('a{0}'.format(dev_id))
    else:
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

def getCPUs(start_cpu,cpu_total=0):
    """
    Function to get available CPUs vEOS node
    """
    cpu_cores = int(psutil.cpu_count(logical=True)/2)
    avail_cpus = []
    if cpu_total:
        cpu_total = int(cpu_total / 2) + start_cpu
    else:
        cpu_total = cpu_cores
    for cpuindex in range(start_cpu, cpu_total):
        avail_cpus.append(str(cpuindex))
        avail_cpus.append(str(cpuindex + cpu_cores))
    return(', '.join(avail_cpus))

def pS(mstat,mtype):
    """
    Function to send output from service file to Syslog
    """
    mmes = "\t" + mtype
    print("[{0}] {1}".format(mstat,mmes.expandtabs(7 - len(mstat))))

def main(uargs):
    global DATA_OUTPUT
    CVP_NODES_CPUS = []
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
    # Perform check if topology is dual deployed and node type
    if 'atd_role' in host_yaml:
        if host_yaml['atd_role'] == 'cvp':
            DEPLOY_CVP = True
            DEPLOY_VEOS = False
        else:
            DEPLOY_CVP = False
            DEPLOY_VEOS = True
    else:
        DEPLOY_CVP = True
        DEPLOY_VEOS = True
    FILE_BUILD = YAML().load(open(REPO_TOPO + TOPO_TAG + '/topo_build.yml', 'r'))
    host_cpu_count = FILE_BUILD['host_cpu']
    cvp_cpu_count = FILE_BUILD['cvp_cpu']
    cvp_node_count = FILE_BUILD['cvp_nodes']
    veos_cpu_count = FILE_BUILD['veos_cpu']
    if 'cvp_ram' in FILE_BUILD:
        cvp_ram_count = FILE_BUILD['cvp_ram'] * 1024
    else:
        cvp_ram_count = 22 * 1024
    if cvp_node_count == 1:
        CVP_CPU_START = int(host_cpu_count / 2)
        CVP_CPUS = getCPUs(CVP_CPU_START, cvp_cpu_count)
        CVP_NODES_CPUS.append(CVP_CPUS)
        VEOS_CPU_START = int(CVP_CPU_START + (cvp_cpu_count / 2))
    else:
        _node_start = int(host_cpu_count / 2)
        for _cvp_node in range(cvp_node_count):
            CVP_NODES_CPUS.append(getCPUs(_node_start, cvp_cpu_count))
            _node_start = int(_node_start + (cvp_cpu_count / 2))
        VEOS_CPU_START = _node_start
    VEOS_CPUS = getCPUs(VEOS_CPU_START)
    NODES = FILE_BUILD['nodes']
    DATA_OUTPUT += TOPO_TAG + "/"
    # Start to build out Node create and Network creation
    for vdev in NODES:
        vdevn = list(vdev.keys())[0]
        if 'sys_mac' in vdev[vdevn]:
            v_sys_mac = vdev[vdevn]['sys_mac']
        else:
            v_sys_mac = False
        if 'type' in vdev[vdevn]:
            node_type = vdev[vdevn]['type']
        else:
            node_type = "veoslab"
        VEOS_NODES[vdevn] = vNODE(vdevn, vdev[vdevn]['ip_addr'], v_sys_mac, vdev[vdevn]['neighbors'], node_type)
    # Output as script OVS Bridge creation
    createOVS(TOPO_TAG)
    # Output as script OVS Bridge deletion
    deleteOVS(TOPO_TAG)
    # Check if app should deploy CVP
    if DEPLOY_CVP:
        # Create xml file for CVP KVM Node
        for _cvp in range(cvp_node_count):
            # Open base cvp xml
            tree = ET.parse(BASE_XML_CVP)
            root = tree.getroot()
            # Add name item for KVM domain
            vname = ET.SubElement(root, 'name')
            vname.text = 'cvp{0}'.format(_cvp + 1)
            # Add CPU Configuration
            vcpu = ET.SubElement(root, 'vcpu')
            # vcpu = ET.SubElement(root, 'vcpu', attrib={
            #     'placement': 'static',
            #     'cpuset': CVP_NODES_CPUS[_cvp]
            # })
            vcpu.text = str(cvp_cpu_count)
            # Add RAM Configuration for CVP
            vmem = ET.SubElement(root, 'memory', attrib={
                'unit': 'MiB'
            })
            vmem.text = str(cvp_ram_count)
            vcurmem = ET.SubElement(root, 'currentMemory', attrib={
                'unit': 'MiB'
            })
            vcurmem.text = str(cvp_ram_count)
            # Get to the device section and add interfaces
            xdev = root.find('./devices')
            # Add/Create disk location for xml
            tmp_disk1 = ET.SubElement(xdev, 'disk', attrib={
                'type': 'file',
                'device': 'disk'
            })
            ET.SubElement(tmp_disk1, 'driver', attrib={
                'name': 'qemu',
                'type': 'qcow2',
                'cache': 'directsync',
                'io': 'native'
            })
            ET.SubElement(tmp_disk1, 'source', attrib={'file': '/var/lib/libvirt/images/cvp{0}/disk1.qcow2'.format(_cvp + 1)})
            ET.SubElement(tmp_disk1, 'target', attrib={
                'dev': 'vda',
                'bus': 'virtio'
            })
            # Second disk for CVP
            tmp_disk2 = ET.SubElement(xdev, 'disk', attrib={
                'type': 'file',
                'device': 'disk'
            })
            ET.SubElement(tmp_disk2, 'driver', attrib={
                'name': 'qemu',
                'type': 'qcow2',
                'cache': 'directsync',
                'io': 'native'
            })
            ET.SubElement(tmp_disk2, 'source', attrib={'file': '/var/lib/libvirt/images/cvp{0}/disk2.qcow2'.format(_cvp + 1)})
            ET.SubElement(tmp_disk2, 'target', attrib={
                'dev': 'vdb',
                'bus': 'virtio'
            })
            # Starting interface section
            tmp_int = ET.SubElement(xdev, 'interface', attrib={'type': 'bridge'})
            ET.SubElement(tmp_int, 'source', attrib={'bridge': 'vmgmt'})
            ET.SubElement(tmp_int, 'mac', attrib={'address': '00:1c:73:{0}:c6:01'.format(createMac('cvp', _cvp))})
            ET.SubElement(tmp_int, 'target', attrib={'dev': 'cvp{0}'.format(_cvp + 1)})
            ET.SubElement(tmp_int, 'model', attrib={'type': 'virtio'})
            ET.SubElement(tmp_int, 'address', attrib={
                'type': 'pci',
                'domain': '0x0000',
                'bus': '0x00',
                'slot': '0x03',
                'function': '0x0'
            })
            # Export out xml for CVP node
            tree.write(DATA_OUTPUT + 'cvp{0}.xml'.format(_cvp + 1))
            if _cvp + 1 == cvp_node_count:
                KOUT_LINES.append("sudo mv /var/lib/libvirt/images/cvp /var/lib/libvirt/images/cvp{0}".format(_cvp + 1))
            else:
                KOUT_LINES.append("sudo mkdir /var/lib/libvirt/images/cvp{0}".format(_cvp + 1))
                KOUT_LINES.append("sudo cp -r /var/lib/libvirt/images/cvp/disk* /var/lib/libvirt/images/cvp{0}/".format(_cvp + 1))
            KOUT_LINES.append("sudo virsh define cvp{0}.xml".format(_cvp + 1))
            KOUT_LINES.append("sudo virsh start cvp{0}".format(_cvp + 1))
            KOUT_LINES.append("sudo virsh autostart cvp{0}".format(_cvp + 1))
            pS("OK", "Created Virsh commands for cvp{0}".format(_cvp + 1))

    if 'eos_type' in host_yaml:
        if host_yaml['eos_type'] == 'veos':
            VEOS = True
        else:
            VEOS = False
    else:
        VEOS = True
    if VEOS and DEPLOY_VEOS:
        # Create xml files for vEOS KVM Nodes
        node_counter = 0
        for vdev in VEOS_NODES:
            # Open base XML file
            if VEOS_NODES[vdev].type == "cloudeos":
                tree = ET.parse(BASE_XML_CLOUDEOS64)
            else:
                tree = ET.parse(BASE_XML_VEOS)
            root = tree.getroot()
            # Get to the device section and add interfaces
            xdev = root.find('./devices')
            # Add name item for KVM domain
            vname = ET.SubElement(root, 'name')
            vname.text = vdev
            # Add CPU configuration
            vcpu = ET.SubElement(root, 'vcpu')
            # vcpu = ET.SubElement(root, 'vcpu', attrib={
            #     'placement': 'static',
            #     'cpuset': VEOS_CPUS
            # })
            vcpu.text = str(veos_cpu_count)

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
            if VEOS_NODES[vdev].sys_mac:
                tmp_sys_mac = VEOS_NODES[vdev].sys_mac
            else:
                tmp_sys_mac = '00:1c:73:{0}:c6:01'.format(createMac('veos', node_counter))
            tmp_int = ET.SubElement(xdev, 'interface', attrib={'type': 'bridge'})
            ET.SubElement(tmp_int, 'source', attrib={'bridge': 'vmgmt'})
            ET.SubElement(tmp_int, 'mac', attrib={'address': tmp_sys_mac})
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
            d_slot_counter = 3
            d_intf_counter = 1
            for vintf in VEOS_NODES[vdev].intfs:
                tmp_dev = VEOS_NODES[vdev].intfs[vintf]
                tmp_int = ET.SubElement(xdev, 'interface', attrib={'type': 'bridge'})
                ET.SubElement(tmp_int, 'source', attrib={'bridge': tmp_dev['bridge']})
                ET.SubElement(tmp_int, 'target', attrib={'dev': '{0}x{1}'.format(VEOS_NODES[vdev].name_short, tmp_dev['port'].replace('X',''))})
                ET.SubElement(tmp_int, 'model', attrib={'type': 'virtio'})
                ET.SubElement(tmp_int, 'virtualport', attrib={'type': 'openvswitch'})
                ET.SubElement(tmp_int, 'address', attrib={
                    'type': 'pci',
                    'domain': '0x0000',
                    'bus': '0x00',
                    'slot': '0x0{0}'.format(d_slot_counter),
                    'function': '0x{0}'.format(d_intf_counter)
                })
                # Check the device increment coutner and increment the counter
                if d_intf_counter == 7:
                    d_slot_counter += 1
                    d_intf_counter = 0
                else:
                    d_intf_counter += 1
            # Export/write of xml for node
            tree.write(DATA_OUTPUT + '{0}.xml'.format(vdev))
            if VEOS_NODES[vdev].type == "veoslab":
                KOUT_LINES.append("sudo cp /var/lib/libvirt/images/veos/base/veos.qcow2 /var/lib/libvirt/images/veos/{0}.qcow2".format(vdev))
            elif VEOS_NODES[vdev].type == "cloudeos":
                KOUT_LINES.append("sudo cp /var/lib/libvirt/images/veos/base/cloudeos64.qcow2 /var/lib/libvirt/images/veos/{0}.qcow2".format(vdev))
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
    print('Starting KVM Builder')
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--tag", type=str, help="Tag name for topology", default=None, required=False)
    parser.add_argument("-f", "--file", type=str, help="Custom Topology build file", default=None, required=False)
    args = parser.parse_args()
    #TODO add in logic to load custom build file. Default to tag's build file
    main(args)
    print('Complete!')
