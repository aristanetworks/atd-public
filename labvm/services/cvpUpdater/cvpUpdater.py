#!/usr/bin/env python


from ruamel.yaml import YAML
from cvprac.cvp_client import CvpClient


import git, requests, json, syslog
from time import sleep
from pprint import pprint as pp

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

topo_file = '/etc/ACCESS_INFO.yaml'
CVP_CONTAINERS = []


def getTopoInfo():
    topoInfo = open(topo_file,'r')
    topoYaml = YAML().load(topoInfo)
    topoInfo.close()
    return(topoYaml)

def checkContainer(cnt):
    if cnt not in CVP_CONTAINERS:
        CVP_CONTAINERS.append(cnt)

def getEosDevice(topo,eosYaml):
    EOS_DEV = {}
    for dev in eosYaml:
        if 'spine' in dev['hostname']:
            EOS_DEV[dev['hostname']] = {'vx_ip':dev['vxlan_ip'],'container':'Spine'}
            checkContainer('Spine')
        elif 'leaf' in dev['hostname']:
            EOS_DEV[dev['hostname']] = {'vx_ip':dev['vxlan_ip'],'container':'Leaf'}
            checkContainer('Leaf')
        elif 'cvx' in dev['hostname']:
            EOS_DEV[dev['hostname']] = {'vx_ip':dev['vxlan_ip'],'container':'CVX'}
            checkContainer('CVX')
        else:
            EOS_DEV[dev['hostname']] = {'vx_ip':dev['vxlan_ip'],'container':'NONE'}
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
                    cvp_clnt = CvpClient()
                    cvp_clnt.connect([atd_yaml['nodes']['cvp'][0]['ip']],c_login['user'],c_login['pw'])
                    # !! cvp_clnt = CVPCON(atd_yaml['nodes']['cvp'][0]['ip'],c_login['user'],c_login['pw'])
                except:
                    pS("ERROR","CVP is currently unavailable....Retrying in 30 seconds.")
                    sleep(30)
    if cvp_clnt:
        # Add new Containers to CVP
        cur_cvp_cnts = cvp_clnt.api.get_containers()
        for p_cnt in CVP_CONTAINERS:
            NEW_CNT = True
            for e_cnt in cur_cvp_cnts['data']:
                if e_cnt['Name'] == p_cnt:
                    NEW_CNT = False
            if NEW_CNT:
                cvp_clnt.api.add_container(p_cnt,"Tenant",cvp_clnt.api.get_container_by_name("Tenant")['key'])
            pS("OK","Added {0} container".format(p_cnt))
        cur_cvp_veos = cvp_clnt.api.get_inventory()
        for veos in eos_info:
            if eos_info[veos]['container'] != "NONE":
                NEW_VEOS = True
                for e_veos in cur_cvp_veos:
                    if veos == e_veos['hostname']:
                        NEW_VEOS = False
                if NEW_VEOS:
                    print(eos_info[veos])
                    print(cvp_clnt.api.get_container_by_name(eos_info[veos]['container'])['key'])
                    cvp_clnt.api.add_device_to_inventory(eos_info[veos]['vx_ip'],eos_info[veos]['container'],cvp_clnt.api.get_container_by_name(eos_info[veos]['container'])['key'])
        # !! Currently device addition is not creating task.
        a = cvp_clnt.api.save_inventory()
        print(a)
        pp(cvp_clnt.api.get_all_temp_actions())
    else:
        pS("ERROR","Couldn't connect to CVP")

if __name__ == '__main__':
    # Open Syslog
    syslog.openlog(logoption=syslog.LOG_PID)
    pS("OK","Starting...")

    # Start the main Service
    main()