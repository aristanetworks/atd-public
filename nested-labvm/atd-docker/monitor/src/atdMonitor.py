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
COUNTER_THRESHOLD = 10
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
            _file = tmp_file.readlines()
            if flast:
                return(_file[-1])
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
    _ENABLE_MONITOR = True
    _tmp_counter = 0
    pS("Performing log query every {0} minutes".format(int(QUERY_TIMEOUT / 60)))
    pS("Inactivity threshold is set for {0} minutes.".format(int(INACTIVITY_THRESHOLD / 60)))
    # Open ACCESS_INFO file
    pS("Accessing ACCESS_INFO Information")
    while _tmp_counter < COUNTER_THRESHOLD:
        access_yaml = openYAML(ATD_ACCESS_PATH)
        if 'project' and 'zone' and 'name' in access_yaml:
            pS("Necessary parameters exist, continuing")
            break
        else:
            _tmp_counter += 1
            pS("Attempt [{0}/{1}] Parameters do not exist in ACCESS_INFO, waiting for {2} seconds".format(_tmp_counter, COUNTER_THRESHOLD, SLEEP_DELAY))
            sleep(SLEEP_DELAY)
    else:
        return(False)
    # Set Variables
    _boot_time = ''
    pS("Setting instance variables")

    project = access_yaml['project']
    name = access_yaml['name']
    zone = access_yaml['zone']
    function_state_url = FUNC_STATE.format(project)
    _func_stop = function_state_url + "?function=stop&instance={0}&zone={1}".format(name, zone)
    pS("Done setting instance variables")
    # Start loop for checking instance status
    while True:
        _stale_ssh = False
        _stale_nginx = False
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
                            if (_tmp_now - _tmp_datetime).seconds < (_tmp_now - _recent_session).seconds:
                                _recent_session = _tmp_datetime
                        else:
                            _recent_session = _tmp_datetime
                    if _recent_session:
                        LAST_LOGS['ssh']['timestamp'] = _recent_session
                    else:
                        LAST_LOGS['ssh']['timestamp'] = _boot_time
            else:
                LAST_LOGS['ssh']['timestamp'] = _boot_time
                pS("No sessions have been created since boot, using boot time")
        else:
            LAST_LOGS['ssh']['timestamp'] = _boot_time
            pS("No sessions logs found, using boot time.")
        # Get nginx Logs
        pS("Getting nginx Logs")
        _nginx_logs = openFile(NGINX_LOG_PATH, True)
        if _nginx_logs:
            pS("Received last nginx log")
            if _nginx_logs != LAST_LOGS['nginx']['log']:
                LAST_LOGS['nginx']['log'] = _nginx_logs
                LAST_LOGS['nginx']['timestamp'] = datetime.now(tz=timezone.utc)
                try:
                    _log_time = _nginx_logs.split('[')[1].split(']')[0]
                    _nginx_log_time = datetime.strptime(_log_time, "%d/%b/%Y:%H:%M:%S %z")
                    if _boot_time:
                        pS("Checking Boot time")
                        if _boot_time >= _nginx_log_time:
                            pS("No NGINX activity since boot")
                            LAST_LOGS['nginx']['log_time'] = _boot_time
                        else:
                            pS("NGINX activity since boot")
                            LAST_LOGS['nginx']['log_time'] = _nginx_log_time
                except:
                    pS("ERROR Parsing nginx log time")
                    pS(_log_time)
                    if _boot_time:
                        LAST_LOGS['nginx']['log_time'] = _boot_time
                    else:
                        LAST_LOGS['nginx']['log_time'] = LAST_LOGS['nginx']['timestamp']
            else:
                pS("No Change in NGINX Logs")
        else:
            LAST_LOGS['nginx']['log_time'] = _boot_time
            pS("NGINX Logs are empty, using boot time.")
        if LAST_LOGS['nginx']['log'] and LAST_LOGS['ssh']['timestamp']:
            _stale_sessions = False
            # Perform Checks on NGINX
            _nginx_timedelta = datetime.now(tz=timezone.utc) - LAST_LOGS['nginx']['log_time']
            if _nginx_timedelta.seconds <= INACTIVITY_THRESHOLD:
                pS("Last NGINX activity on the instance {0} minutes ago".format(int(_nginx_timedelta.seconds/60)))
            else:
                _stale_nginx = True
                pS("Stale activity on NGINX, last session {0} minutes ago. {1} minutes over inactivity threshold!".format(
                    int(_nginx_timedelta.seconds / 60),
                    int((_nginx_timedelta.seconds/60) - (INACTIVITY_THRESHOLD / 60))
                ))
            # Perform Checks on ssh sessions
            _ssh_timedelta = datetime.now(tz=timezone.utc) - LAST_LOGS['ssh']['timestamp']
            if _ssh_timedelta.seconds <= INACTIVITY_THRESHOLD:
                pS("Last SSH activity on the instance {0} minutes ago".format(int(_ssh_timedelta.seconds/60)))
            else:
                _stale_ssh = True
                pS("Stale activity on SSH, last session {0} minutes ago. {1} minutes over inactivity threshold!".format(
                    int(_ssh_timedelta.seconds / 60),
                    int((_ssh_timedelta.seconds / 60) - (INACTIVITY_THRESHOLD / 60))
                ))
        if _stale_nginx and _stale_ssh:
            pS("Last session is over threshold of {0} minutes".format(int(INACTIVITY_THRESHOLD / 60)))
            pS("STALE SESSIONS SHUTTING DOWN!!!!")
            response = requests.post(_func_stop)
            break
        else:
            sleep(QUERY_TIMEOUT)

if __name__ == '__main__':
    pS("Starting instance monitoring...")
    atdmonitor = main()
    if atdmonitor:
        pS("Instance is shutting down")
    else:
        pS("Old topology setup, exiting...")
        while True:
            sleep(600)
