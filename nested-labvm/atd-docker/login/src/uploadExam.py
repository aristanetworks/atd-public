#!/usr/bin/env python

# This script will export the running configs of each switch.  Make sure eAPI is configured correctly

import time
import jsonrpclib
import yaml
import ssl
import sys,os,re
import tarfile
from ftplib import FTP
import json
from base64 import b64decode, b64encode

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


labACCESS = '/etc/atd/ACCESS_INFO.yaml'
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

def encodeID(tmp_data):
    tmp_str = json.dumps(tmp_data).encode()
    enc_str = b64encode(tmp_str).decode()
    return(enc_str)

def readLabDetails():
    # get the lab password and the topolgy in use
    with open(labACCESS) as f:
        labDetails = yaml.load(f,Loader=yaml.FullLoader)
    return labDetails['login_info']['jump_host']['pw'], labDetails['topology'],labDetails['name']



def readAtdTopo(labTopology):
    #get a list of all IP addresses in the topology
    with open("/opt/atd/topologies/"+ labTopology +"/topo_build.yml") as f:
        topology = yaml.load(f,Loader=yaml.FullLoader)
    #   print(topology)
        mylist= topology['nodes']
        test=[]
        for item in mylist:
           test.append(list(item.keys()))
           hostsName = [item for sublist in test for item in sublist]
    hostsIP = []
    for a in topology['nodes']:
        for key in a.keys():
            hostsIP.append(a[key]['ip_addr'])
    return hostsIP, hostsName

def checkEmail(email):
    if(re.fullmatch(regex, email)):
#        print("Valid Email")
        return 1
    else:
        print("Invalid Email")
        return 0


def ftpUpload(filename):
    try:
        with FTP('rpmainserver.ddns.net', 'ftpuser', 'ftparista') as ftp, open(str(filename), 'rb') as file:
            ftp.cwd('/files/')
            if filename in ftp.nlst():
                print("It looks like you have already uploaded your exam files. If you think this is an error please contract Arista training - training@arista.com")
            else:
                ftp.storbinary('STOR ' + str(filename), file)
    except:
        raise

def getUserInfo():
    accept = "n"
    emailCounter = 0
    print("This script requires eAPI to be enabled and functioning. By default this should work, however if any of the settings have been modified it many not work correctly")
    print("You should only upload once you have finished your exam. Once uploaded you will NOT be able to do it again without contacting Arista training or SDN-Pros.")
    while accept != "y":
        accept = input ("Do you accept this? (y/n) ")
        if accept == "n":
            sys.exit()
    fullName = input("Please provide your full name: ")
    fullName = fullName.replace(' ','')
    email = input("Please provide your email address: ")
    while checkEmail(email) == 0:
        emailCounter +=1
        if emailCounter == 4:
            print("You have entered your email incorrect too many times, please restart")
            sys.exit()
        email = input ("Please provide your email address: ")

    candidateID = input("Please provide your candidateID: ")
    return fullName, email, candidateID

def createUserFile(fullName,email,candidateID,folder,labName,labTopology):
    topo_id = encodeID({'instance': labName,'topology': labTopology})
    with open(folder + "/User-Details", 'w') as f:
         f.writelines(["Name = " + fullName,"\nEmail address = " + email,"\nCandidateID = " + candidateID, "\nLab Name = " + labName,"\nLab Token = " + topo_id,"\n"])
    print("Written user details to file")



def main():
    labPassword, labTopology, labName = readLabDetails()
    allHostsIP, allHostsName = readAtdTopo(labTopology)
    restarted = 0
    fullName, email, candidateID = getUserInfo()
    folder = str(fullName)
#    print(folder)
    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
        except OSError as exc: # Guard against race condition
                raise
    for name, ip in zip(allHostsName,allHostsIP):
        switch = jsonrpclib.Server("https://arista:{password}@{ipaddress}/command-api".format(password = labPassword, ipaddress = ip))
        try:
            config = switch.runCmds(1,["enable", "show running-config"],"text")
            runConfig = (config[1]["output"])
        except:
            print("Check eAPI is enabled on {switch}".format(switch = name))
        else:
            filename = str(name) + ".txt"
            completePath = os.path.join(folder, filename)
            with open(completePath, 'w') as f:
                f.write(runConfig)
            print("Switch {switch} config saved".format(switch = name))
    tarFile = folder + "-" + candidateID
    createUserFile(fullName,email,candidateID,folder,labName,labTopology)
    print("This file will be created and uploaded " + tarFile)
    with tarfile.open(tarFile, "w:gz") as tar:
        tar.add(os.getcwd() + "/" + folder, arcname=os.path.basename(tarFile))
    ftpUpload(tarFile)


main()