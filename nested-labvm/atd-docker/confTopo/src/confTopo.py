#!/usr/bin/env python3

import tornado.ioloop
import tornado.web
import time
import yaml
from datetime import datetime, timedelta
from os.path import exists
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ACCESS = '/etc/atd/ACCESS_INFO.yaml'
gitTempPath = '/opt/atd/'
APP_PORT = 50010
sleep_delay = 30

# =================================================
# Handler Configuration
# =================================================    
class ConfigureHandler(tornado.web.RequestHandler):
    def get(self):
        # Check for passed arguments
        if 'status' in self.request.arguments:
            pS("GET STATUS")


# =================================================
# Utility Functions
# =================================================

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

while True:
    if exists(ACCESS):
        break
    else:
        pS("ERROR", "ACCESS_INFO file is not available...Waiting for {0} seconds".format(sleep_delay))
        time.sleep(sleep_delay)
try:
    f = open(ACCESS)
    accessinfo = yaml.safe_load(f)
    f.close()
    topology = accessinfo['topology']
except:
    topology = 'none'


if __name__ == "__main__":
    app = tornado.web.Application([
        (r'/api/conftopo', ConfigureHandler)
    ])
    app.listen(APP_PORT)

    pS('*** Server Started on {} ***'.format(APP_PORT))
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.instance().stop()
        pS("*** Server Stopped ***")