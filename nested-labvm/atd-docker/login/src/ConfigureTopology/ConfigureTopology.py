#!/usr/bin/env python

import json
import os
import syslog
import time

import paramiko
import requests
from ruamel.yaml import YAML
from scp import SCPClient
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEBUG = False

cp_run_start = """enable
copy running-config startup-config
"""
cp_start_run = """enable
copy startup-config running-config
"""
ztp_cmds = """enable
show zerotouch | grep ZeroTouch
"""
ztp_cancel = """enable
zerotouch cancel
"""


class ConfigureTopology():

    def __init__(self, selected_menu, selected_lab, public_module_flag=False):
        self.selected_menu = selected_menu
        self.selected_lab = selected_lab
        self.public_module_flag = public_module_flag
        self.proxy_url = os.environ.get("CVP_PROXY_URL", "http://atd-cvp-proxy:8880")
        self.deploy_lab()

    def check_cvp_ready(self):
        try:
            resp = requests.get(f"{self.proxy_url}/api/v1/health", timeout=5)
            health = resp.json()
            if health.get("cvp_status") == "READY":
                return True
            print(f"\nCloudVision is not yet operational (status: {health.get('cvp_status')})")
            print(health.get("message", "Please wait and try again."))
            return False
        except requests.ConnectionError:
            print("\nCVP proxy service is not reachable.")
            return False

    def update_topology(self, lab_configlets):
        device_assignments = lab_configlets[self.selected_lab]

        self.send_to_syslog("INFO", f"Applying lab configlets for {self.selected_lab}")
        print("Applying lab configuration...")

        resp = requests.post(
            f"{self.proxy_url}/api/v1/assignments/apply",
            json={
                "device_assignments": device_assignments,
                "global_configlets": ["ATD-INFRA"],
            },
            params={"stream": "true"},
            stream=True,
            timeout=600,
        )
        resp.raise_for_status()

        for line in resp.iter_lines():
            if line and line.startswith(b"data: "):
                try:
                    event = json.loads(line[6:])
                    phase = event.get("phase", "")
                    message = event.get("message", "")
                    print(f"[{phase}] {message}")
                    self.send_to_syslog("INFO", f"[{phase}] {message}")
                except json.JSONDecodeError:
                    pass

    def send_to_syslog(self, mstat, mtype):
        mmes = "\t" + mtype
        syslog.syslog("[{0}] {1}".format(mstat, mmes.expandtabs(7 - len(mstat))))
        if DEBUG:
            print("[{0}] {1}".format(mstat, mmes.expandtabs(7 - len(mstat))))

    def push_bare_config(self, veos_host, veos_ip, veos_config):
        device_config = "/tmp/" + veos_host + ".cfg"
        with open(device_config, "a") as tmp_config:
            tmp_config.write(veos_config)

        DEVREBOOT = False
        veos_ssh = paramiko.SSHClient()
        veos_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        veos_ssh.connect(hostname=veos_ip, username="root", password="", port="50001")
        scp = SCPClient(veos_ssh.get_transport())
        scp.put(device_config, remote_path="/mnt/flash/startup-config")
        scp.close()
        veos_ssh.exec_command('FastCli -c "{0}"'.format(cp_start_run))
        veos_ssh.exec_command('FastCli -c "{0}"'.format(cp_run_start))
        stdin, stdout, stderr = veos_ssh.exec_command('FastCli -c "{0}"'.format(ztp_cmds))
        ztp_out = stdout.readlines()
        if 'Active' in ztp_out[0]:
            DEVREBOOT = True
            self.send_to_syslog("INFO", "Rebooting {0}...This will take a couple minutes to come back up".format(veos_host))
            veos_ssh.exec_command('FastCli -c "{0}"'.format(ztp_cancel))
        veos_ssh.close()
        return DEVREBOOT

    def deploy_lab(self):
        lab_file = open('/home/arista/menus/{0}'.format(self.selected_menu + '.yaml'))
        lab_info = YAML().load(lab_file)
        lab_file.close()

        additional_commands = []
        if 'additional_commands' in lab_info['lab_list'][self.selected_lab]:
            additional_commands = lab_info['lab_list'][self.selected_lab]['additional_commands']

        f = open('/etc/atd/ACCESS_INFO.yaml')
        access_info = YAML().load(f)
        f.close()

        lab_configlets = lab_info['labconfiglets']

        self.send_to_syslog('INFO', 'Starting deployment for {0} - {1} lab...'.format(self.selected_menu, self.selected_lab))
        print("Starting deployment for {0} - {1} lab...".format(self.selected_menu, self.selected_lab))

        if 'cvp' in access_info['nodes']:
            if not self.check_cvp_ready():
                if not self.public_module_flag:
                    input("Press Enter to return to the menu...")
                return

            self.update_topology(lab_configlets)

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
        else:
            f = open('/home/arista/cvp/cvp_info.yaml')
            cvp_info = YAML().load(f)
            f.close()

            cvp_configs = cvp_info["cvp_info"]["configlets"]
            infra_configs = cvp_configs["containers"]["Tenant"]

            self.send_to_syslog("INFO", "Setting up {0} lab".format(self.selected_lab))
            for node in access_info["nodes"]["veos"]:
                device_config = ""
                hostname = node["hostname"]
                base_configs = cvp_configs["netelements"]
                configs = base_configs[hostname] + infra_configs + lab_configlets[self.selected_lab][hostname]
                configs = list(dict.fromkeys(configs))
                for config in configs:
                    with open('/opt/atd/topologies/{0}/configlets/{1}'.format(access_info['topology'], config), 'r') as configlet:
                        device_config += configlet.read()
                self.send_to_syslog("INFO", "Pushing {0} config for {1} on IP {2} with configlets: {3}".format(self.selected_lab, hostname, node["ip"], configs))
                self.push_bare_config(hostname, node["ip"], device_config)

            if len(additional_commands) > 0:
                print('Running additional setup commands...')
                for command in additional_commands:
                    os.system(command)

            if not self.public_module_flag:
                input('Lab Setup Completed. Please press Enter to continue...')
                self.send_to_syslog("OK", 'Lab Setup Completed.')
            else:
                self.send_to_syslog("OK", 'Lab Setup Completed.')
