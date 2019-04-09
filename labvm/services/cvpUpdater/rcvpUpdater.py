#!/usr/bin/env python


from ruamel.yaml import YAML
import git, requests, json, syslog
from time import sleep
from pprint import pprint as pp
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


topo_file = '/etc/ACCESS_INFO.yaml'
CVP_CONTAINERS = []

# Class definition for EOS devices
class CVPSWITCH():
    def __init__(self,host,vx_ip,t_cnt):
        self.serial_num = ""
        self.fqdn = ""
        self.hostname = host
        self.ip = vx_ip
        self.targetContainerName = t_cnt
        self.parentContainer = ""
        self.sys_mac = ""
    
    def updateContainer(self,CVPOBJ):
        CVPOBJ.getDeviceInventory()
        self.parentContainer = CVPOBJ.getContainerInfo(CVPOBJ.inventory[self.hostname]["parentContainerKey"])


# Class definition for working with CVP
class CVPCON():
    def __init__(self,cvp_url,c_user,c_pwd):
        self.cvp_url = cvp_url
        self.cvp_user = c_user
        self.cvp_pwd = c_pwd
        self.cvp_api = {
            'authenticate': 'cvpservice/login/authenticate.do',
            'searchTopo': 'cvpservice/provisioning/searchTopology.do',
            'getContainer': 'cvpservice/inventory/containers?name=',
            'getContainerInfo': '/cvpservice/provisioning/getContainerInfoById',
            'addTempAction': 'cvpservice/provisioning/addTempAction.do',
            'deviceInventory': 'cvpservice/inventory/devices',
            'saveTopo': 'cvpservice/provisioning/v2/saveTopology.do'
        }
        self.headers = {
            'Content-Type':'application/json',
            'Accept':'application/json'
        }
        self.SID = self.getSID()
        self.containers = {
            'Tenant': {'name':'Tenant','key':self.getContainerId('Tenant')[0]["Key"]}
        }
        self.inventory = {}

    def _sendRequest(self,c_meth,url,payload={}):
        response = requests.request(c_meth,"https://{}/".format(self.cvp_url) + url,json=payload,headers=self.headers,verify=False)
        return(response.json())
        
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
            self.inventory[res['hostname']] = {"fqdn":res['fqdn'],'ipAddress':res['ipAddress'],'parentContainerKey':res['parentContainerKey']}
    
    def moveDevice(self,eos_obj):
        msg = "Moving {0} device under the {1} container".format(cnt_name,pnt_name)
        payload = {
            'data': [
                {
                    'info': msg,
                    'infoPreview': msg,
                    'action': 'update',
                    'nodeType': 'netelement',
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
        for p_cnt in CVP_CONTAINERS:
            cvp_clnt.addContainer(p_cnt,"Tenant")
            cvp_clnt.saveTopo()
            cvp_response = cvp_clnt.getContainerId(p_cnt)[0]
            cvp_clnt.containers[p_cnt] = {"name":cvp_response['Name'],"key":cvp_response['Key']}
            pS("OK","Added {0} container".format(p_cnt))
        # Add devices to Inventory/Provisioning
        for eos in eos_info:
            if eos.parentContainer:
                cvp_clnt.addDeviceInventory(eos_info[eos]['vx_ip'])
                eos.updateContainer()
                cvp_clnt.moveDevice(eos) # Finish writing the move device object function
    else:
        pS("ERROR","Couldn't connect to CVP")

if __name__ == '__main__':
    # Open Syslog
    syslog.openlog(logoption=syslog.LOG_PID)
    pS("OK","Starting...")

    # Start the main Service
    main()
