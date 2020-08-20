#!/usr/bin/env python3

import time, shutil, syslog, os
from ruamel.yaml import YAML
from rcvpapi.rcvpapi import *
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

pDEBUG = False
topo_file = '/etc/ACCESS_INFO.yaml'

def pS(mstat,mtype):
    """
    Function to send output from service file to Syslog
    Parameters:
    mstat = Message Status, ie "OK", "INFO" (required)
    mtype = Message to be sent/displayed (required)
    """
    mmes = "\t" + mtype
    syslog.syslog("[{0}] {1}".format(mstat,mmes.expandtabs(7 - len(mstat))))
    if pDEBUG:
        print("[{0}] {1}".format(mstat,mmes.expandtabs(7 - len(mstat))))

def getTopoInfo(yaml_file):
    """
    Function that parses the supplied YAML file to build the CVP topology.
    """
    topoInfo = open(yaml_file,'r')
    topoYaml = YAML().load(topoInfo)
    topoInfo.close()
    return(topoYaml)

def main():
   """
   Main Function if this is the initial deployment for the ATD/CVP
   """
   try:
      accessinfo = getTopoInfo(topo_file)
      topology = accessinfo['topology']

   except:
      topology = 'none'
      
   # Temp path for where repo will be cloned to (include trailing /)
   gitTempPath = '/tmp/atd/'

   # Relative path within the repo to the configlet directory
   configletPath = 'topologies/' + topology + '/configlets/'
   ignoreConfiglets = ['readme.md']

   for urole in accessinfo['login_info']['cvp']['shell']:
      if urole['user'] == 'arista':
         cvpUsername = urole['user']
         cvpPassword = urole['pw']

   # rcvpapi clnt var container
   cvp_clnt = ""

   # Adding new connection to CVP via rcvpapi
   while not cvp_clnt:
      try:
         cvp_clnt = CVPCON(accessinfo['nodes']['cvp'][0]['internal_ip'],cvpUsername,cvpPassword)
         print("[OK] Connected to CVP at {0}".format(accessinfo['nodes']['cvp'][0]['internal_ip']))
      except:
         print("[ERROR] CVP is currently unavailable....Retrying in 30 seconds.")
         time.sleep(30)

   # Check if the repo has been downloaded
   while True:
      if os.path.isdir(gitTempPath):
         print("Local copy exists....continuing")
         break
      else:
         print("Local copy is missing....Waiting 1 minute for it to become available")
         time.sleep(60)

   configlets = os.listdir(gitTempPath + configletPath)

   for configletName in configlets:
      if configletName not in ignoreConfiglets:
         with open(gitTempPath + configletPath + configletName, 'r') as configletData:
            configletConfig=configletData.read()
         # Add check for ConfigletBuilder
         if '.py' in configletName:
            new_configletName = configletName.replace(".py","")
            res = cvp_clnt.impConfiglet("builder",new_configletName,configletConfig)
            print("{0} Configlet Builder: {1}".format(res[0],new_configletName))
         else:
            res = cvp_clnt.impConfiglet("static",configletName,configletConfig)
            print("{0} Configlet: {1}".format(res[0],configletName))

   print("Configlet sync complete")


if __name__ == '__main__':
   # Open Syslog
   syslog.openlog(logoption=syslog.LOG_PID)
   pS("OK","Starting...")

   atd_yaml = getTopoInfo(topo_file)
   if 'cvp' in atd_yaml['nodes']:
      # Start the main Service
      pS("OK","Initial ATD Topo Boot")
      main()
      pS("OK","Completed Configlet Sync")
   else:
      pS("INFO","CVP is not present in this topology, disabling gitConfigletSync")
      os.system("systemctl disable gitConfigletSync")
      os.system("systemctl stop gitConfigletSync")
