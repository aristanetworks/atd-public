#!/usr/bin/env python

from cvprac import cvp_client
from datetime import datetime
import uuid
import time

from rcvpapi.rcvpapi import *
import syslog
from ruamel.yaml import YAML
import paramiko
from scp import SCPClient
from os.path import exists
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


DEBUG = False

TOPO_MENU = '/home/arista/menus/{lab}.yaml'
BASE_CFGS = ['ATD-INFRA']
SLEEP_DELAY = 15

# Cmds to copy bare startup to running
cp_run_start = """enable
copy running-config startup-config
"""
cp_start_run = """enable
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

# Create class to handle configuring the topology
class ConfigureTopology():

    def __init__(self, access_info, cvp_nodes, username, password, public_module_flag=False):
        self.access_info = access_info
        self.username = username
        self.password = password
        self.public_module_flag = public_module_flag
        self.cvp_nodes = cvp_nodes
        self.inventory = {}
        self.cvp_clnt = ''
        self._lab_module = ''
        self._lab = ''
        self._lab_list = {}
        self._lab_cfgs = {}
        self._cc_ids = ''
        self._cc_status = {}
        self._task_ids = []
        # self.deploy_lab()
        if self.cvp_nodes:
            self.connect_to_cvp()
            self.get_cvp_inventory()
            pS("Connected to CVP")
        else:
            pS("No CVP in this topo")

    @property
    def lab_list(self):
        return(self._lab_list)

    @lab_list.setter
    def lab_list(self, lab_list):
        self._lab_list = lab_list
    
    @property
    def lab_cfgs(self):
        return(self._lab_cfgs)
    
    @lab_cfgs.setter
    def lab_cfgs(self, lab_cfgs):
        self._lab_cfgs = lab_cfgs

    @property
    def lab(self):
        return(self._lab)
    
    @lab.setter
    def lab(self, topo_lab):
        _topo_path = TOPO_MENU.format(
            lab = topo_lab
        )
        if exists(_topo_path):
            with open(_topo_path, 'r') as topo_menu:
                _lab_info = YAML().load(topo_menu)
            self.lab_cfgs = _lab_info['labconfiglets']
            self.lab_list = _lab_info['lab_list']
            self._lab = topo_lab
            return(True)
        else:
            pS("Lab not part of topology")
            return(False)
    
    @property
    def task_ids(self):
        return(self._task_ids)

    @task_ids.setter
    def task_ids(self, task_ids):
        self._task_ids = task_ids

    @property
    def cc_ids(self):
        return(self._cc_ids)

    @cc_ids.setter
    def cc_ids(self, cc_ids):
        self._cc_ids = cc_ids
    
    @property
    def cc_status(self):
        return(self._cc_status)

    @cc_status.setter
    def cc_status(self, cc):
        self._cc_status = {
            'id': cc['id'],
            'status': cc['status']
        }

    @property
    def lab_module(self):
        return(self._lab_module)
    
    @lab_module.setter
    def lab_module(self, module):
        if module in self.lab_list:
            pS(f"Updating {self.lab} lab to {module}")
            self._lab_module = module
            if self.cvp_clnt:
                pS("Getting current configlets for nodes via CVP")
                self.get_device_cfgs()
                # Iterate through all nodes and update configlets
                for _node in self.inventory:
                    self.update_device_cfgs(_node)
                # Grab all generated tasks available for CC
                _tmp_task_ids = []
                for _task in self.cvp_clnt.api.change_control_available_tasks():
                    _tmp_task_ids.append(_task['workOrderId'])
                self.task_ids = _tmp_task_ids
                pS(f"Tasks to be added a CC {self.task_ids}")
                # Create a CC for the above tasks
                if self.task_ids:
                    _tmp_uuid = str(uuid.uuid4())
                    response = self.cvp_clnt.api.create_change_control_v3(
                        f"confTopo_{self.lab}_{self.lab_module}_{_tmp_uuid}",
                        f"confTopo_{self.lab}_{self.lab_module}_{_tmp_uuid}",
                        self.task_ids
                    )
                    if len(response) > 0:
                        self.cc_ids = response[0]['id']
                if self.cc_ids:
                    # Approve and execute CC
                    pS(f"Approving CC {self.cc_ids}")
                    self.cvp_clnt.api.approve_change_control(self.cc_ids, timestamp=datetime.utcnow().isoformat() + 'Z')
                    pS(f"Executing CC {self.cc_ids}")
                    self.cvp_clnt.api.execute_change_controls([self.cc_ids])
                    # Loop through to check status of CC
                    while not self.cc_ids:
                        _status = self.cvp_clnt.api.get_change_control_status(self.cc_ids)[0]
                        self.cc_status = {
                            'id': self.cc_ids,
                            'status': _status['status']
                        }
                        if _status['status'] == 'Running':
                            time.sleep(SLEEP_DELAY)
                        else:
                            self.cc_ids = ''
                    pS("Completed CC")

            else:
                pS("Non CVP Topology")

        else:
            pS(f"{module} is not a valid option")

    def connect_to_cvp(self):
        # Adding new connection to CVP via cvprac
        while not self.cvp_clnt:
            try:
                self.cvp_clnt = cvp_client.CvpClient()
                self.cvp_clnt.connect(self.cvp_nodes, self.username, self.password)
                return(True)
            except:
                pS("CVP is currently unavailable....Retrying in 30 seconds.")
                time.sleep(30)

    def get_cvp_inventory(self):
        try:
            for _node in self.cvp_clnt.api.get_inventory():
                self.inventory[_node['hostname']] = {
                    'cvp': _node,
                    'cfgs': self.cvp_clnt.api.get_configlets_by_netelement_id(_node['systemMacAddress'])['configletList']
                }
            return(True)
        except:
            return(False)

    def get_device_info(self):
        eos_devices = []
        for dev in self.client.inventory:
            tmp_eos = self.client.inventory[dev]
            tmp_eos_sw = CVPSWITCH(dev, tmp_eos['ipAddress'])
            tmp_eos_sw.updateDevice(self.client)
            eos_devices.append(tmp_eos_sw)
        return(eos_devices)
    
    def get_device_cfgs(self):
        for _node in self.inventory:
            self.inventory[_node]['cfgs'] = self.cvp_clnt.api.get_configlets_by_netelement_id(self.inventory[_node]['cvp']['systemMacAddress'])['configletList']

    def update_device_cfgs(self, node):
        """
        Function to remove old configlets and apply new configlets to device
        """
        _cfgs_remove = []
        _cfgs_remain = []
        for _cfg in self.inventory[node]['cfgs']:
            if _cfg['name'] not in (BASE_CFGS + self.lab_cfgs[self.lab_module][node]):
                pS(f"Configlet {_cfg['name']} not part of lab configlets on {node} - Removing from device")
                _cfgs_remove.append({
                    'name': _cfg['name'],
                    'key': _cfg['key']
                })
        for _cfg_name in BASE_CFGS + self.lab_cfgs[self.lab_module][node]:
            _cfg_info = self.cvp_clnt.api.get_configlet_by_name(_cfg_name)
            pS(f"Configlet {_cfg_name} will be applied to {node}")
            _cfgs_remain.append({
                'name': _cfg_info['name'],
                'key': _cfg_info['key']
            })
        self.cvp_clnt.api.remove_configlets_from_device("confTopo", self.inventory[node]['cvp'], _cfgs_remove)
        self.cvp_clnt.api.apply_configlets_to_device("confTopo", self.inventory[node]['cvp'], _cfgs_remain)

        

    def remove_configlets(self, device, lab_configlets):
        """
        Removes all configlets except the ones defined as 'base'
        Define base configlets that are to be untouched
        """
        base_configlets = ['ATD-INFRA']
        
        configlets_to_remove = []
        configlets_to_remain = base_configlets

        configlets = self.client.getConfigletsByNetElementId(device)
        for configlet in configlets['configletList']:
            if configlet['name'] in base_configlets:
                configlets_to_remain.append(configlet['name'])
                self.send_to_syslog("INFO", "Configlet {0} is part of the base on {1} - Configlet will remain.".format(configlet['name'], device.hostname))
            elif configlet['name'] not in lab_configlets:
                configlets_to_remove.append(configlet['name'])
                self.send_to_syslog("INFO", "Configlet {0} not part of lab configlets on {1} - Removing from device".format(configlet['name'], device.hostname))
            else:
                pass
        if len(configlets_to_remain) > 0:
            device.removeConfiglets(self.client,configlets_to_remove)
            self.client.addDeviceConfiglets(device, configlets_to_remain)
            self.client.applyConfiglets(device)
        else:
            pass

    def update_topology(self, configlets):
        # Get all the devices in CVP
        devices = self.get_device_info()
        # Loop through all devices
        
        for device in devices:
            # Get the actual name of the device
            device_name = device.hostname
            
            # Define a list of configlets built off of the lab yaml file
            lab_configlets = []
            for configlet_name in configlets[self.selected_lab][device_name]:
                lab_configlets.append(configlet_name)

            # Remove unnecessary configlets
            self.remove_configlets(device, lab_configlets)

            # Apply the configlets to the device
            self.client.addDeviceConfiglets(device, lab_configlets)
            self.client.applyConfiglets(device)

        # Perform a single Save Topology by default
        self.client.saveTopology()

    def send_to_syslog(self, mstat, mtype):
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


    def push_bare_config(self, veos_host, veos_ip, veos_config):
        """
        Pushes a bare config to the EOS device.
        """
        # Write config to tmp file
        device_config = "/tmp/" + veos_host + ".cfg"
        with open(device_config,"a") as tmp_config:
            tmp_config.write(veos_config)

        DEVREBOOT = False
        veos_ssh = paramiko.SSHClient()
        veos_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        veos_ssh.connect(hostname=veos_ip, username="root", password="", port="50001")
        scp = SCPClient(veos_ssh.get_transport())
        scp.put(device_config,remote_path="/mnt/flash/startup-config")
        scp.close()
        veos_ssh.exec_command('FastCli -c "{0}"'.format(cp_start_run))
        veos_ssh.exec_command('FastCli -c "{0}"'.format(cp_run_start))
        stdin, stdout, stderr = veos_ssh.exec_command('FastCli -c "{0}"'.format(ztp_cmds))
        ztp_out = stdout.readlines()
        if 'Active' in ztp_out[0]:
            DEVREBOOT = True
            self.send_to_syslog("INFO", "Rebooting {0}...This will take a couple minutes to come back up".format(veos_host))
            #veos_ssh.exec_command("/sbin/reboot -f > /dev/null 2>&1 &")
            veos_ssh.exec_command('FastCli -c "{0}"'.format(ztp_cancel))
        veos_ssh.close()
        return(DEVREBOOT)

    def check_for_tasks(self):
        self.client.getRecentTasks(50)
        tasks_in_progress = False
        for task in self.client.tasks['recent']:
            if 'in progress' in task['workOrderUserDefinedStatus'].lower():
                self.send_to_syslog('INFO', 'Task Check: Task {0} status: {1}'.format(task['workOrderId'],task['workOrderUserDefinedStatus']))
                tasks_in_progress = True
            else:
                pass
        
        if tasks_in_progress:
            self.send_to_syslog('INFO', 'Tasks in progress. Waiting for 10 seconds.')
            print('Tasks are currently executing. Waiting 10 seconds...')
            time.sleep(10)
            self.check_for_tasks()

        else:
            return


    def deploy_lab(self):


        # Check for additional commands in lab yaml file
        lab_file = open('/home/arista/menus/{0}'.format(self.selected_menu + '.yaml'))
        lab_info = YAML().load(lab_file)
        lab_file.close()

        additional_commands = []
        if 'additional_commands' in lab_info['lab_list'][self.selected_lab]:
            additional_commands = lab_info['lab_list'][self.selected_lab]['additional_commands']

        # Get access info for the topology
        f = open('/etc/atd/ACCESS_INFO.yaml')
        access_info = YAML().load(f)
        f.close()

        # List of configlets
        lab_configlets = lab_info['labconfiglets']

        # Send message that deployment is beginning
        self.send_to_syslog('INFO', 'Starting deployment for {0} - {1} lab...'.format(self.selected_menu,self.selected_lab))
        print("Starting deployment for {0} - {1} lab...".format(self.selected_menu,self.selected_lab))

        # Check if the topo has CVP, and if it does, create CVP connection
        if 'cvp' in access_info['nodes']:
            self.client = self.connect_to_cvp(access_info)

            self.check_for_tasks()

            # Config the topology
            self.update_topology(lab_configlets)
            # Wait time for CVP to generate tasks
            time.sleep(15)
            
            # Execute all tasks generated from reset_devices()
            print('Gathering task information...')
            self.send_to_syslog("INFO", 'Gathering task information')
            self.client.getAllTasks("pending")
            tasks_to_check = self.client.tasks['pending']
            self.send_to_syslog('INFO', 'Relevant tasks: {0}'.format([task['workOrderId'] for task in tasks_to_check]))
            self.client.execAllTasks("pending")
            self.send_to_syslog("OK", 'Completed setting devices to topology: {}'.format(self.selected_lab))

            print('Waiting on change control to finish executing...')
            all_tasks_completed = False
            while not all_tasks_completed:
                tasks_running = []
                for task in tasks_to_check:
                    if self.client.getTaskStatus(task['workOrderId'])['taskStatus'] != 'Completed':
                        tasks_running.append(task)
                    elif self.client.getTaskStatus(task['workOrderId'])['taskStatus'] == 'Failed':
                        print('Task {0} failed.'.format(task['workOrderId']))
                    else:
                        pass
                
                if len(tasks_running) == 0:

                    # Execute additional commands in linux if needed
                    if len(additional_commands) > 0:
                        print('Running additional setup commands...')
                        self.send_to_syslog('INFO', 'Running additional setup commands.')

                        for command in additional_commands:
                            os.system(command)

                    if not self.public_module_flag:
                        input('Lab Setup Completed. Please press Enter to continue...')
                        self.send_to_syslog("OK", 'Lab Setup Completed.')
                    else:
                        self.send_to_syslog("OK", 'Lab Setup Completed.')
                    all_tasks_completed = True
                else:
                    pass
        else:
            # Open up defaults
            f = open('/home/arista/cvp/cvp_info.yaml')
            cvp_info = YAML().load(f)
            f.close()

            cvp_configs = cvp_info["cvp_info"]["configlets"]
            infra_configs = cvp_configs["containers"]["Tenant"]

            self.send_to_syslog("INFO","Setting up {0} lab".format(self.selected_lab))
            for node in access_info["nodes"]["veos"]:
                device_config = ""
                hostname = node["hostname"]
                base_configs = cvp_configs["netelements"]
                configs = base_configs[hostname] + infra_configs + lab_configlets[self.selected_lab][hostname]
                configs = list(dict.fromkeys(configs))
                for config in configs:
                    with open('/opt/atd/topologies/{0}/configlets/{1}'.format(access_info['topology'], config), 'r') as configlet:
                        device_config += configlet.read()
                self.send_to_syslog("INFO","Pushing {0} config for {1} on IP {2} with configlets: {3}".format(self.selected_lab,hostname,node["ip"],configs))
                self.push_bare_config(hostname, node["ip"], device_config)

                # Execute additional commands in linux if needed
                if len(additional_commands) > 0:
                    print('Running additional setup commands...')

                    for command in additional_commands:
                        os.system(command)
            if not self.public_module_flag:
                input('Lab Setup Completed. Please press Enter to continue...')
                self.send_to_syslog("OK", 'Lab Setup Completed.')
            else:
                self.send_to_syslog("OK", 'Lab Setup Completed.')

# =========================================================
# Utility Functions
# =========================================================

def pS(mtype):
    """
    Function to send output from service file to Syslog
    """
    cur_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mmes = "\t" + mtype
    print("[{0}] {1}".format(cur_dt, mmes.expandtabs(7 - len(cur_dt))))
