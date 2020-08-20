#!/usr/bin/env python3

import getopt
import sys
from rcvpapi.rcvpapi import *
import syslog, time
from ruamel.yaml import YAML
import paramiko
from scp import SCPClient
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import logging
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

DEBUG = False

# Cmds to copy bare startup to running
cpRunStart = """enable
copy running-config startup-config
"""
cpStartRun = """enable
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
class ConfigureTopology:

    def remove_configlets(self,client, device, lab_configlets):
        """
        Removes all configlets except the ones defined here or starting with SYS_
        Define base configlets that are to be untouched
        mext = lab type to keep track of which base configlets to keep.  Added for RATD and RATD-Ring
        """
        base_configlets = ['ATD-INFRA']
        
        configlets_to_remove = []
        configlets_to_remain = base_configlets

        configlets = client.getConfigletsByNetElementId(device)
        for configlet in configlets['configletList']:
            if configlet['name'] not in base_configlets or configlet['name'] not in lab_configlets:
                configlets_to_remove.append(configlet['name'])
                self.send_to_syslog("INFO", "Configlet {0} not part of base on {1} - Removing from device".format(configlet['name'], device.hostname))
            elif configlet['name'] in base_configlets:
                configlets_to_remain.append(configlet['name'])
                self.send_to_syslog("INFO", "Configlet {0} is part of the base on {1} - Configlet will remain.".format(configlet['name'], device.hostname))
            else:
                pass
        device.removeConfiglets(client, configlets_to_remove)
        client.addDeviceConfiglets(device, configlets_to_remain)
        client.applyConfiglets(device)


    def get_device_info(self,client):
        eos_devices = []
        for dev in client.inventory:
            tmp_eos = client.inventory[dev]
            tmp_eos_sw = CVPSWITCH(dev, tmp_eos['ipAddress'])
            tmp_eos_sw.updateDevice(client)
            eos_devices.append(tmp_eos_sw)
        return(eos_devices)


    def update_topology(self,client,lab,configlets):
        # Get all the devices in CVP
        devices = self.get_device_info(client)
        # Loop through all devices
        
        for device in devices:
            # Get the actual name of the device
            device_name = device.hostname
            
            # Define a list of configlets built off of the lab yaml file
            lab_configlets = []
            for configlet_name in configlets[lab][device_name]:
                lab_configlets.append(configlet_name)

            # Remove unnecessary configlets
            self.remove_configlets(client, device, lab_configlets)

            # Apply the configlets to the device
            client.addDeviceConfiglets(device, lab_configlets)
            client.applyConfiglets(device)

        # Perform a single Save Topology by default
        client.saveTopology()

    def print_usage(self,topologies):
        # Function to print help menu with valid topologies
        print('Usage:')
        print('')
        print('ConfigureTopology.py - No options will reset the topology to the base')
        print('  -t Topology to push out to devices')
        print('')
        print('Valid topologies are:')
        print(', '.join(topologies))
        print('')
        quit()

    def send_to_syslog(self,mstat,mtype):
        """
        Function to send output from service file to Syslog
        Parameters:
        mstat = Message Status, ie "OK", "INFO" (required)
        mtype = Message to be sent/displayed (required)
        """
        mmes = "\t" + mtype
        logging.info("[{0}] {1}".format(mstat,mmes.expandtabs(7 - len(mstat))))
        if DEBUG:
            print("[{0}] {1}".format(mstat,mmes.expandtabs(7 - len(mstat))))


    def push_bare_config(self,veos_host, veos_ip, veos_config):
        """
        Pushes a bare config to the EOS device.
        """
        # Write config to tmp file
        deviceConfig = "/tmp/" + veos_host + ".cfg"
        with open(deviceConfig,"a") as tmpConfig:
            tmpConfig.write(veos_config)

        DEVREBOOT = False
        veos_ssh = paramiko.SSHClient()
        veos_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        veos_ssh.connect(hostname=veos_ip, username="root", password="", port="50001")
        scp = SCPClient(veos_ssh.get_transport())
        scp.put(deviceConfig,remote_path="/mnt/flash/startup-config")
        scp.close()
        veos_ssh.exec_command('FastCli -c "{0}"'.format(cpStartRun))
        veos_ssh.exec_command('FastCli -c "{0}"'.format(cpRunStart))
        stdin, stdout, stderr = veos_ssh.exec_command('FastCli -c "{0}"'.format(ztp_cmds))
        ztp_out = stdout.readlines()
        if 'Active' in ztp_out[0]:
            DEVREBOOT = True
            self.send_to_syslog("INFO", "Rebooting {0}...This will take a couple minutes to come back up".format(veos_host))
            #veos_ssh.exec_command("/sbin/reboot -f > /dev/null 2>&1 &")
            veos_ssh.exec_command('FastCli -c "{0}"'.format(ztp_cancel))
        veos_ssh.close()
        return(DEVREBOOT)

    def deploy_lab(self,selected_menu,selected_lab):

        # Check for additional commands in lab yaml file
        lab_file = open('/home/arista/menus/{0}'.format(selected_menu + '.yaml'))
        lab_info = YAML().load(lab_file)
        lab_file.close()

        additional_commands = []
        if 'additional_commands' in lab_info['lab_list'][selected_lab]:
            additional_commands = lab_info['lab_list'][selected_lab]['additional_commands']

        # Get access info for the topology
        f = open('/etc/ACCESS_INFO.yaml')
        access_info = YAML().load(f)
        f.close()

        # List of configlets
        lab_configlets = lab_info['labconfiglets']

        # Send message that deployment is beginning
        print("Starting deployment for {0} - {1} lab...".format(selected_menu,selected_lab))

        # Check if the topo has CVP
        if 'cvp' in access_info['nodes']:
            # Adding new connection to CVP via rcvpapi
            cvp_clnt = ''
            for c_login in access_info['login_info']['cvp']['shell']:
                if c_login['user'] == 'arista':
                    while not cvp_clnt:
                        try:
                            cvp_clnt = CVPCON(access_info['nodes']['cvp'][0]['internal_ip'],c_login['user'],c_login['pw'])
                            self.send_to_syslog("OK","Connected to CVP at {0}".format(access_info['nodes']['cvp'][0]['internal_ip']))
                        except:
                            self.send_to_syslog("ERROR", "CVP is currently unavailable....Retrying in 30 seconds.")
                            time.sleep(30)

            # Config the topology
            self.update_topology(cvp_clnt,selected_lab,lab_configlets)
            
            # Execute all tasks generated from reset_devices()
            print('Gathering task information...')
            cvp_clnt.getAllTasks("pending")
            tasks_to_check = cvp_clnt.tasks['pending']
            cvp_clnt.execAllTasks("pending")
            self.send_to_syslog("OK", 'Completed setting devices to topology: {}'.format(selected_lab))

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
                    input("Lab Setup Completed. Please press Enter to continue...")
                    all_tasks_completed = True
                else:
                    pass
        else:
            # Open up defaults
            f = open('/home/arista/cvp/cvp_info.yaml')
            cvpInfo = YAML.load(f)
            f.close()

            cvpConfigs = cvpInfo["cvp_info"]["configlets"]
            infraConfigs = cvpConfigs["containers"]["Tenant"]

            self.send_to_syslog("INFO","Setting up {0} lab".format(selected_lab))
            for node in access_info["nodes"]["veos"]:
                deviceConfig = ""
                hostname = node["hostname"]
                baseConfigs = cvpConfigs["netelements"]
                configs = baseConfigs[hostname] + infraConfigs + lab_configlets[selected_lab][hostname]
                configs = list(dict.fromkeys(configs))
                for config in configs:
                    with open('/tmp/atd/topologies/{0}/configlets/{1}'.format(access_info['topology'], config), 'r') as configlet:
                        deviceConfig += configlet.read()
                self.send_to_syslog("INFO","Pushing {0} config for {1} on IP {2} with configlets: {3}".format(selected_lab,hostname,node["ip"],configs))
                self.push_bare_config(hostname, node["ip"], deviceConfig)