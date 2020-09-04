#!/usr/bin/env python3

import time, shutil, syslog, os
from ruamel.yaml import YAML
from rcvpapi.rcvpapi import *
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

pDEBUG = False
topo_file = '/etc/ACCESS_INFO.yaml'
CVP_CONFIG_FILE = '/home/arista/.cvpState.txt'

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
         pS("OK", "Connected to CVP at {0}".format(accessinfo['nodes']['cvp'][0]['internal_ip']))
      except:
         pS("Error", "CVP is currently unavailable....Retrying in 30 seconds.")
         time.sleep(30)

   # Check if the repo has been downloaded
   while True:
      if os.path.isdir(gitTempPath):
         pS("INFO", "Local copy exists....continuing")
         break
      else:
         pS("ERROR", "Local copy is missing....Waiting 1 minute for it to become available")
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
            pS("INFO", "{0} Configlet Builder: {1}".format(res[0],new_configletName))
         else:
            res = cvp_clnt.impConfiglet("static",configletName,configletConfig)
            pS("INFO", "{0} Configlet: {1}".format(res[0],configletName))
   # Perform a check to see if there any pending tasks to be executed due to configlet update
   sleep(10)
   pS("INFO", "Performing check for pending tasks.")
   cvp_clnt.getAllTasks("pending")
   if cvp_clnt.tasks['pending']:
      pS("INFO", "Pending tasks found, will execute")
      task_response = cvp_clnt.execAllTasks("pending")
      # Perform check to see if there are any existing tasks to be executed
      if task_response:
         pS("INFO", "All pending tasks are executing")
         for task_id in task_response['ids']:
            task_status = cvp_clnt.getTaskStatus(task_id)['taskStatus']
            while task_status != "Completed":
               task_status = cvp_clnt.getTaskStatus(task_id)['taskStatus']
               if task_status == 'Failed':
                     pS("ERROR", "Task ID: {0} Status: {1}".format(task_id, task_status))
                     break
               elif task_status == 'Completed':
                     pS("OK", "Task ID: {0} Status: {1}".format(task_id, task_status))
                     break
               else:
                     pS("INFO", "Task ID: {0} Status: {1}, Waiting 10 seconds...".format(task_id, task_status))
                     sleep(10)
   else:
      pS("OK", "No pending tasks found")


   pS("OK", "Configlet sync complete")


if __name__ == '__main__':
   # Open Syslog
   syslog.openlog(logoption=syslog.LOG_PID)
   pS("OK","Starting...")

   atd_yaml = getTopoInfo(topo_file)
   if 'cvp' in atd_yaml['nodes']:
      # Check if cvpUpdater has run
      if os.path.exists(CVP_CONFIG_FILE):
         # Start the main Service
         pS("INFO", "Starting configlet sync...")
         main()
         pS("OK","Completed Configlet Sync")
      else:
         pS("OK","Initial ATD Topo Boot, exiting")
   else:
      pS("INFO","CVP is not present in this topology, disabling gitConfigletSync")
      os.system("systemctl disable gitConfigletSync")
      os.system("systemctl stop gitConfigletSync")