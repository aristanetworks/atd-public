#!/bin/bash/python

#Save running config on all switches

import jsonrpclib,ssl,sys
import yaml


#static files
labACCESS = '/etc/atd/ACCESS_INFO.yaml'



try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

def saveRunningConfig(allHosts,labPassword):
    for IPaddress in allHosts:
        try:
            #use eAPI to copy the running-config to start-config
            switch = jsonrpclib.Server("https://arista:{password}@{ipaddress}/command-api".format(password = labPassword, ipaddress = IPaddress))
            switch.runCmds( 1, [ "enable", "copy running-config startup-config" ] )
            print("Done {0}".format(IPaddress))

        except KeyboardInterrupt:
            print("Caught Keyboard Interrupt - Exiting")
            sys.exit()

        except OSError as ERR :
            # Socket Errors
            print(ERR)



def readLabDetails():
    # get the lab password and the topolgy in use
    with open(labACCESS) as f:
        labDetails = yaml.load(f,Loader=yaml.FullLoader)
    return labDetails['login_info']['jump_host']['pw'], labDetails['topology']



def readAtdTopo(labTopology):
    #get a list of all IP addresses in the topology
    with open("/opt/atd/topologies/"+ labTopology +"/topo_build.yml") as f:
       topology = yaml.load(f,Loader=yaml.FullLoader)
    hosts = []
    for a in topology['nodes']:
        for key in a.keys():
            hosts.append(a[key]['ip_addr'])
    return hosts


def main():
    labPassword, labTopology = readLabDetails()
    allHosts = readAtdTopo(labTopology)
    saveRunningConfig(allHosts,labPassword)

main()

