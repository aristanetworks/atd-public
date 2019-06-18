#!/usr/bin/env python

from ruamel.yaml import YAML
from rcvpapi.rcvpapi import *
from sys import exit
import argparse

ACCESS = '/etc/ACCESS_INFO.yaml'
CVPINFO = '/home/arista/cvp/cvp_info.yaml'
dev_list = []

# Try loading ACCESS_INFO
try:
    veos_devs = YAML().load(ACCESS)['nodes']['veos']
except:
    veos_devs = [{'hostname':'eos1'},{'hostname':'eos2'}]

for veos in veos_devs:
    dev_list.append(veos['hostname'])
"""
# Try loading cvp_info.yaml
try:
    with open(CVPINFO,'r') as ci:
        cvp_info = YAML().load(ci)
except:
    print("{0} is not found".format(CVPINFO))
    exit(1)
"""

def main(vdevs):
    print("Device{0} to be reset: {1}".format("s" if len(vdevs) > 1 else "",", ".join(vdevs)))


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