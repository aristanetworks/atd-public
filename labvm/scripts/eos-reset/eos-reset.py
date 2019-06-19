#!/usr/bin/env python

from ruamel.yaml import YAML
from rcvpapi.rcvpapi import *
import paramiko
from sys import exit
import argparse

ACCESS = '/etc/ACCESS_INFO.yaml'
CVPINFO = '/home/arista/cvp/cvp_info.yaml'
BARE_CFGS = ['AAA']
# List object to list available devices
dev_list = []
# Dict object to keep track of veos devices
re_veos = {}

# Bare device specific config portion
dev_bare = """
hostname {0}
!
interface Management1
   ip address {1}/24
!
management api http-commands
   no shutdown
"""

# Loading ACCESS_INFO
with open(ACCESS,'r') as atdyaml:
    atd_yaml = YAML().load(atdyaml)
    veos_devs = atd_yaml['nodes']['veos']
    TOPO = atd_yaml['topology']

for veos in veos_devs:
    dev_list.append(veos['hostname'])
    re_veos[veos['hostname']] = {'hostname':veos['hostname'],'internal_ip':veos['internal_ip'],'ip':veos['ip'],'cvpobj':""}

# Loading cvp_info.yaml
with open(CVPINFO,'r') as ci:
    cvp_info = YAML().load(ci)

def pushBareConfig(veos_host,veos_ip,veos_config):
    veos_ssh = paramiko.SSHClient()
    veos_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    veos_ssh.connect(hostname=veos_ip,username="root",password="",port="22220")
    veos_ssh.exec_command('echo "{0}" | tee /mnt/flash/startup-config'.format(veos_config))
    #veos_ssh.exec_command('reboot')
    veos_ssh.close()

def main(vdevs):
    print("Device{0} to be reset: {1}".format("s" if len(vdevs) > 1 else "",", ".join(vdevs)))
    bare_veos = ""
    for b_cfg in BARE_CFGS:
        with open('/tmp/atd/topologies/{0}/configlets/{1}'.format(TOPO,b_cfg,'r')) as bcfg:
            bare_veos += bcfg.read() + "\n"
    # Create necessary info
    for cur_veos in vdevs:
        tmp_veos_config = bare_veos + dev_bare.format(re_veos[cur_veos]['hostname'],re_veos[cur_veos]['internal_ip'])
        pushBareConfig(cur_veos,re_veos[cur_veos]['ip'],tmp_veos_config)


if __name__ == '__main__':
    u_opts = argparse.ArgumentParser()
    u_opts.add_argument("-d",type=str,help="List of devies to reset:",choices=dev_list + ['all'],nargs='+',required=True)

    args = u_opts.parse_args()
    vdevs = args.d 
    if 'all' in vdevs:
        res_dev = dev_list
    else:
        res_dev = vdevs
    main(res_dev)