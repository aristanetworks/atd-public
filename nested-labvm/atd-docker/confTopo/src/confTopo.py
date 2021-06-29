#!/usr/bin/env python3

import tornado.ioloop
import tornado.web
import time
import yaml
from base64 import b64decode, b64encode
import json
from cvprac import cvp_client
from datetime import datetime
from os.path import exists
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ACCESS = '/etc/atd/ACCESS_INFO.yaml'
REPO_PATH = '/opt/atd/'
APP_PORT = 50010
SLEEP_DELAY = 30
CVP_NODES = ['192.168.0.5']
TOPO_USER = ''
TOPO_PWD = ''

# =================================================
# Handler Configuration
# =================================================    
class TopologyHandler(tornado.web.RequestHandler):
    def get(self):
        # Check for passed arguments
        if 'action' in self.request.arguments:
            _action = decodeID(self.get_argument('action'))
            pS(f"GET {_action}")
            # Check the status of CVP
            if _action == 'cvp_status':
                try:
                    cvp_clnt = cvp_client.CvpClient()
                    cvp_clnt.connect(CVP_NODES, TOPO_USER, TOPO_PWD)
                    result = cvp_clnt.api.get_cvp_info()
                    cvp_clnt.logout()
                    _cvp_status = result['version']
                except:
                    _cvp_status = False
                if _cvp_status:
                    self.write({
                        'status': 'UP',
                        'version': _cvp_status
                    })
                    pS(f"CVP VERSION = {_cvp_status}")
                else:
                    self.write({
                        'status': 'DOWN',
                        'version': ""
                    })
                    pS("CVP IS DOWN")
            # Get a list of Tasks in CVP
            elif _action == 'tasks':
                pS("GET CVP TASKS")
            # Get the status of Tasks from CVP
            elif _action == 'cvp_task_status':
                pS("GET CVP TASK STATUS")


# =================================================
# Utility Functions
# =================================================

def encodeID(tmp_data):
    tmp_str = json.dumps(tmp_data).encode()
    enc_str = b64encode(tmp_str).decode()
    return(enc_str)

def decodeID(tmp_data):
    decrypt_str = b64decode(tmp_data.encode()).decode()
    tmp_json = json.loads(decrypt_str)
    return(tmp_json)

def pS(mtype):
    """
    Function to send output from service file to Syslog
    """
    cur_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mmes = "\t" + mtype
    print("[{0}] {1}".format(cur_dt, mmes.expandtabs(7 - len(cur_dt))))

# =================================================
# SETUP of environment
# =================================================

def main():
    global TOPO_USER
    global TOPO_PWD
    while True:
        if exists(ACCESS):
            break
        else:
            pS(f"ERROR: ACCESS_INFO file is not available...Waiting for {SLEEP_DELAY} seconds")
            time.sleep(SLEEP_DELAY)
    try:
        f = open(ACCESS)
        accessinfo = yaml.safe_load(f)
        f.close()
        topology = accessinfo['topology']
    except:
        topology = 'none'
    TOPO_USER = accessinfo['login_info']['jump_host']['user']
    TOPO_PWD = accessinfo['login_info']['jump_host']['pw']



if __name__ == "__main__":
    main()
    app = tornado.web.Application([
        (r'/td-api/conftopo', TopologyHandler)
    ])
    app.listen(APP_PORT)
    pS('*** Server Started on {} ***'.format(APP_PORT))
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.instance().stop()
        pS("*** Server Stopped ***")