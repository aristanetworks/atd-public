#!/usr/bin/python

import getopt
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from rcvpapi.rcvpapi import *
import yaml, syslog, time

DEBUG = False

def remove_configlets(client, device):
    # Removes all configlets except the ones defined here or starting with SYS_
    # Define base configlets that are to be untouched
    base_configlets = ['AAA','aws-infa']
    
    configlets_to_remove = []
    configlets_to_remain = []

    configlets = client.getConfigletsByNetElementId(device)
    for configlet in configlets['configletList']:
        if configlet['name'] in base_configlets or configlet['name'].startswith('SYS_') or configlet['name'].startswith('BaseIPv4_'):
            configlets_to_remain.append(configlet['name'])
        else:
            pS("INFO", "Configlet {0} not part of base on {1} - Removing from device".format(configlet['name'], device.hostname))
            configlets_to_remove.append(configlet)
    device.removeConfiglets(client, configlets_to_remove)
    client.addDeviceConfiglets(device, configlets_to_remain)
    client.applyConfiglets(device)
    client.saveTopology()
    return

def getDeviceInfo(client):
    eos_devices = []
    for dev in client.inventory:
        tmp_eos = client.inventory[dev]
        tmp_eos_sw = CVPSWITCH(dev, tmp_eos['ipAddress'])
        tmp_eos_sw.updateDevice(client)
        eos_devices.append(tmp_eos_sw)
    return(eos_devices)


def update_topology(client, lab, configlets):
    # Get all the devices in CVP
    devices = getDeviceInfo(client)
    # Loop through all devices
    # for device in devices:
    for device in devices:
        # Get the actual name of the device
        device_name = device.hostname
        
        # Set everything back to the base
        remove_configlets(client, device)
        
        # Only apply configlets if an actual 'lab' was defined
        # Only apply configlets to devices that are specified in the 'lab'
        # If the device isn't specified in the MenuOptions.yaml, it'll be ignored
        if lab != 'reset' and device_name in configlets[lab]:
          lab_configlets = []
        
          # Define a list of configlets built off of the MenuOptions.yaml
          for configlet_name in configlets[lab][device_name]:
              lab_configlets.append(configlet_name)

          # Apply the configlets to the device
          client.addDeviceConfiglets(device, lab_configlets)
          client.applyConfiglets(device)
          client.saveTopology()

    return

def print_usage(topologies):
    # Function to print help menu with valid topologies
    print 'Usage:'
    print ''
    print 'ConfigureTopology.py - No options will reset the topology to the base'
    print '  -t Topology to push out to devices'
    print ''
    print 'Valid topologies are:'
    print ', '.join(topologies)
    print ''
    quit()

def pS(mstat,mtype):
    """
    Function to send output from service file to Syslog
    Parameters:
    mstat = Message Status, ie "OK", "INFO" (required)
    mtype = Message to be sent/displayed (required)
    """
    mmes = "\t" + mtype
    syslog.syslog("[{0}] {1}".format(mstat,mmes.expandtabs(7 - len(mstat))))
    if DEBUG:
        print("[{0}] {1}".format(mstat,mmes.expandtabs(7 - len(mstat))))

def main(argv):
    f = open('/etc/ACCESS_INFO.yaml')
    accessinfo = yaml.safe_load(f)
    f.close()

    f = open('/home/arista/MenuOptions.yaml')
    menuoptions = yaml.safe_load(f)
    f.close()

    options = menuoptions['options']
    # Check to see if we need the media menu
    enableControls2 = False
    try:
      with open("/home/arista/enable-media", 'r') as fh:
        enableControls2 = True
    except:
      enableControls2 = False

    if enableControls2:
      options.update(menuoptions['media-options'])

    lab = 'reset'

    # Parse command arguments
    try:
        opts, args = getopt.getopt(argv,"ht:",["topology="])
    except getopt.GetOptError:
        print_usage(options)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print_usage(options)
            sys.exit()
        elif opt in ("-t", "--topology"):
            lab = arg

    # List of configlets
    labconfiglets = menuoptions['labconfiglets']

    # Adding new connection to CVP via rcvpapi
    cvp_clnt = ''
    for c_login in accessinfo['login_info']['cvp']['shell']:
        if c_login['user'] == 'arista':
            while not cvp_clnt:
                try:
                    cvp_clnt = CVPCON(accessinfo['nodes']['cvp'][0]['internal_ip'],c_login['user'],c_login['pw'])
                    pS("OK","Connected to CVP at {0}".format(accessinfo['nodes']['cvp'][0]['internal_ip']))
                except:
                    pS("ERROR", "CVP is currently unavailable....Retrying in 30 seconds.")
                    time.sleep(30)

    # Make sure option chosen is valid, then configure the topology
    if lab in options:
        update_topology(cvp_clnt, lab, labconfiglets)
    else:
      print_usage(options)

    # Execute all tasks generated from reset_devices()
    cvp_clnt.getAllTasks("pending")
    cvp_clnt.execAllTasks("pending")
    pS("OK", 'Completed setting devices to topology: {}'.format(lab))

if __name__ == '__main__':
    syslog.openlog(logoption=syslog.LOG_PID)
    main(sys.argv[1:])
