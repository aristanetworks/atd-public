#!/usr/bin/python

import getopt
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from rcvpapi.rcvpapi import *
import yaml, syslog, time
import paramiko

DEBUG = False

# Cmds to copy bare startup to running
dev_cmds = """enable
copy startup-config running-config
"""
# Cmds to grab ZTP status
ztp_cmds = """enable
show zerotouch | grep ZeroTouch
"""
# Cancel ZTP
ztp_cancel = """enable
zerotouch cancel
"""

def remove_configlets(client, device, mext=None):
    """
    Removes all configlets except the ones defined here or starting with SYS_
    Define base configlets that are to be untouched
    mext = lab type to keep track of which base configlets to keep.  Added for RATD and RATD-Ring
    """
    base_configlets = ['AAA','aws-infra','ATD-INFRA', 'VLANs']
    
    configlets_to_remove = []
    configlets_to_remain = []

    configlets = client.getConfigletsByNetElementId(device)
    for configlet in configlets['configletList']:
        if configlet['name'] in base_configlets or configlet['name'].startswith('SYS_') or configlet['name'].startswith('BaseIPv4_'):
            # Do further evaluation on RATD topo to distinguish between standard RATD and RATD-Ring modules
            if configlet['name'].startswith('BaseIPv4_'):
                if mext and '_RING' not in configlet['name']:
                    configlets_to_remove.append(configlet['name'])
                elif not mext and '_RING' in configlet['name']:
                    configlets_to_remove.append(configlet['name'])
                else:
                    configlets_to_remain.append(configlet['name'])
            else:
                configlets_to_remain.append(configlet['name'])
            continue
        else:
            pS("INFO", "Configlet {0} not part of base on {1} - Removing from device".format(configlet['name'], device.hostname))
            configlets_to_remove.append(configlet['name'])
    device.removeConfiglets(client, configlets_to_remove)
    client.addDeviceConfiglets(device, configlets_to_remain)
    client.applyConfiglets(device)
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
        
        # Check to see if this is a RATD-Ring topo:
        if 'ring' in lab:
            # Set it back to RATD-Ring Base
            remove_configlets(client, device, lab)
        else:
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
    # Perform a single Save Topology by default
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

def pushBareConfig(veos_host, veos_ip, veos_config):
    """
    Pushes a bare config to the EOS device.
    """

    DEVREBOOT = False
    veos_ssh = paramiko.SSHClient()
    veos_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    veos_ssh.connect(hostname=veos_ip, username="root", password="", port="50001")
    veos_ssh.exec_command("echo 'testing' | tee /mnt/flash/startup-config".format(veos_config))
    veos_ssh.exec_command('FastCli -c "{0}"'.format(dev_cmds))
    stdin, stdout, stderr = veos_ssh.exec_command('FastCli -c "{0}"'.format(ztp_cmds))
    ztp_out = stdout.readlines()
    if 'Active' in ztp_out[0]:
        DEVREBOOT = True
        pS("INFO", "Rebooting {0}...This will take a couple minutes to come back up".format(veos_host))
        #veos_ssh.exec_command("/sbin/reboot -f > /dev/null 2>&1 &")
        veos_ssh.exec_command('FastCli -c "{0}"'.format(ztp_cancel))
    veos_ssh.close()
    return(DEVREBOOT)

def main(argv):
    f = open('/etc/ACCESS_INFO.yaml')
    accessinfo = yaml.safe_load(f)
    f.close()

    f = open('/home/arista/menus/{0}.yaml'.format(argv[1]))
    menuoptions = yaml.safe_load(f)
    f.close()

    options = menuoptions['lab_list']

    # Parse command arguments
    lab = argv[3]
    # try:
    #     opts, args = getopt.getopt(argv,"ht:",["topology="])
    # except getopt.GetOptError:
    #     print_usage(options)
    #     sys.exit(2)
    # for opt, arg in opts:
    #     if opt == '-h':
    #         print_usage(options)
    #         sys.exit()
    #     elif opt in ("-t", "--topology"):
    #         lab = arg
    


    # Check to see if we need the media menu
    # enableControls2 = False
    # try:
    #   with open("/home/arista/enable-media", 'r') as fh:
    #     enableControls2 = True
    # except:
    #   enableControls2 = False

    # if enableControls2:
    #   options.update(menuoptions['media-options'])

    # List of configlets
    labconfiglets = menuoptions['labconfiglets']

    # Check if the topo has CVP
    if 'cvp' in accessinfo['nodes']:
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
        print("Please wait while the {0} lab is prepared...".format(lab))
        if lab in options:
            pS("INFO", "Setting {0} topology to {1} setup".format(accessinfo['topology'], lab))
            update_topology(cvp_clnt, lab, labconfiglets)
        else:
            print_usage(options)
        
        # Execute all tasks generated from reset_devices()
        print('Gathering task information...')
        cvp_clnt.getAllTasks("pending")
        tasks_to_check = cvp_clnt.tasks['pending']
        cvp_clnt.execAllTasks("pending")
        pS("OK", 'Completed setting devices to topology: {}'.format(lab))

        print('Waiting on change control to finish executing...')
        all_tasks_completed = False
        while not all_tasks_completed:
            tasks_running = []
            for task in tasks_to_check:
                if cvp_clnt.getTaskStatus(task['workOrderId'])['taskStatus'] != 'Completed':
                    tasks_running.append(task)
                elif cvp_clnt.getTaskStatus(task['workOrderId'])['taskStatus'] == 'Failed':
                    print('Task {0} failed.'.format(task['workOrderId']))
                else:
                    pass
            
            if len(tasks_running) == 0:
                raw_input("Lab Setup Completed. Please press Enter to continue...")
                all_tasks_completed = True
            else:
                pass
    else:
        # Open up defaults
        f = open('/home/arista/cvp/cvp_info.yaml')
        cvpInfo = yaml.safe_load(f)
        f.close()

        cvpConfigs = cvpInfo["cvp_info"]["configlets"]
        infraConfigs = cvpConfigs["containers"]["Tenant"]

        print("Setting up {0} lab").format(lab)
        for node in accessinfo["nodes"]["veos"]:
            deviceConfig = ""
            hostname = node["hostname"]
            baseConfigs = cvpConfigs["netelements"]
            configs = baseConfigs[hostname] + infraConfigs + labconfiglets[lab][hostname]
            configs = list(dict.fromkeys(configs))
            for config in configs:
                with open('/tmp/atd/topologies/{0}/configlets/{1}'.format(accessinfo['topology'], config), 'r') as configlet:
                    deviceConfig += configlet.read()
            print("Pushing {0} config for {1} on IP {3} with configlets: {2}").format(lab,hostname,configs,node["ip"])
            pushBareConfig(hostname, node["ip"], deviceConfig)
            


if __name__ == '__main__':
    syslog.openlog(logoption=syslog.LOG_PID)
    main(sys.argv[1:])
