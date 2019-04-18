#!/usr/bin/env python
"""
Script that will reset all EOS devices back to a base config
"""

import requests, json, argparse
from ruamel.yaml import YAML
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Output directory:

CFG_OUT = 'base_configlets/'
ACCESS = '/etc/ACCESS_INFO.yaml'
#ACCESS = 'ACCESS_INFO.yaml'


ATD_CVP = "192.168.0.5"

BASE_CFGS = [
    ['AAA','Static'],
    ['VLANs','Static'],
    ['SYS_BaseConfig','Generated'],
    ['SYS_Telem','Generated'],
    ['cvx01-Controller','Static']]

eos_cfgs = {}

with open(ACCESS,'r') as a_yaml:
    veos_yaml = YAML().load(a_yaml)['nodes']['veos']

for node in veos_yaml:
    if 'host' not in node['hostname']:
        eos_cfgs[node['internal_ip']] = {'name':node['hostname'],'config':[],'vx_ip':node['ip']}


class CVPSWITCH():
    def __init__(self,sw):
        self.serial_num = sw['serialNumber']
        self.fqdn = sw['fqdn']
        self.hostname = sw['hostname']
        self.ip = sw['ipAddress']
        self.com_code = sw['complianceCode']
        self.com_status = sw['complianceIndication']
        self.eos_version = sw['version']
        self.streaming = sw['streamingStatus']
        self.sys_mac = sw['systemMacAddress']
        self.status = sw['status']
        self.all_data = sw


class CVPCON():
    def __init__(self,cvp_url,c_user,c_pwd):
        self.cvp_url = cvp_url
        self.cvp_user = c_user
        self.cvp_pwd = c_pwd
        self.cvp_headers = {
            'Content-Type':'application/json',
            'Accept':'application/json'
        }
        self.cur_sid = self.getSID(c_user,c_pwd)
        self.cvp_version = self._checkVersion()
        self.cvp_inventory = []
        self.cvp_inventory_sn = []

    def _sendRequest(self,c_meth,url,payload={}):
        response = requests.request(c_meth,"https://{}/".format(self.cvp_url) + url,json=payload,headers=self.cvp_headers,verify=False)
        return(response.json())

    def getSID(self,c_user,c_pwd):
        url = 'cvpservice/login/authenticate.do'
        payload = {
            'userId':c_user,
            'password':c_pwd
            }
        response = self._sendRequest("POST",url,payload)
        self.cvp_headers['Cookie'] = 'session_id={}'.format(response['sessionId'])
        return(response['sessionId'])

    def _checkSession(self):
        url = 'cvpservice/login/home.do'
        if 'Cookie' in self.cvp_headers.keys():
            pass
        else:
            pass
        response = self._sendRequest("GET",url)
        if type(response) == dict:
            if response['data'] == 'success':
                return(True)
            else:
                return(False)
        else:
            return(False)

    def _checkVersion(self):
        url = 'cvpservice/cvpInfo/getCvpInfo.do'
        if self._checkSession():
            return(self._sendRequest("GET",url))

    def getDevices(self):
        url = 'cvpservice/inventory/devices'
        if self._checkSession():
            response = self._sendRequest("GET",url)
            for device in response:
                if device['serialNumber'] not in self.cvp_inventory_sn:
                    self.cvp_inventory.append({device['serialNumber']:CVPSWITCH(device)})
                    self.cvp_inventory_sn.append(device['serialNumber'])

    def getConfiglets(self):
        url = 'cvpservice/configlet/getConfiglets.do?startIndex=0&endIndex=0'
        if self._checkSession():
            response = self._sendRequest("GET",url)
            return(response)
        else:
            return({
                "status":"failed"
            })

def main(args):
    cvp = CVPCON(ATD_CVP,args.user,args.passwd)
    cvp.getDevices()
    cfg_data = cvp.getConfiglets()

    for cfg in cfg_data['data']:
        for b_cfg in BASE_CFGS:
            if b_cfg[0] in cfg['name'] and b_cfg[1] == cfg['type']:
                if cfg['type'] == 'Static':
                    for eos in eos_cfgs.keys():
                        if 'cvx01-Controller' == cfg['name'] and eos_cfgs[eos]['name'] == 'cvx':
                            eos_cfgs[eos]['config'] += str(cfg['config']).split('\n')
                        elif 'cvx' not in cfg['name']:
                            eos_cfgs[eos]['config'] += str(cfg['config']).split('\n')
                elif cfg['type'] == 'Generated':
                    cfg_ip = cfg['name'].split('_')[2]
                    eos_cfgs[cfg_ip]['config'] += str(cfg['config']).split('\n')
    
    for eos in eos_cfgs.keys():
        with open(CFG_OUT + eos_cfgs[eos]['name'],'w') as out_eos:
            out_eos.writelines("\n".join(eos_cfgs[eos]['config']))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u","--user",type=str,help="Enter a valid CVP username",required=True)
    parser.add_argument("-p","--passwd",type=str,help="Entery the password for the CVP user",required=True)

    args = parser.parse_args()

    main(args)

