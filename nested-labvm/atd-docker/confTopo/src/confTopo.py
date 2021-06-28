#!/usr/bin/env python3

import tornado.ioloop
import tornado.web
import time
from datetime import datetime, timedelta
from os.path import exists

APP_PORT = 50010

class ConfigureHandler(tornado.web.RequestHandler):
    def get(self):
        # Check for passed arguments
        if 'status' in self.request.arguments:
            pS("GET STATUS")



def pS(mtype):
    """
    Function to send output from service file to Syslog
    """
    cur_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mmes = "\t" + mtype
    print("[{0}] {1}".format(cur_dt, mmes.expandtabs(7 - len(cur_dt))))


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