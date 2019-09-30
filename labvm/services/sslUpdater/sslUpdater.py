#!/usr/bin/env python

from rcvpapi.rcvpapi import *
from ruamel.yaml import YAML
import requests, json, syslog, time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Globals
PDEBUG = False
TOPO_FILE = '/etc/ACCESS_INFO.yaml'

# ==================================
# Start of Global Functions
# ==================================
def getTopoInfo(yaml_file):
    """
    Function that parses the supplied YAML file to build the CVP topology.
    """
    topoInfo = open(yaml_file,'r')
    topoYaml = YAML().load(topoInfo)
    topoInfo.close()
    return(topoYaml)

def convertDaysToSeconds(pdays):
    """
    Function to convert days to seconds.
    seconds * minutes * hours * days
    """
    return(60 * 60 * 24 * pdays)

def pS(mstat,mtype):
    """
    Function to send output from service file to Syslog
    Parameters:
    mstat = Message Status, ie "OK", "INFO" (required)
    mtype = Message to be sent/displayed (required)
    """
    mmes = "\t" + mtype
    syslog.syslog("[{0}] {1}".format(mstat,mmes.expandtabs(7 - len(mstat))))
    if PDEBUG:
        print("[{0}] {1}".format(mstat,mmes.expandtabs(7 - len(mstat))))


def main():
    """
    Main function
    """
    # Open connection to CVP
    cvp_clnt = ""
    atd_yaml = getTopoInfo(TOPO_FILE)
    for c_login in atd_yaml['login_info']['cvp']['shell']:
        if c_login['user'] == 'arista':
            while not cvp_clnt:
                try:
                    cvp_clnt = CVPCON(atd_yaml['nodes']['cvp'][0]['ip'],c_login['user'],c_login['pw'])
                    pS("OK","Connected to CVP at {0}".format(atd_yaml['nodes']['cvp'][0]['ip']))
                except:
                    pS("ERROR","CVP is currently unavailable....Retrying in 30 seconds.")
                    sleep(30)
    if cvp_clnt:
        # If connected to CVP, grab ssl information
        cvpSSL = cvp_clnt.getCerts()
        # Check if the SSL cert expires within 14 days
        if time.time() >= ((cvpSSL['validTill'] / 1000) - convertDaysToSeconds(14)):
            try:
                cvp_clnt.generateCert('ATD CVP', 'Arista', 'CloudVision', 'ATD CVP', 365)
                cvp_clnt.installCert()
                pS("INFO","Created and imported new CVP Cert.")
            except:
                pS("ERROR","There was an issue creating and importing a new cert")

if __name__ == '__main__':
    # Open Syslog
    syslog.openlog(logoption=syslog.LOG_PID)
    pS("OK","Starting...")