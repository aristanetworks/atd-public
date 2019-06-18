#!/usr/bin/python

import getopt
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import cvprac.cvp_client
from cvprac.cvp_client_errors import CvpLoginError
import yaml

DEBUG = False

def remove_configlets(client, device):
    # Removes all configlets except the ones defined here or starting with SYS_
    # Define base configlets that are to be untouched
    base_configlets = ['AAA','aws-infa']
    
    configlets_to_remove = []

    device_id = device['systemMacAddress']
    configlets = client.api.get_configlets_by_device_id(device_id)
    for configlet in configlets:
        if configlet['name'] in base_configlets or configlet['name'].startswith('SYS_') or configlet['name'].startswith('BaseIPv4_'):
            continue
        else:
            if DEBUG:
               print 'Configlet %s not part of base on %s - Removing from device' % (configlet['name'], device['fqdn'])
            configlets_to_remove.append( {'name': configlet['name'], 'key': configlet['key']} )

    client.api.remove_configlets_from_device('ConfigureTopology', device, configlets_to_remove)
    return

def get_devices(client):
    # Returns a list of devices
    devices = []
    containers = client.api.get_containers()
    container_list = containers['data']
    number_of_containers = containers['total']

    for container in container_list:
        container_name = container['name']
        _devices = client.api.get_devices_in_container(container_name)
        devices.extend(_devices)

    return devices

def update_topology(client, lab, configlets):
    # Get all the devices in CVP
    devices = get_devices(client)
    # Loop through all devices
    for device in devices:
        # Get the actual name of the device
        device_name = device['fqdn'].split('.')[0]
        
        # Set everything back to the base
        remove_configlets(client, device)
        
        # Only apply configlets if an actual 'lab' was defined
        # Only apply configlets to devices that are specified in the 'lab'
        # If the device isn't specified in the MenuOptions.yaml, it'll be ignored
        if lab != 'reset' and device_name in configlets[lab]:
          lab_configlets = []
        
          # Define a list of configlets built off of the MenuOptions.yaml
          for configlet_name in configlets[lab][device_name]:
             lab_configlet = client.api.get_configlet_by_name(configlet_name)
             lab_configlets.append({'name': lab_configlet['name'], 'key': lab_configlet['key']})

          # Apply the configlets to the device
          client.api.apply_configlets_to_device('ConfigureTopology', device, lab_configlets)

    return

def execute_pending_tasks(client):
    tasks = client.api.get_tasks_by_status('Pending')
    for task in tasks:
        client.api.execute_task(task['workOrderId'])

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

    # Topology from ADC
    topology = accessinfo['topology']

    # CVP Info
    cvlogin = accessinfo['login_info']['cvp']['gui'][0]
    cvip = accessinfo['nodes']['cvp'][0]['internal_ip']

    user = 'arista' # someday should be cvlogin['user']
    pwd = 'arista' # cvlogin['pw']

    # Setup the client
    cvp_client = cvprac.cvp_client.CvpClient()

    # Attempt to connect to CVP
    try:
        cvp_client.connect([cvip], user, pwd)
    except CvpLoginError as e:
        if DEBUG:
           print 'CvpLoginError has occured...Error Message:'
           print e.msg
        sys.exit(2)

    # Make sure option chosen is valid, then configure the topology
    if lab in options:
      update_topology(cvp_client, lab, labconfiglets)
    else:
      print_usage(options)

    # Execute all tasks generated from reset_devices()
    execute_pending_tasks(cvp_client)
    if DEBUG:
       print 'Completed setting devices to topology: %s' % lab

if __name__ == '__main__':
    main(sys.argv[1:])
