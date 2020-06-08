#!/usr/bin/env python3

import tornado.ioloop
import tornado.web
import psutil
import time
from datetime import datetime, timedelta
from os.path import exists

APP_PORT = 50010

class UptimeHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({
            'uptime': uptimeSeconds(),
            'status': checkProvisioned('/etc/atd/.provisioned')
        })


def uptimeSeconds():
    return(round(time.time() - psutil.boot_time()))

def checkProvisioned(full_file_path):
    if exists(full_file_path):
        return('post')
    else:
        return('init')

def pS(mtype):
    """
    Function to send output from service file to Syslog
    """
    cur_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mmes = "\t" + mtype
    print("[{0}] {1}".format(cur_dt, mmes.expandtabs(7 - len(cur_dt))))


if __name__ == "__main__":
    app = tornado.web.Application([
        (r'/', UptimeHandler)
    ])
    app.listen(APP_PORT)
    pS('*** Server Started on {} ***'.format(APP_PORT))
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.instance().stop()
        pS("*** Server Stopped ***")