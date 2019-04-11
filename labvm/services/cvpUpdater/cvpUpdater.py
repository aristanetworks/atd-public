#!/usr/bin/env python


from ruamel.yaml import YAML
import requests, json, syslog
from os import path
from time import sleep

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


topo_file = '/etc/ACCESS_INFO.yaml'
CVP_CONFIG_FIILE = '/home/arista/.cvpState.txt'
CVP_CONTAINERS = []

# ==================================
# Class definition for EOS devices
# ==================================
class CVPSWITCH():
    def __init__(self,host,vx_ip,t_cnt):
        self.serial_num = ""
        self.fqdn = ""
        self.hostname = host
        self.ip = vx_ip
        self.targetContainerName = t_cnt
        self.parentContainer = ""
        self.sys_mac = ""
        self.configlets = {"keys":[],"names":[]}
    
    def updateContainer(self,CVPOBJ):
        CVPOBJ.getDeviceInventory()
        self.sys_mac = CVPOBJ.inventory[self.hostname]["systemMacAddress"]
        self.parentContainer = CVPOBJ.getContainerInfo(CVPOBJ.inventory[self.hostname]["parentContainerKey"])

# ==================================
# Class definition for working with CVP
# ==================================
class CVPCON():
    def __init__(self,cvp_url,c_user,c_pwd):
        self.cvp_url = cvp_url
        self.cvp_user = c_user
        self.cvp_pwd = c_pwd
        self.inventory = {}
        self.tasks = {}
        self.cvp_api = {
            'authenticate': 'cvpservice/login/authenticate.do',
            'searchTopo': 'cvpservice/provisioning/searchTopology.do',
            'getContainer': 'cvpservice/inventory/containers?name=',
            'getContainerInfo': '/cvpservice/provisioning/getContainerInfoById.do',
            'addTempAction': 'cvpservice/provisioning/addTempAction.do',
            'deviceInventory': 'cvpservice/inventory/devices',
            'saveTopo': 'cvpservice/provisioning/v2/saveTopology.do',
            'getAllTemp': 'cvpservice/provisioning/getAllTempActions.do?startIndex=0&endIndex=0',
            'getAllTasks': 'cvpservice/task/getTasks.do',
            'executeAllTasks': 'cvpservice/task/executeTask.do',
            'getTaskStatus': 'cvpservice/task/getTaskStatusById.do',
            'generateCB': 'cvpservice/configlet/autoConfigletGenerator.do',
            'getTempConfigs': 'cvpservice/provisioning/getTempConfigsByNetElementId.do'
        }
        self.headers = {
            'Content-Type':'application/json',
            'Accept':'application/json'
        }
        self.SID = self.getSID()
        self.containers = {
            'Tenant': {'name':'Tenant','key':self.getContainerId('Tenant')[0]["Key"]},
            'Undefined': {'name':'Undefined','key':self.getContainerId('Undefined')[0]["Key"]}
        }
        self.getDeviceInventory()

    def _sendRequest(self,c_meth,url,payload={},ret_json=True):
        response = requests.request(c_meth,"https://{}/".format(self.cvp_url) + url,json=payload,headers=self.headers,verify=False)
        if ret_json:
            return(response.json())
        else:
            return(response)
    
    def saveTopology(self):
        payload = self._sendRequest("GET",self.cvp_api['getAllTemp'])['data']
        response = self._sendRequest("POST",self.cvp_api['saveTopo'],payload)
        return(response)
        
    def getSID(self):
        payload = {
            'userId':self.cvp_user,
            'password':self.cvp_pwd
        }
        response = self._sendRequest("POST",self.cvp_api['authenticate'],payload)
        self.headers['Cookie'] = 'session_id={}'.format(response['sessionId'])
        return(response['sessionId'])
    
    def saveTopo(self):
        payload = []
        response = self._sendRequest("POST",self.cvp_api['saveTopo'],payload)
        return(response)
    
    def getContainerId(self,cnt_name):
        response = self._sendRequest("GET",self.cvp_api['getContainer'] + cnt_name)
        return(response)
    
    def getContainerInfo(self,cnt_key):
        response = self._sendRequest("GET",self.cvp_api['getContainerInfo'] + '?containerId={0}'.format(cnt_key))
        return(response)

    def getDeviceId(self,vEOS):
        pass
    
    def addContainer(self,cnt_name,pnt_name):
        msg = "Creating {0} container under the {1} container".format(cnt_name,pnt_name)
        payload = {
            'data': [
                {
                    'info': msg,
                    'infoPreview': msg,
                    'action': 'add',
                    'nodeType': 'container',
                    'nodeId': 'new_container',
                    'toId': self.containers[pnt_name]["key"],
                    'fromId': '',
                    'nodeName': cnt_name,
                    'fromName': '',
                    'toName': self.containers[pnt_name]["name"],
                    'childTasks': [],
                    'parentTask': '',
                    'toIdType': 'container'
                }
            ]
        }
        response = self._sendRequest("POST",self.cvp_api['addTempAction'] + "?format=topology&queryParam=&nodeId=root",payload)
        return(response)

    def addDeviceInventory(self,eos_ip):
        payload = {
            "hosts": [eos_ip]
        }
        response = self._sendRequest("POST",self.cvp_api['deviceInventory'],payload)
        return(response)
    
    def getDeviceInventory(self):
        response = self._sendRequest("GET",self.cvp_api['deviceInventory'] + "?provisioned=true")
        for res in response:
            self.inventory[res['hostname']] = {"fqdn":res['fqdn'],'ipAddress':res['ipAddress'],'parentContainerKey':res['parentContainerKey'],"systemMacAddress":res["systemMacAddress"]}
    
    def moveDevice(self,eos_obj):
        msg = "Moving {0} device under the {1} container".format(eos_obj.hostname,eos_obj.targetContainerName)
        payload = {
            'data': [
                {
                    'info': msg,
                    'infoPreview': msg,
                    'action': 'update',
                    'nodeType': 'netelement',
                    'nodeId': eos_obj.sys_mac,
                    'toId': self.containers[eos_obj.targetContainerName]["key"],
                    'fromId': self.containers[eos_obj.parentContainer["name"]]["key"],
                    'nodeName': eos_obj.hostname,
                    'fromName': eos_obj.parentContainer["name"],
                    'toName': eos_obj.targetContainerName,
                    'childTasks': [],
                    'parentTask': '',
                    'toIdType': 'container'
                }
            ]
        }
        response = self._sendRequest("POST",self.cvp_api['addTempAction'] + "?format=topology&queryParam=&nodeId=root",payload)
        return(response)

    def getAllTasks(self,t_type):
        response = self._sendRequest("GET",self.cvp_api['getAllTasks'] + "?queryparam={0}&startIndex=0&endIndex=0".format(t_type))
        self.tasks[t_type] = response['data']
    
    def execAllTasks(self,t_type):
        data = []
        if t_type in self.tasks.keys():
            if self.tasks[t_type]:
                for task in self.tasks[t_type]:
                    data.append(task['workOrderId'])
        if data:
            payload = {"data": data }
            response = self._sendRequest("POST",self.cvp_api['executeAllTasks'],payload)
            for task in data:
                while True:
                    t_response = self.getTaskStatus(task)
                    if 'Task Update In Progress' not in t_response['taskStatus']:
                        pS("OK","Task Id: {0} has {1}".format(task,t_response['taskStatus']))
                        break
                    else:
                        pS("INFO","Task Id: {0} Still in progress....sleeping".format(task))
                        sleep(10)
            self.getAllTasks(t_type)
            return(response)
    
    def getTaskStatus(self,t_id):
        response = self._sendRequest("GET",self.cvp_api['getTaskStatus'] + "?taskId={0}".format(t_id))
        return(response)
    
    def getTempConfigs(self,eos_obj,c_type):
        ret_configs = []
        cnvt_id = eos_obj.sys_mac.replace(":","%3A")
        response = self._sendRequest("GET",self.cvp_api['getTempConfigs'] + "?netElementId={0}".format(cnvt_id))
        for p_config in response['proposedConfiglets']:
            if p_config['type'] == c_type:
                ret_configs.append(p_config['key'])
            if p_config['type'] != "Builder":
                eos_obj.configlets["keys"].append(p_config['key'])
                eos_obj.configlets["names"].append(p_config['name'])
        return(ret_configs)
    
    def genConfigBuilders(self,eos_obj):
        payload = {
            'netElementIds':[eos_obj.sys_mac],
            'containerId': self.containers[eos_obj.targetContainerName]['key'],
            'pageType': 'netelement'
        }
        tmp_cb = self.getTempConfigs(eos_obj,"Builder")
        for cb in tmp_cb:
            payload['configletBuilderId'] = cb
            response = self._sendRequest("POST",self.cvp_api['generateCB'],payload)
            eos_obj.configlets["keys"].append(response['data'][0]['configlet']['key'])
            eos_obj.configlets["names"].append(response['data'][0]['configlet']['name'])
        return(response)
    
    def applyConfiglets(self,eos_obj):
        msg = "Applying configlets to {0}".format(eos_obj.hostname)
        payload = {
            'data': [
                {
                    'info': msg,
                    'infoPreview': msg,
                    'action': 'associate',
                    'nodeType': 'configlet',
                    'configletList': eos_obj.configlets["keys"],
                    'configletNamesList': eos_obj.configlets["names"],
                    'ignoreConfigletNamesList': [],
                    'ignoreConfigletList': [],
                    'configletBuilderList': [],
                    'configletBuilderNamesList': [],
                    'ignoreConfigletBuilderList': [],
                    'ignoreConfigletBuilderNamesList': [],
                    'nodeId': '',
                    'toId': eos_obj.sys_mac,
                    'fromId': '',
                    'nodeName': '',
                    'fromName': '',
                    'toName': eos_obj.fqdn,
                    'nodeIpAddress': eos_obj.ip,
                    'nodeTargetIpAddress': eos_obj.ip,
                    'childTasks': [],
                    'parentTask': '',
                    'toIdType': 'netelement'
                }
            ]
        }
        response = self._sendRequest("POST",self.cvp_api['addTempAction'] + "?format=topology&queryParam=&nodeId=root",payload)
        return(response)


# ==================================
# End of Class Object declarations
# ==================================

# ==================================
# Start of Global Functions
# ==================================
def getTopoInfo():
    topoInfo = open(topo_file,'r')
    topoYaml = YAML().load(topoInfo)
    topoInfo.close()
    return(topoYaml)

def checkContainer(cnt):
    if cnt not in CVP_CONTAINERS:
        CVP_CONTAINERS.append(cnt)

def getEosDevice(topo,eosYaml):
    EOS_DEV = []
    for dev in eosYaml:
        if 'spine' in dev['hostname']:
            EOS_DEV.append(CVPSWITCH(dev['hostname'],dev['vxlan_ip'],'Spine'))
            #EOS_DEV[dev['hostname']] = {'vx_ip':dev['vxlan_ip'],'container':'Spine','p_cnt_key':'','c_cnt_key':''}
            checkContainer('Spine')
        elif 'leaf' in dev['hostname']:
            EOS_DEV.append(CVPSWITCH(dev['hostname'],dev['vxlan_ip'],'Leaf'))
            #EOS_DEV[dev['hostname']] = {'vx_ip':dev['vxlan_ip'],'container':'Leaf','p_cnt_key':'','c_cnt_key':''}
            checkContainer('Leaf')
        elif 'cvx' in dev['hostname']:
            EOS_DEV.append(CVPSWITCH(dev['hostname'],dev['vxlan_ip'],'CVX'))
            #EOS_DEV[dev['hostname']] = {'vx_ip':dev['vxlan_ip'],'container':'CVX','p_cnt_key':'','c_cnt_key':''}
            checkContainer('CVX')
        else:
            EOS_DEV.append(CVPSWITCH(dev['hostname'],dev['vxlan_ip'],''))
            #EOS_DEV[dev['hostname']] = {'vx_ip':dev['vxlan_ip'],'container':'NONE','p_cnt_key':'','c_cnt_key':''}
    return(EOS_DEV)

def pS(mstat,mtype):
    """
    Function to send output from service file to Syslog
    """
    mmes = "\t" + mtype
    syslog.syslog("[{0}] {1}".format(mstat,mmes.expandtabs(7 - len(mstat))))

def main():
    cvp_clnt = ""
    atd_yaml = getTopoInfo()
    eos_info = getEosDevice(atd_yaml['topology'],atd_yaml['nodes']['veos'])
    for c_login in atd_yaml['login_info']['cvp']['shell']:
        if c_login['user'] == 'arista':
            while not cvp_clnt:
                try:
                    cvp_clnt = CVPCON(atd_yaml['nodes']['cvp'][0]['ip'],c_login['user'],c_login['pw'])
                except:
                    pS("ERROR","CVP is currently unavailable....Retrying in 30 seconds.")
                    sleep(30)
    if cvp_clnt:
        # Add new containers into CVP
        for p_cnt in CVP_CONTAINERS:
            cvp_clnt.addContainer(p_cnt,"Tenant")
            cvp_clnt.saveTopo()
            cvp_response = cvp_clnt.getContainerId(p_cnt)[0]
            cvp_clnt.containers[p_cnt] = {"name":cvp_response['Name'],"key":cvp_response['Key']}
            pS("OK","Added {0} container".format(p_cnt))
        # Add devices to Inventory/Provisioning
        for eos in eos_info:
            # Check to see if the device is already provisioned
            if eos.hostname not in cvp_clnt.inventory.keys():
                if eos.targetContainerName:
                    cvp_clnt.addDeviceInventory(eos.ip)
                    eos.updateContainer(cvp_clnt)
                    if eos.targetContainerName != eos.parentContainer["name"]:
                        cvp_clnt.moveDevice(eos) 
                        cvp_clnt.applyConfiglets(eos)
            else:
                pS("INFO","Skipping {}".format(eos.hostname))
        cvp_clnt.saveTopology()
        cvp_clnt.getAllTasks("pending")
        cvp_clnt.execAllTasks("pending")
    else:
        pS("ERROR","Couldn't connect to CVP")

if __name__ == '__main__':
    # Open Syslog
    syslog.openlog(logoption=syslog.LOG_PID)
    pS("OK","Starting...")

    if not path.exists(CVP_CONFIG_FIILE):
        # Start the main Service
        pS("OK","Initial ATD Topo Boot")
        main()
        with open(CVP_CONFIG_FIILE,'w') as tf:
            tf.write("CVP_CONFIGURED")
        pS("OK","Completed CVP Configuration")
    else:
        pS("OK","CVP is already configured")
