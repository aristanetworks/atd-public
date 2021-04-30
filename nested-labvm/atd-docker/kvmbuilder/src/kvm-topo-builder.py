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
BASE_XML_CVP = expanduser('~/base_cvp.xml')
BASE_XML_DMF = expanduser('~/base_dmf.xml')

OVS_BRIDGES = []
VEOS_NODES = {}
sleep_delay = 30
KOUT_LINES = ['#!/bin/bash','']


class vNODE():
    def __init__(self, node_name, node_ip, node_mac, node_neighbors):
        self.name = node_name
        self.name_short = parseNames(node_name)['code']
        self.ip = node_ip
        self.sys_mac = node_mac
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
    devDC = False
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
    elif dev_type == 'dmf':
        return('9{0}'.format(dev_id))
    else:
        if dev_id < 10:
            return('b{0}'.format(dev_id))
        elif dev_id >= 10 and dev_id < 20:
            return('c{0}'.format(dev_id - 10))
        elif dev_id >=20 and dev_id < 30:
            return('d{0}'.format(dev_id - 20))

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
    global KOUT_LINES
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
    FILE_BUILD = YAML().load(open(REPO_TOPO + TOPO_TAG + '/topo_build.yml', 'r'))
    host_cpu_count = FILE_BUILD['host_cpu']
    cvp_cpu_count = FILE_BUILD['cvp_cpu']
    cvp_node_count = FILE_BUILD['cvp_nodes']
    veos_cpu_count = FILE_BUILD['veos_cpu']
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
        VEOS_NODES[vdevn] = vNODE(vdevn, vdev[vdevn]['ip_addr'], v_sys_mac, vdev[vdevn]['neighbors'])
    # Create xml file for CVP KVM Node
    for _cvp in range(cvp_node_count):
        # Open base cvp xml
        tree = ET.parse(BASE_XML_CVP)
        root = tree.getroot()
        # Add name item for KVM domain
        vname = ET.SubElement(root, 'name')
        vname.text = 'cvp{0}'.format(_cvp + 1)
        # Add CPU Configuration
        vcpu = ET.SubElement(root, 'vcpu', attrib={
            'placement': 'static',
            'cpuset': CVP_NODES_CPUS[_cvp]
        })
        vcpu.text = str(cvp_cpu_count)
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
    if VEOS:
        # Create xml files for vEOS KVM Nodes
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
            # Add CPU configuration
            vcpu = ET.SubElement(root, 'vcpu', attrib={
                'placement': 'static',
                'cpuset': VEOS_CPUS
            })
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
            KOUT_LINES.append("sudo cp /var/lib/libvirt/images/veos/base/veos.qcow2 /var/lib/libvirt/images/veos/{0}.qcow2".format(vdev))
            KOUT_LINES.append("sudo virsh define {0}.xml".format(vdev))
            KOUT_LINES.append("sudo virsh start {0}".format(vdev))
            KOUT_LINES.append("sudo virsh autostart {0}".format(vdev))
            pS("OK", "Created Virsh commands for {0}".format(vdev))
            # Increment the node counter
            node_counter += 1

    # Output as script OVS Bridge creation
    createOVS(TOPO_TAG)
    # Output as script OVS Bridge deletion
    deleteOVS(TOPO_TAG)
    # Create xml file for CVP KVM Node

    if "dmf" in FILE_BUILD:
        node_counter = 1
        dmfControllerIP = FILE_BUILD['dmf']['nodes']['dmf-controller']['ip_addr']
        for dmfNodeName in FILE_BUILD['dmf']['nodes']:
            dmfNode = FILE_BUILD['dmf']['nodes'][dmfNodeName]
            dmfType = dmfNode['type']
            dmfVcpu = FILE_BUILD['dmf']['type'][dmfType]['vcpu']
            dmfIP = dmfNode['ip_addr']
            dmfMemory = FILE_BUILD['dmf']['type'][dmfType]['memory'] * 1024 * 1024
            # Open base cvp xml
            tree = ET.parse(BASE_XML_DMF)
            root = tree.getroot()
            # Add name item for KVM domain
            vname = ET.SubElement(root, 'name')
            vname.text = dmfNodeName
            # Add CPU Configuration
            vcpu = ET.SubElement(root, 'vcpu', attrib={
                'placement': 'static',
                'cpuset': VEOS_CPUS
            })
            vcpu.text = str(dmfVcpu)
            memory = ET.SubElement(root, 'memory', attrib={
                'unit': 'KiB'
            })
            memory.text = str(dmfMemory)
            currentMemory = ET.SubElement(root, 'currentMemory', attrib={
                'unit': 'KiB',
            })
            currentMemory.text = str(dmfMemory)

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
            ET.SubElement(tmp_disk1, 'source', attrib={'file': '/var/lib/libvirt/images/dmf/{0}.qcow2'.format(dmfNodeName)})
            ET.SubElement(tmp_disk1, 'target', attrib={
                'dev': 'vda',
                'bus': 'virtio'
            })
            # Starting interface section
            tmp_int = ET.SubElement(xdev, 'interface', attrib={'type': 'bridge'})
            ET.SubElement(tmp_int, 'source', attrib={'bridge': 'vmgmt'})
            ET.SubElement(tmp_int, 'mac', attrib={'address': '00:1c:73:{0}:c6:01'.format(createMac('dmf', node_counter))})
            ET.SubElement(tmp_int, 'target', attrib={'dev': '{0}'.format(dmfNodeName)})
            ET.SubElement(tmp_int, 'model', attrib={'type': 'virtio'})
            ET.SubElement(tmp_int, 'address', attrib={
                'type': 'pci',
                'domain': '0x0000',
                'bus': '0x00',
                'slot': '0x03',
                'function': '0x0'
            })


            # Interface specific links
            # dmfIntCount starts at 1 for eth0 aka mgmt
            dmfIntCount = 1
            DMF_BRIDGES = []
            DMF_KOUT = []
            if 'interfaces' in FILE_BUILD['dmf']['nodes'][dmfNodeName]:
                d_slot_counter = 3
                d_intf_counter = 1
                for dmfInt in FILE_BUILD['dmf']['nodes'][dmfNodeName]['interfaces']:
                    dmfIntCount += 1
                    dmfConnectTo = FILE_BUILD['dmf']['nodes'][dmfNodeName]['interfaces'][dmfInt]['connectTo']
                    dmfIntMode = FILE_BUILD['dmf']['nodes'][dmfNodeName]['interfaces'][dmfInt]['mode']
                    dmfIntName = "dmf{0}x{1}".format(node_counter,dmfInt)
                    if dmfIntMode == 'fabric' or dmfIntMode == 'tool':
                        DMF_BRIDGES.append(dmfConnectTo)
                        DMF_KOUT.append("sudo OFPORT=`ovs-vsctl get Interface {0} ofport`".format(dmfIntName))
                        DMF_KOUT.append("sudo ovs-vsctl set bridge {0} fail_mode=secure".format(dmfConnectTo))
                        DMF_KOUT.append("sudo ovs-ofctl add-flow {0} table=0,priority=0,in_port=$OFPORT,actions=flood".format(dmfConnectTo))
                    elif dmfIntMode == 'tap':
                        DMF_KOUT.append("BRIDGE=`sudo ovs-vsctl port-to-br {0}`".format(dmfConnectTo))
                        DMF_KOUT.append("sudo ovs-vsctl -- set bridge $BRIDGE mirrors=@m -- --id=@{0} get Port {0} -- --id=@{1} get Port {1} -- --id=@m create Mirror name=m{0} select-dst-port=@{0} select-src-port=@{0} output-port=@{1}".format(dmfConnectTo,dmfIntName))

                    tmp_int = ET.SubElement(xdev, 'interface', attrib={'type': 'bridge'})
                    ET.SubElement(tmp_int, 'source', attrib={'bridge': dmfConnectTo})
                    ET.SubElement(tmp_int, 'target', attrib={'dev': '{0}'.format(dmfIntName)})
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



            # Export out xml for DMF node
            tree.write(DATA_OUTPUT + '{0}.xml'.format(dmfNodeName))

            KOUT_LINES.append("sudo cp -r /var/lib/libvirt/images/dmf/{0}.qcow2 /var/lib/libvirt/images/dmf/{1}.qcow2".format(dmfType,dmfNodeName))
            KOUT_LINES.append("sudo virsh define {0}.xml".format(dmfNodeName))

            if dmfType == 'switch':
              dmfSwID = dmfNode['dmf_sw']
              KOUT_LINES.append("sed 's/DMF_SWITCH_IP/{0}/g' /opt/atd/nested-labvm/atd-docker/kvmbuilder/dmf-swconfig.sh > {1}-conf.sh".format(dmfIP,dmfNodeName))
              KOUT_LINES.append("sed -i 's/DMF_CONTROLLER_IP/{0}/g' {1}-conf.sh".format(dmfControllerIP,dmfNodeName))
              KOUT_LINES.append("sed -i 's/MAC_ADDRESS_INDEX_REPLACE/{0}/g' {1}-conf.sh".format(dmfSwID,dmfNodeName))
              KOUT_LINES.append("sed -i 's/INTERFACE_COUNT_REPLACE/{0}/g' {1}-conf.sh".format(dmfIntCount,dmfNodeName))
              KOUT_LINES.append("mv {0}-conf.sh CONFIGURE.sh".format(dmfNodeName))
              KOUT_LINES.append("virt-copy-in -d {0} /opt/atd/nested-labvm/atd-docker/kvmbuilder/.profile /home/mininet/".format(dmfNodeName))
              KOUT_LINES.append("virt-copy-in -d {0} CONFIGURE.sh /home/mininet/".format(dmfNodeName))
              KOUT_LINES.append("mv CONFIGURE.sh {0}-conf.sh".format(dmfNodeName))

            KOUT_LINES.append("sudo virsh start {0}".format(dmfNodeName))
            KOUT_LINES.append("sudo virsh autostart {0}".format(dmfNodeName))
            pS("OK", "Created Virsh commands for {0}".format(dmfNodeName))
            node_counter += 1

    # Combine lists and remove dupes
    global OVS_BRIDGES
    OVS_BRIDGES = OVS_BRIDGES + DMF_BRIDGES
    OVS_BRIDGES = list(set(OVS_BRIDGES))
    pS("OK","Removing dupes from OVS_BRIDGES {0}".format(OVS_BRIDGES))

    # Output as script OVS Bridge creation
    createOVS(TOPO_TAG)
    # Output as script OVS Bridge deletion
    deleteOVS(TOPO_TAG)
    # Create xml file for CVP KVM Node

    KOUT_LINES = KOUT_LINES + DMF_KOUT

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