#!/usr/bin/python

import getopt
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import cvprac.cvp_client
from cvprac.cvp_client_errors import CvpLoginError
import yaml

def remove_configlets(client, device):
    # Define base configlets that are to be untouched
    base_configlets = ['AAA', 'VLANs']

    # Remove all configlets, except base_configlets or SYS_...
    configlets_to_remove = []

    device_id = device['systemMacAddress']
    configlets = client.api.get_configlets_by_device_id(device_id)
    for configlet in configlets:
        if configlet['name'] in base_configlets or configlet['name'].startswith('SYS_'):
            continue
        else:
            print 'Configlet %s not part of base on %s - Removing from device' % (configlet['name'], device['fqdn'])
            configlets_to_remove.append( {'name': configlet['name'], 'key': configlet['key']} )

    client.api.remove_configlets_from_device('ConfigureTopology', device, configlets_to_remove)
    return

def get_devices(client):
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
    devices = get_devices(client)
    for device in devices:
        device_name = device['fqdn'].split('.')[0]

        remove_configlets(client, device)
        
        if lab != 'reset' and device_name in configlets[lab]:
          lab_configlets = []

          for configlet_name in configlets[lab][device_name]:
             lab_configlet = client.api.get_configlet_by_name(configlet_name)
             lab_configlets.append({'name': lab_configlet['name'], 'key': lab_configlet['key']})

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

    lab = 'reset'

    try:
        opts, args = getopt.getopt(argv,"ht:",["topology="])
    except getopt.GetOptError:
        print_usage(menuoptions['options'])
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print_usage(menuoptions['options'])
            sys.exit()
        elif opt in ("-t", "--topology"):
            lab = arg

    labconfiglets = menuoptions['labconfiglets']

    topology = accessinfo['topology']

    cvlogin = accessinfo['login_info']['cvp']['gui'][0]
    cvip = accessinfo['nodes']['cvp'][0]['internal_ip']

    user = 'arista' # someday should be cvlogin['user']
    pwd = 'arista' # cvlogin['pw']

    cvp_client = cvprac.cvp_client.CvpClient()

    try:
        cvp_client.connect([cvip], user, pwd)
    except CvpLoginError as e:
        print 'CvpLoginError has occured...Error Message:'
        print e.msg
        sys.exit(2)

    if lab in menuoptions['options']:
      update_topology(cvp_client, lab, labconfiglets)
    else:
      print_usage(menuoptions['options'])

    # Execute all tasks generated from reset_devices()
    execute_pending_tasks(cvp_client)
    print 'Completed setting devices to topology: %s' % lab

if __name__ == '__main__':
    main(sys.argv[1:])
