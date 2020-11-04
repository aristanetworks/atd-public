#!/usr/bin/env python3

from ruamel.yaml import YAML
from time import sleep
from datetime import datetime, timezone
from subprocess import Popen, PIPE
import requests


# =====================================
# Global Variables
# =====================================

SLEEP_DELAY = 10
QUERY_TIMEOUT= 10 * 60
INACTIVITY_THRESHOLD = 3 * 60 * 60
ATD_ACCESS_PATH = '/etc/atd/ACCESS_INFO.yaml'
NGINX_LOG_PATH = '/var/log/nginx/atd-access.log'
FUNC_STATE = 'https://us-central1-{0}.cloudfunctions.net/atd-state'
LAST_LOGS = {
    'nginx': {
        'log': '',
        'log_time': '',
        'timestamp': ''
    },
    'ssh': {
        'timestamp': ''
    }
}


# =====================================
# Utility Functions
# =====================================
def pS(mtype):
    """
    Function to send output from service file to Syslog
    """
    cur_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mmes = "\t" + mtype
    print("[{0}] {1}".format(cur_dt, mmes.expandtabs(7 - len(cur_dt))))

def openYAML(fpath):
    """
    Function to open and read yaml file contents.
    """
    try:
        host_yaml = YAML().load(open(fpath, 'r'))
        return(host_yaml)
    except:
        return("File not available")

def openFile(fpath, flast=False):
    """
    Function to open and read the contents of a file.
    """
    try:
        with open(fpath, 'r') as tmp_file:
            _file = tmp_file.read()
            if flast:
                _file = _file.split('\n')
                return(_file[len(_file) - 2])
            else:
                return(_file)
    except:
        return(False)

def runCmd(cmd):
    """
    Function to run a shell command and return the output.
    """
    if type(cmd) == str:
        cmd = [cmd]
    _cmd = Popen(cmd, stdout=PIPE, stderr=PIPE)
    try:
        _cmd_result = _cmd.communicate()
        _cmd_out = _cmd_result[0].decode().split('\n')
        return(_cmd_out)
    except:
        return(False)

def main():
    # Open ACCESS_INFO file
    pS("Accessing ACCESS_INFO Information")
    while True:
        access_yaml = openYAML(ATD_ACCESS_PATH)
        if 'project' and 'zone' and 'name' in access_yaml:
            pS("Necessary parameters exist, continuing")
            break
        else:
            pS("Parameters do not exists in ACCESS_INFO, waiting for {0} seconds".format(SLEEP_DELAY))
            sleep(SLEEP_DELAY)
    # Set Variables
    pS("Setting instance variables")
    project = access_yaml['project']
    name = access_yaml['name']
    zone = access_yaml['zone']
    function_state_url = FUNC_STATE.format(project)
    _func_stop = function_state_url + "?function=stop&instance={0}&zone={1}".format(name, zone)
    _full_stop_cmd = "curl -X POST '{0}' -H 'Content-Type:application/json' --data '{{}}'".format(_func_stop)
    pS("Done setting instance variables")

    # Start loop for checking instance status
    while True:
        _stale_ssh = False
        _stale_nginx = False
        # Get nginx Logs
        pS("Getting nginx Logs")
        _nginx_logs = openFile(NGINX_LOG_PATH, True)
        if _nginx_logs:
            pS("Received last nginx log")
            if _nginx_logs != LAST_LOGS['nginx']['log']:
                pS("New NGINX Log Update")
                LAST_LOGS['nginx']['log'] = _nginx_logs
                LAST_LOGS['nginx']['timestamp'] = datetime.now(tz=timezone.utc)
                try:
                    _log_time = _nginx_logs.split('[')[1].split(']')[0]
                    LAST_LOGS['nginx']['log_time'] = datetime.strptime(_log_time, "%d/%b/%Y:%H:%M:%S %z")
                except:
                    LAST_LOGS['nginx']['log_time'] = LAST_LOGS['nginx']['timestamp']
            else:
                pS("No Change in NGINX Logs")
        else:
            pS("Error accessing NGINX Logs")
        # Get session history
        _session_logs = runCmd(["last","-FR"])
        if _session_logs:
            pS("Received session logs")
            _current_session = []
            # Grab any session since last boot
            for _session in _session_logs:
                if 'reboot' in _session:
                    _tmp_boot = _session.split()
                    _tmp_boottime = "{}-{}-{}:{} +0000".format(_tmp_boot[7], _tmp_boot[4], _tmp_boot[5],_tmp_boot[6])
                    _boot_time = datetime.strptime(_tmp_boottime, "%Y-%b-%d:%H:%M:%S %z")
                    break
                else:
                    _current_session.append(_session)
            # Check if there have been any sessions since boot
            if _current_session:
                pS("Sessions has been created since boot")
                if 'no logout' in str(_current_session) or 'still logged in' in str(_current_session):
                    LAST_LOGS['ssh']['timestamp'] = datetime.now(tz=timezone.utc)
                else:
                    _recent_session = ''
                    _tmp_now = datetime.now(tz=timezone.utc)
                    for _session in _current_session:
                        _tmp_session = _session.split('-')[1].split()
                        _tmp_time = "{}-{}-{}:{} +0000".format(_tmp_session[4], _tmp_session[1], _tmp_session[2],_tmp_session[3])
                        _tmp_datetime = datetime.strptime(_tmp_time, "%Y-%b-%d:%H:%M:%S %z")
                        if _recent_session:
                            if (_tmp_now - _tmp_datetime).seconds > (_tmp_now - _recent_session).seconds:
                                _recent_session = _tmp_datetime
                    if _recent_session:
                        LAST_LOGS['ssh']['timestamp'] = _recent_session
                    else:
                        LAST_LOGS['ssh']['timestamp'] = _boot_time
            else:
                pS("No sessions have been created since boot")
        if LAST_LOGS['nginx']['log'] and LAST_LOGS['ssh']['timestamp']:
            _stale_sessions = False
            # Perform Checks on NGINX
            _nginx_timedelta = datetime.now(tz=timezone.utc) - LAST_LOGS['nginx']['log_time']
            if _nginx_timedelta.seconds <= INACTIVITY_THRESHOLD:
                pS("NGINX activity on the instance within the last {0} minutes".format(int(_nginx_timedelta.seconds/60)))
            else:
                _stale_nginx = True
                pS("Stale activity on NGINX sessions since {0} minutes".format(int(_nginx_timedelta.seconds/60)))
            # Perform Checks on ssh sessions
            _ssh_timedelta = datetime.now(tz=timezone.utc) - LAST_LOGS['ssh']['timestamp']
            if _ssh_timedelta.seconds <= INACTIVITY_THRESHOLD:
                pS("SSH activity on the instance within the last {0} minutes".format(int(_ssh_timedelta.seconds/60)))
            else:
                _stale_ssh = True
                pS("Stale activity on SSH sessions since {0} minutes".format(int(_ssh_timedelta.seconds/60)))
        if _stale_nginx and _stale_ssh:
            pS("STALE SESSIONS SHUTTING DOWN!!!!")
            break
        else:
            sleep(QUERY_TIMEOUT)


if __name__ == '__main__':
    main()