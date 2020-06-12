#!/usr/bin/env python3

import tornado.ioloop
import tornado.web
import requests
from datetime import datetime
from ruamel.yaml import YAML

PORT = 80
BASE_PATH = '/opt/topo/html/'
ATD_ACCESS_PATH = '/etc/atd/ACCESS_INFO.yaml'

class topoRequestHandler(tornado.web.RequestHandler):
    def get(self):
        access_yaml = loadYAML()
        node_ip = getPublicIP()
        self.render(
            BASE_PATH + 'index.html',
            ARISTA_PWD=access_yaml['login_info']['jump_host']['pw'],
            PUBLIC_IP=node_ip
        )
    
# ===============================
# Utility Functions
# ===============================

def getPublicIP():
    """
    Function to get Public IP.
    """
    response = requests.get('http://ipecho.net/plain')
    return(response.text)

def loadYAML():
    host_yaml = YAML().load(open(ATD_ACCESS_PATH, 'r'))
    return(host_yaml)

def pS(mtype):
    """
    Function to send output from service file to Syslog
    """
    cur_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mmes = "\t" + mtype
    print("[{0}] {1}".format(cur_dt, mmes.expandtabs(7 - len(cur_dt))))


if __name__ == "__main__":
    app = tornado.web.Application([
        (r'/js/(.*)', tornado.web.StaticFileHandler, {'path': BASE_PATH +  "js/"}),
        (r'/css/(.*)', tornado.web.StaticFileHandler, {'path': BASE_PATH +  "css/"}),
        (r'/labguides/(.*)', tornado.web.StaticFileHandler, {'path': BASE_PATH +  "labguides/"}),
        (r'/images/(.*)', tornado.web.StaticFileHandler, {'path': BASE_PATH +  "images/"}),
        (r'/', topoRequestHandler)
    ])
    app.listen(PORT)
    print('*** Websocket Server Started on {} ***'.format(PORT))
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.instance().stop()
        print("*** Websocked Server Stopped ***")
