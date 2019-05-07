#!/usr/bin/python
# Copyright (c) 2015-2016 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
'''Cvptool provides ability to take snapshots of state of the Cvp instance. The state
information is stored in a tar file. It also provides the ability to restore
the state of the Cvp instance using the backup tar file. Cvp instance can also be
reset to its initial state using this tool.p
'''

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import sys
sys.path.append('/cvp/tools')

import getopt
import errorCodes
import cvpServices
import Queue
import json
import argparse
import cvp
import tarfile
import os
import re
import getpass
import tempfile
import shutil


def resetDevices( server,topology,excludeList):

   # Define list of configlets/labs

   s1 = [ "Spine1-MLAG-Lab","Spine1-BGP-Lab","Spine1-BGP-Lab","Spine1-L2EVPN-Lab","Spine1-L3EVPN-Lab","Spine1-BGP-Lab","media-spine1-IP-Intro-start","media-spine1-VLAN-STP-start","media-spine1-OSPF-start","media-spine1-BGP-start","media-spine1-Multicast-lab" ]
   s2 = [ "Spine2-MLAG-Lab","Spine2-BGP-Lab","Spine2-BGP-Lab","Spine2-L2EVPN-Lab","Spine2-L3EVPN-Lab","Spine2-BGP-Lab","media-spine2-IP-Intro-start","media-spine2-VLAN-STP-start","media-spine2-OSPF-start","media-spine2-BGP-start","media-spine2-Multicast-lab" ]
   l1 = [ "Leaf1-MLAG-Lab","Leaf1-BGP-Lab","Leaf1-VXLAN-Lab","Leaf1-L2EVPN-Lab","Leaf1-L3EVPN-Lab","Leaf1-BGP-Lab","media-leaf1-IP-Intro-start","media-leaf1-VLAN-STP-start","media-leaf1-OSPF-start","media-leaf1-BGP-start","media-leaf1-Multicast-lab" ]
   l2 = [ "Leaf2-MLAG-Lab","Leaf2-BGP-Lab","Leaf2-VXLAN-Lab","Leaf2-L2EVPN-Lab","Leaf2-L3EVPN-Lab","Leaf2-BGP-Lab","media-leaf2-IP-Intro-start","media-leaf2-VLAN-STP-start","media-leaf2-OSPF-start","media-leaf2-BGP-start","media-leaf2-Multicast-lab" ]
   l3 = [ "Leaf3-MLAG-Lab","Leaf3-BGP-Lab","Leaf3-VXLAN-Lab","Leaf3-L2EVPN-Lab","Leaf3-L3EVPN-Lab","Leaf3-BGP-Lab","media-leaf3-IP-Intro-start","media-leaf3-VLAN-STP-start","media-leaf3-OSPF-start","media-leaf3-BGP-start","media-leaf3-Multicast-lab" ]
   l4 = [ "Leaf4-MLAG-Lab","Leaf4-BGP-Lab","Leaf4-VXLAN-Lab","Leaf4-L2EVPN-Lab","Leaf4-L3EVPN-Lab","Leaf4-BGP-Lab-Full","media-leaf4-IP-Intro-start","media-leaf4-VLAN-STP-start","media-leaf4-OSPF-start","media-leaf4-BGP-start","media-leaf4-Multicast-lab" ]

   # Map the topology provided upon call to the above list
   if topology == 'mlag':
     lab = 0
   elif topology == 'bgp':
     lab = 1
   elif topology == 'vxlan':
     lab = 2
   elif topology == 'l2evpn':
     lab = 3
   elif topology == 'l3evpn':
     lab = 4
   elif topology == 'cvp':
     lab = 5
   elif topology == 'media-intro':
     lab = 6
   elif topology == 'media-vlan':
     lab = 7
   elif topology == 'media-ospf':
     lab = 8
   elif topology == 'media-bgp':
     lab = 9
   elif topology == 'multicast':
     lab = 10

   # Loop through devices
   devices = server.getDevices()
   for device in devices:
     deviceName = device.fqdn
     deviceName = deviceName.split(".")
     deviceName = deviceName[0]

     if deviceName == 'leaf1':
       leaf1 = device
       if topology != 'base':
         labConfiglet = server.getConfiglet(l1[lab])
     elif deviceName == 'leaf2':
       leaf2 = device
       if topology != 'base':
         labConfiglet = server.getConfiglet(l2[lab])
     elif deviceName == 'leaf3':
       leaf3 = device
       if topology != 'base':
         labConfiglet = server.getConfiglet(l3[lab])
     elif deviceName == 'leaf4':
       leaf4 = device
       if topology != 'base':
         labConfiglet = server.getConfiglet(l4[lab])
     elif deviceName == 'spine1':
       spine1 = device
       if topology != 'base':
         labConfiglet = server.getConfiglet(s1[lab])
     elif deviceName == 'spine2':
       spine2 = device
       if topology != 'base':
         labConfiglet = server.getConfiglet(s2[lab])
     elif deviceName == 'cvx01':
       cvx01 = device
       continue

     # Define base configlets that are to be untouched
     baseConfiglets = [ "SYS_","AAA","VLANs" ]

     # Reset all devices to only have the above configlets (remove all others)
     for configlet in device.configlets:
       if configlet not in baseConfiglets:
         if not configlet.startswith(baseConfiglets[0]):
           print 'Configlet ',configlet,' not part of base on ',device.fqdn,' - Removing from device'
           configlet = server.getConfiglet(configlet)
           configletsToRemove = [ configlet ]
           server.removeConfigletAppliedToDevice(device,configletsToRemove)

     if deviceName in excludeList:
       print 'Excluding',deviceName
       continue

     # Apply necessary configlet to each device
     if topology != 'base':
       labConfigletList = [ labConfiglet ]
       server.mapConfigletToDevice(device,labConfigletList)

   # Execute the changes
   server.executeAllPendingTask()
   print "Completed setting devices to topology:",topology

def dump(obj):
  # This is for testing to print all of the object attributes
  for attr in dir(obj):
    print "obj.%s = %s" % (attr, getattr(obj, attr))

def main(argv):
   topology = 'base'
   exclude = ''

   # Process arguments
   try:
     opts, args = getopt.getopt(argv,"ht:e:",["topology=","exclude="])
   except getopt.GetOptError:
     print 'Usage:'
     print ''
     print 'ConfigureTopology.py - No options will reset the topology to the base'
     print '  -t Topology to push out to devices - currently mlag and bgp'
     print '  -e Exclude host(s) separated by commas if more than one'
     sys.exit(2)
   for opt, arg in opts:
     if opt == '-h':
       print 'Usage:'
       print ''
       print 'ConfigureTopology.py - No options will reset the topology to the base'
       print '  -t Topology to push out to devices - currently mlag and bgp'
       print '  -e Exclude host(s) separated by commas if more than one'
       sys.exit()
     elif opt in ("-t", "--topology"):
       topology = arg
     elif opt in ("-e", "--exclude"):
       exclude = arg

   if "," in exclude:
     exclude = exclude.split(",")

   tmpDir = tempfile.mkdtemp()
   server = cvp.Cvp( 'localhost', 'true', 443, tmpDir )
   server.authenticate( 'arista', 'arista' )
   resetDevices(server,topology,exclude)

if __name__ == '__main__':
   main(sys.argv[1:])