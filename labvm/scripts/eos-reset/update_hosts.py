#!/usr/bin/env python

# Example ovs output

from pprint import pprint as pp
from subprocess import Popen, call, PIPE

host_info = {}

scmd = ["sudo","ovs-vsctl","show"]

host_file = 'hosts'

hosts_base = [
    "[all:vars]",
    "ansible_connection=ssh",
    "ansible_user=root",
    "ansible_ssh_pass=test",
    "ansible_port=22220\n",
    "[all]\n"
]

ovs_res = Popen(scmd,stdout=PIPE)
ovs_list = ovs_res.communicate()[0].split('\n')


for entry in ovs_list:
    if 'Interface' in entry and 'vx' in entry and not 'host' in entry and not 'cvp' in entry:
        cur_intf = entry.split('"')[1]
        cur_ind = ovs_list.index(entry)
        host_info[entry.split('"')[1][3:]] = ovs_list[cur_ind + 2].split('"')[1]


with open(host_file,'w') as hw:
    hw.writelines("\n".join(hosts_base))
    for ehost in host_info.keys():
        hw.write("{0} ansible_host={1}\n".format(ehost,host_info[ehost]))

