#!/usr/bin/env python3

import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado import gen, concurrent
# import threading
import time
import yaml
from base64 import b64decode, b64encode
import json
from cvprac import cvp_client
from datetime import datetime
from os.path import exists
from ConfigureTopology.ConfigureTopology import ConfigureTopology
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
executor = concurrent.futures.ThreadPoolExecutor(8)

ACCESS = '/etc/atd/ACCESS_INFO.yaml'
REPO_PATH = '/opt/atd/'
APP_PORT = 50010
SLEEP_DELAY = 30
CVP_NODES = []
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
                        'status': 'Starting',
                        'version': ""
                    })
                    pS("CVP IS DOWN")
            # Get a list of Tasks in CVP
            elif _action == 'cvp_tasks':
                _cvp_tasks = {}
                _active_tasks = 0
                try:
                    cvp_clnt = cvp_client.CvpClient()
                    cvp_clnt.connect(CVP_NODES, TOPO_USER, TOPO_PWD)
                    result = cvp_clnt.api.get_tasks_by_status("active")
                    cvp_clnt.logout()
                    _total_tasks = len(result)
                    if _total_tasks > 0:
                        for _task in result:
                            if 'cancelled' not in _task['workOrderUserDefinedStatus'].lower():
                                _active_tasks += 1
                                if _task['workOrderUserDefinedStatus'] in _cvp_tasks:
                                    _cvp_tasks[_task['workOrderUserDefinedStatus']] += 1
                                else:
                                    _cvp_tasks[_task['workOrderUserDefinedStatus']] = 1
                    if _active_tasks:
                        self.write({
                            'status': "Active",
                            'total': _active_tasks,
                            'tasks': _cvp_tasks
                        })
                    else:
                        self.write({
                            'status': 'Complete',
                            'total': 0,
                            'tasks': _cvp_tasks
                        })
                except Exception as e:
                    print(str(e))
                    self.write({
                        'status': 'Error getting tasks',
                        'total': 0,
                        'tasks': _cvp_tasks
                    })
            elif _action == 'update_lab':
                if 'module' in self.request.arguments and 'lab' in self.request.arguments:
                    with open(ACCESS,'r') as acfile:
                        accessinfo = yaml.safe_load(acfile)
                    _module = decodeID(self.get_argument('module'))
                    _lab = decodeID(self.get_argument('lab'))
                    pS(f"Update {_lab} lab for {_module}")
                    cvp = ConfigureTopology(accessinfo, CVP_NODES, TOPO_USER, TOPO_PWD)
                    cvp.lab = _lab
                    if _module in cvp.lab_list:
                        cvp.update_lab(_module, grouped=False)

class topoDataHandler(tornado.websocket.WebSocketHandler):
    # executor = ThreadPoolExecutor(max_workers=4)

    def open(self):
        with open(ACCESS,'r') as acfile:
            self.accessinfo = yaml.safe_load(acfile)
        pS("New backend websocket connection")
    
    def on_message(self,message):
        pS("Message Received")
        try:
            recv = json.loads(message)
            cdata = recv['data']
            if recv['type'] == 'hello':
                pS("Hello")
            elif recv['type'] == 'update_lab':
                pS("Lab Update")
                if 'module' in cdata and 'lab' in cdata:
                    _module = cdata['module']
                    _lab = cdata['lab']
                    pS(f"Update {_lab} lab for {_module}")
                    cvp = ConfigureTopology(self.accessinfo, CVP_NODES, TOPO_USER, TOPO_PWD)
                    cvp.lab = _lab
                    if _module in cvp.lab_list:
                        self.write_message(json.dumps({
                            'type': 'lab_status',
                            'data': {
                                'status': "starting"
                            }
                        }))
                        # tornado.ioloop.IOLoop.current().spawn_callback(self.update_lab, cvp, _module, False)
                        # _cvp_lab_update = yield update_lab(cvp, _module, False)
                        # cvp.update_lab(_module, grouped=False)
                        # update_lab(cvp, _module, False)
                        executor.submit(cvp.update_lab, _module, grouped=False)
                        _previous_status = ''
                        pS("Starting CVP Status Check Loop")
                        while cvp.status != "Lab Update complete":
                            if _previous_status != cvp.status:
                                _previous_status = cvp.status
                                self.write_message(json.dumps({
                                    'type': 'lab_status',
                                    'data': {
                                        'status': cvp.status
                                    }
                                }))
                        self.write_message(json.dumps({
                            'type': 'lab_status',
                            'data': {
                                'status': "complete"
                            }
                        }))
        except Exception as e:
            pS("WS ERROR")
            pS(str(e))


    def schedule_update(self):
        try:
            self.timeout = tornado.ioloop.IOLoop.instance().add_timeout(timedelta(seconds=30),self.keepalive)
        except:
            pS("Error with timeout call")
        
    def keepalive(self):
        try:
            self.uptime = getUptime('192.168.0.1')
            self.cvp_status = getAPI("cvp_status")
            if self.cvp_status['status'] == 'UP':
                self.cvp_tasks = getAPI("cvp_tasks")
            else:
                self.cvp_tasks = ''
            self.sendData('status')
        except:
            pS("ERROR sending update")
        finally:
            self.schedule_update()

    def on_close(self):
        try:
            tornado.ioloop.IOLoop.instance().remove_timeout(self.timeout)
            pS('connection closed')
        except:
            pS('connection already closed')
 
    def check_origin(self, origin):
        return(True)
    
    def sendData(self, mtype):
        instance_data = {
            'cvp': self.cvp_status,
            'tasks': self.cvp_tasks,
            'uptime': self.uptime
        }
        self.write_message(json.dumps({
            'type': mtype,
            'data': instance_data
        }))

# =================================================
# Utility Functions
# =================================================
# def update_lab(cvp, _module, _grouped):
#     t = threading.Thread(target=cvp.update_lab, args=(_module,), kwargs={"grouped":_grouped})
#     t.start()
#     # cvp.update_lab(_module, grouped=_grouped)
#     return(True)

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
    global CVP_NODES
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
    if accessinfo['cvp']:
        for _node in accessinfo['nodes']['cvp']:
            CVP_NODES.append(_node['ip'])
    TOPO_USER = accessinfo['login_info']['jump_host']['user']
    TOPO_PWD = accessinfo['login_info']['jump_host']['pw']



if __name__ == "__main__":
    main()
    app = tornado.web.Application([
        (r'/td-api/conftopo', TopologyHandler),
        (r'/td-api/ws-conftopo', topoDataHandler)
    ])
    app.listen(APP_PORT)
    pS('*** Server Started on {} ***'.format(APP_PORT))
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.instance().stop()
        pS("*** Server Stopped ***")