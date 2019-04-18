#!/usr/bin/python

from cvprac.cvp_client import CvpClient
import os
import time
import shutil
import yaml
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
   f = open('/etc/ACCESS_INFO.yaml')
   accessinfo = yaml.safe_load(f)
   f.close()
   topology = accessinfo['topology']

except:
   topology = 'none'
   
# Temp path for where repo will be cloned to (include trailing /)
gitTempPath = '/tmp/atd/'

# Relative path within the repo to the configlet directory
configletPath = 'topologies/' + topology + '/configlets/'
ignoreConfiglets = ['readme.md']
# cvpNodes can be a single item or a list of the cluster
cvpNodes = ['192.168.0.5']
cvpUsername = 'arista'
cvpPassword = 'arista'

# Initialize the client
clnt = CvpClient()

# Attempt to connect to CVP, if it's not available wait 60 seconds
attempts = 0
while 1:
   try: 
      clnt.connect(cvpNodes, cvpUsername, cvpPassword)
      if clnt.api.get_cvp_info()['version']:
         break
   except:
      attempts += 1
      print "Cannot connect to CVP waiting 1 minute attempt",attempts
      time.sleep(60)


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
        print "Configlet", configletName, "exists and is up to date!"
      else:
        cvpClient.api.update_configlet(configletConfig,configletKey,configletName)
        print "Configlet", configletName, "exists and is now up to date"
     
   except:
      addConfiglet = cvpClient.api.add_configlet(configletName,configletConfig)
      print "Configlet", configletName, "has been added"

##### End of syncConfiglet

# Check if the repo has been downloaded
while True:
   if os.path.isdir(gitTempPath):
      print("Local copy exists....continuing")
      break
   else:
      print "Local copy is missing....Waiting 1 minute for it to become available"
      time.sleep(60)

configlets = os.listdir(gitTempPath + configletPath)

for configletName in configlets:
   if configletName not in ignoreConfiglets:
      with open(gitTempPath + configletPath + configletName, 'r') as configletData:
         configletConfig=configletData.read()
      syncConfiglet(clnt,configletName,configletConfig)

print("Configlet sync complete")
