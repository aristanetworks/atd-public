#!/usr/bin/env python3
import urllib3, yaml
#from pprint import pprint
from cvprac.cvp_client import CvpClient
urllib3.disable_warnings()
clnt = CvpClient()
with open('group_vars/CVP/CVP_CRED.yml', 'r') as passfile:
    file_data = yaml.safe_load(passfile)
    cvpPass = file_data['ansible_password']
clnt.connect(['192.168.0.5'], 'arista', cvpPass )

##Cleanup Tenant Container
container_name = "Tenant"
configletName = 'ATD-INFRA'
container = clnt.api.get_container_by_name(container_name)
configlet = clnt.api.get_configlet_by_name(configletName)
result = clnt.api.remove_configlets_from_container("", container, [configlet], True)
#pprint (result)
#print (result['data']['taskIds'])
task = result['data'].get('taskIds')
for item in task:
    #print (item)
    itemExecute = clnt.api.execute_task(item)
    #print (itemExecute)
#result2 = clnt.api.execute_task(result['data']['taskIds'])