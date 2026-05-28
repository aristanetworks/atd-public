#!/usr/bin/env python

import os
import syslog
import urllib3

from cvprac.cvp_client import CvpClient
import paramiko
from ruamel.yaml import YAML
from scp import SCPClient

from .cv_studio import CVStudiosClient

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
        self.deploy_lab()

    def send_to_syslog(self, mstat, mtype):
        mmes = "\t" + mtype
        syslog.syslog("[{0}] {1}".format(mstat, mmes.expandtabs(7 - len(mstat))))
        if DEBUG:
            print("[{0}] {1}".format(mstat, mmes.expandtabs(7 - len(mstat))))

    def _hostname_to_device_id(self, host, user, pw):
        """Resolve hostname -> CVP device identifier (serial, fallback systemMacAddress)
        used by Static Configuration Studio 'device:<id>' queries.
        """
        clnt = CvpClient()
        clnt.api.request_timeout = 180
        clnt.connect([host], user, pw)
        mapping = {}
        for dev in clnt.api.get_inventory():
            dev_id = dev.get('serialNumber') or dev.get('systemMacAddress')
            if dev_id:
                mapping[dev['hostname']] = dev_id
        return mapping

    def push_bare_config(self, veos_host, veos_ip, veos_config):
        """Pushes a bare config to the EOS device (no-CVP path)."""
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
        with open('/home/arista/menus/{0}'.format(self.selected_menu + '.yaml')) as lab_file:
            lab_info = YAML().load(lab_file)

        additional_commands = lab_info['lab_list'][self.selected_lab].get('additional_commands', [])

        with open('/etc/atd/ACCESS_INFO.yaml') as f:
            access_info = YAML().load(f)

        lab_configlets = lab_info['labconfiglets']

        self.send_to_syslog('INFO', 'Starting deployment for {0} - {1} lab...'.format(self.selected_menu, self.selected_lab))
        print("Starting deployment for {0} - {1} lab...".format(self.selected_menu, self.selected_lab))

        if 'cvp' in access_info['nodes']:
            cvp_host = access_info['nodes']['cvp'][0]['ip']
            cvp_user = access_info['login_info']['jump_host']['user']
            cvp_pw = access_info['login_info']['jump_host']['pw']

            hostname_to_dev = self._hostname_to_device_id(cvp_host, cvp_user, cvp_pw)

            dry_run = os.environ.get('ATD_CV_DRY_RUN', '').lower() in ('1', 'true', 'yes')
            cv = CVStudiosClient(host=cvp_host, username=cvp_user, password=cvp_pw, dry_run=dry_run)
            try:
                cv.connect()
                self.send_to_syslog("OK", "Connected to CVP at {0}".format(cvp_host))
                cv.apply_lab(
                    per_device_configlets=lab_configlets[self.selected_lab],
                    hostname_to_device_id=hostname_to_dev,
                    label="{0}/{1}".format(self.selected_menu, self.selected_lab),
                )
                self.send_to_syslog("OK", 'Completed setting devices to topology: {}'.format(self.selected_lab))

                if additional_commands:
                    print('Running additional setup commands...')
                    self.send_to_syslog('INFO', 'Running additional setup commands.')
                    for command in additional_commands:
                        os.system(command)

                if not self.public_module_flag:
                    input('Lab Setup Completed. Please press Enter to continue...')
                self.send_to_syslog("OK", 'Lab Setup Completed.')
            finally:
                cv.close()
        else:
            with open('/home/arista/cvp/cvp_info.yaml') as f:
                cvp_info = YAML().load(f)

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
                    with open('/opt/atd/topologies/{0}/configlets/{1}'.format(access_info['topology'], config), 'r') as configlet_f:
                        device_config += configlet_f.read()
                self.send_to_syslog("INFO", "Pushing {0} config for {1} on IP {2} with configlets: {3}".format(self.selected_lab, hostname, node["ip"], configs))
                self.push_bare_config(hostname, node["ip"], device_config)

                if additional_commands:
                    print('Running additional setup commands...')
                    for command in additional_commands:
                        os.system(command)
            if not self.public_module_flag:
                input('Lab Setup Completed. Please press Enter to continue...')
            self.send_to_syslog("OK", 'Lab Setup Completed.')
