#!/usr/bin/python

import os
import time
import shutil
import yaml
from ruamel.yaml import YAML
from rcvpapi.rcvpapi import *
from cvprac.cvp_client import CvpClient
from paramiko import SSHClient
from paramiko import AutoAddPolicy
from scp import SCPClient
from os import path
from datetime import datetime
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ACCESS = '/etc/atd/ACCESS_INFO.yaml'
REPO_PATH = '/opt/atd/'
REPO_TOPO = REPO_PATH + 'topologies/'
CVP_CONFIG_FIILE = os.path.expanduser('~/CVP_DATA/.cvpState.txt')
sleep_delay = 30

# Function to sync configlet to CVP
def syncConfiglet(cvpClient,configletName,configletConfig):
   try:
      # See if configlet exists
      configlet = cvpClient.api.get_configlet_by_name(configletName)
      configletKey = configlet['key']
      configletCurrentConfig = configlet['config']
      # For future use to compare date in CVP vs. Git (use this to push to Git)
      configletCurrentDate = configlet['dateTimeInLongFormat']
      # If it does, check to see if the config is in sync, if not update the config with the one in Git
      if configletConfig == configletCurrentConfig:
        pS("OK", "Configlet {0} exists and is up to date!".format(configletName))
      else:
        cvpClient.api.update_configlet(configletConfig,configletKey,configletName)
        pS("OK", "Configlet {0} exists and is now up to date".format(configletName))
     
   except:
      addConfiglet = cvpClient.api.add_configlet(configletName,configletConfig)
      pS("OK", "Configlet {0}has been added".format(configletName))

##### End of syncConfiglet

def getTopoInfo(yaml_file):
    """
    Function that parses the supplied YAML file to build the CVP topology.
    """
    topoInfo = open(yaml_file,'r')
    topoYaml = YAML().load(topoInfo)
    topoInfo.close()
    return(topoYaml)

def checkConnected(cvp_clnt, NODES):
    """
    Function to check if all nodes have connected and
    are reachable via ping
    Parameters:
    cvp_clnt = CVP rCVPAPI client (object)
    NODES = EOS Node yaml (dict)
    """
    tmp_device_count = len(cvp_clnt.inventory)
    while len(NODES) > tmp_device_count:
        pS("INFO", "Only {0} out of {1} nodes have registered to CVP. Sleeping {2} seconds.".format(tmp_device_count, len(NODES), sleep_delay))
        sleep(sleep_delay)
        cvp_clnt.getDeviceInventory()
        tmp_device_count = len(cvp_clnt.inventory)
    pS("OK", "All {0} out of {1} nodes have registered to CVP.".format(tmp_device_count, len(NODES)))
    pS("INFO", "Checking to see if all nodes are reachable")
    # Make sure all nodes are up and reachable
    for vnode in cvp_clnt.inventory:
        while True:
            vresponse = cvp_clnt.ipConnectivityTest(cvp_clnt.inventory[vnode]['ipAddress'])
            if 'data' in vresponse:
                if vresponse['data'] == 'success':
                    pS("OK", "{0} is up and reachable at {1}".format(vnode, cvp_clnt.inventory[vnode]['ipAddress']))
                    break
            else:
                pS("INFO", "{0} is NOT reachable at {1}. Sleeping {2} seconds.".format(vnode, cvp_clnt.inventory[vnode]['ipAddress'], sleep_delay))
                sleep(sleep_delay)
    pS("OK", "All Devices are registered and reachable.")
    return(True)

def pS(mstat,mtype):
    """
    Function to send output from service file to Syslog
    """
    cur_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mmes = "\t" + mtype
    print("[{0}] [{1}] {2}".format(cur_dt, mstat, mmes.expandtabs(7 - len(mstat))))




def main():
   NODES = []
   while True:
      if os.path.exists(ACCESS):
         break
      else:
         pS("ERROR", "ACCESS_INFO file is not available...Waiting for {0} seconds".format(sleep_delay))
         time.sleep(sleep_delay)
   try:
      f = open(ACCESS)
      accessinfo = yaml.safe_load(f)
      f.close()
      topology = accessinfo['topology']
   except:
      topology = 'none'
      
   # Temp path for where repo will be cloned to (include trailing /)
   gitTempPath = '/opt/atd/'

   # Determining the EOS type and build file
   if accessinfo["eos_type"] == "ceos":
      topo_filename = "ceos_build.yml"
   else:
      topo_filename = "topo_build.yml"

   # Check if Configlets should get updated
   # ==========================================
   # Add Check for CVP Mode
   # ==========================================
   if 'cvp_mode' in accessinfo:
      if accessinfo['cvp_mode'] == 'bare':
         pS("INFO", "CVP is in bare configuration mode, no configlets to be imported.")
         return(True)

   # Relative path within the repo to the configlet directory
   configletPath = 'topologies/' + topology + '/configlets/'
   ignoreConfiglets = ['readme.md']

   # cvpNodes can be a single item or a list of the cluster
   cvpNodes = ['192.168.0.5']
   cvpUsername = accessinfo['login_info']['jump_host']['user']
   cvpPassword = accessinfo['login_info']['jump_host']['pw']
   # for urole in accessinfo['login_info']['cvp']['shell']:
   #    if urole['user'] == 'arista':
   #       cvpUsername = urole['user']
   #       cvpPassword = urole['pw']

   # rcvpapi clnt var container
   cvp_clnt = ""
   cvprc_clnt = ""

   # Adding new connection to CVP via rcvpapi
   while not cvp_clnt:
      try:
         cvp_clnt = CVPCON(accessinfo['nodes']['cvp'][0]['ip'],cvpUsername,cvpPassword)
         pS("OK", "Connected to CVP at {0}".format(accessinfo['nodes']['cvp'][0]['ip']))
      except:
         pS("iBerg", "CVP is currently unavailable....Retrying in 30 seconds.")
         time.sleep(30)

   # Check if the repo has been downloaded
   while True:
      if os.path.isdir(gitTempPath):
         pS("OK", "Local copy exists....continuing")
         break
      else:
         pS("INFO", "Local copy is missing....Waiting 1 minute for it to become available")
         time.sleep(60)
   while not cvprc_clnt:
      try:
         cvprac_clnt = CvpClient()
         cvprac_clnt.api.request_timeout = 180
         cvprac_clnt.connect([accessinfo['nodes']['cvp'][0]['ip']], cvpUsername, cvpPassword)
         cvprc_clnt = CVPCON(accessinfo['nodes']['cvp'][0]['ip'], cvpUsername, cvpPassword)
         pS("OK","Connected to CVP at {0}".format(accessinfo['nodes']['cvp'][0]['ip']))
      except:
         pS("ERROR","CVP is currently unavailable....Retrying in {0} seconds.".format(sleep_delay))
         sleep(sleep_delay)
   
   # ==========================================
   # Check the current version to see if a 
   # token needs to be generated
   # ==========================================
   _version = cvprac_clnt.api.get_cvp_info()
   _version = _version['version'].split('.')
   _version_major = float(f"{_version[0]}.{_version[1]}")
   build_yaml = getTopoInfo(f"{REPO_TOPO}{accessinfo['topology']}/{topo_filename}")

   # Perform check and iterate over all nodes that are CV Manage
   if accessinfo["eos_type"] == "ceos":
      for _node in build_yaml["nodes"]:
         if _node["cv_manage"]:
            NODES.append(_node)
   else:
      NODES = build_yaml['nodes']

   # Perform check if it is a cEOS based topo and 2022.2 or later CVP
   if _version_major >= 2022.2:
      pS("INFO", "Generating a token for onboarding...")
      _token_response = cvprac_clnt.api.create_enroll_token("24h")
      _token_path = path.expanduser(f"~/token")
      with open(f"{_token_path}", 'w') as token_out:
         token_out.write(_token_response['data'])
      # EOS_DEV = []
      for dev in NODES:
         if accessinfo["eos_type"] == "ceos":
            devn = dev["name"]
            _eos_ip = dev["ip_addr"]
         else:
            devn = list(dev.keys())[0]
            _eos_ip = dev[devn]['ip_addr']
         with SSHClient() as ssh:
            ssh.set_missing_host_key_policy(AutoAddPolicy())
            ssh.connect(_eos_ip, username=cvpUsername, password=cvpPassword,)
            with SCPClient(ssh.get_transport()) as scp:
               pS("INFO", f"Transferring token to {devn}")
               scp.put(f"{_token_path}", "/tmp/token")
   else:
      pS("INFO", f"Version does not require a token for onboarding...")

   # ==========================================
   # Check to see how many nodes have connected
   # ==========================================
   checkConnected(cvp_clnt, NODES)

   configlets = os.listdir(gitTempPath + configletPath)

   for configletName in configlets:
      if configletName not in ignoreConfiglets:
         with open(gitTempPath + configletPath + configletName, 'r') as configletData:
            configletConfig=configletData.read()
         new_configletName = configletName.replace(".py","")
         # Add check for ConfigletBuilder
         if '.py' in configletName:
            # Check for a form file
            if configletName.replace('.py', '.form') in configlets:
               pS("INFO", "Form data found for {0}".format(new_configletName))
               with open(gitTempPath + configletPath + configletName.replace('.py', '.form'), 'r') as configletData:
                  configletForm = configletData.read()
               configletFormData = yaml.safe_load(configletForm)['FormList']
            else:
               configletFormData = []
            res = cvp_clnt.impConfiglet("builder",new_configletName,configletConfig, configletFormData)
            pS("OK", "{0} Configlet Builder: {1}".format(res[0],new_configletName))
         elif '.form' in configletName:
            # Ignoring .form files here
            pass
         else:
            res = cvp_clnt.impConfiglet("static",configletName,configletConfig)
            pS("OK", "{0} Configlet: {1}".format(res[0],configletName))
   # Perform a check to see if there any pending tasks to be executed due to configlet update
   time.sleep(20)
   pS("INFO", "Checking for any pending tasks")
   cvp_clnt.getAllTasks("pending")
   if cvp_clnt.tasks['pending']:
      pS("INFO", "{0} Pending tasks found, will be executing".format(len(cvp_clnt.tasks['pending'])))
      task_response = cvp_clnt.execAllTasks("pending")
      time.sleep(10)
      while len(cvp_clnt.tasks['pending']) > 0:
         pS("INFO", "{0} Pending tasks found, will be executing".format(len(cvp_clnt.tasks['pending'])))
         _tmp_response = cvp_clnt.execAllTasks("pending")
         time.sleep(5)
         cvp_clnt.getAllTasks("pending")
      # Perform check to see if there are any existing tasks to be executed
      if task_response:
         pS("OK", "All pending tasks are executing")
         for task_id in task_response['ids']:
            task_status = cvp_clnt.getTaskStatus(task_id)['taskStatus']
            while task_status != "Completed":
               task_status = cvp_clnt.getTaskStatus(task_id)['taskStatus']
               if task_status == 'Failed':
                     pS("iBerg", "Task ID: {0} Status: {1}".format(task_id, task_status))
                     break
               elif task_status == 'Completed':
                     pS("INFO", "Task ID: {0} Status: {1}".format(task_id, task_status))
                     break
               else:
                     pS("INFO", "Task ID: {0} Status: {1}, Waiting 10 seconds...".format(task_id, task_status))
                     time.sleep(10)
      # Perform check to see if any tasks failed
      cvp_clnt.getAllTasks("failed")
      if len(cvp_clnt.tasks["failed"]) > 0:
         pS("INFO", "Failed tasks found, will execute tasks...")
         task_response = cvp_clnt.execAllTasks("failed")
         if task_response:
            pS("OK", "All pending tasks are executing")
            for task_id in task_response['ids']:
               task_status = cvp_clnt.getTaskStatus(task_id)['taskStatus']
               while task_status != "Completed":
                  task_status = cvp_clnt.getTaskStatus(task_id)['taskStatus']
                  if task_status == 'Failed':
                        pS("iBerg", "Task ID: {0} Status: {1}".format(task_id, task_status))
                        break
                  elif task_status == 'Completed':
                        pS("INFO", "Task ID: {0} Status: {1}".format(task_id, task_status))
                        break
                  else:
                        pS("INFO", "Task ID: {0} Status: {1}, Waiting 10 seconds...".format(task_id, task_status))
                        time.sleep(10)
   else:
      pS("INFO", "No pending tasks found to be executed.")


if __name__ == '__main__':
   # Check to see if cvpUpdater has already run
   if os.path.exists(CVP_CONFIG_FIILE):
      pS("INFO", "CVP Already configured....Updating configlets.")
      main()
      pS("OK", "Configlet sync complete")
   else:
      pS("INFO", "CVP not provisioned, holding off on configlet sync.")
   while True:
      time.sleep(600)