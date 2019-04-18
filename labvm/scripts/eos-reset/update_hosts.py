#!/usr/bin/env python

from ruamel.yaml import YAML

host_info = {}
ACCESS = '/etc/ACCESS_INFO.yaml'
#ACCESS = 'ACCESS_INFO.yaml'

host_file = 'hosts'

hosts_base = [
    "[all:vars]",
    "ansible_connection=ssh",
    "ansible_user=root",
    "ansible_ssh_pass=test",
    "ansible_port=22220\n",
    "[all]\n"
]

with open(ACCESS,'r') as a_yaml:
    veos_yaml = YAML().load(a_yaml)['nodes']['veos']

for node in veos_yaml:
    if 'host' not in node['hostname']:
        host_info[node['hostname']] = {'vxlan':node['ip'],'internal_ip':node['internal_ip']}

with open(host_file,'w') as hw:
    hw.writelines("\n".join(hosts_base))
    for ehost in host_info.keys():
        hw.write("{0} ansible_host={1}\n".format(ehost,host_info[ehost]['vxlan']))

