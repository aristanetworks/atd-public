#!/usr/bin/env python3

import ruamel.yaml import YAML
import tornado.ioloop
import tornado.web
import json
import requests
import traceback

PORT = 50020
NODE_IP = getPublicIP()
MODULE_FILE = 'modules.yaml'

MOD_YAML = YAML().load(open(MODULE_FILE, 'r'))



class topoRequestHandler(tornado.web.RequestHandler):
    def get(self):
        if 'lab' in self.request.arguments:
            if self.get_argument("lab") in MOD_YAML:
                # Set Vars for index render
                self.render(
                    'index.html'
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


if __name__ == "__main__":
    app = tornado.web.Application([
        (r'/module', topoRequestHandler),
    ])
    app.listen(PORT)
    print('*** Websocket Server Started on {} ***'.format(PORT))
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.instance().stop()
        print("*** Websocked Server Stopped ***")
