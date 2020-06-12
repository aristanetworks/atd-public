#!/usr/bin/env python3

import tornado.ioloop
import tornado.web
from datetime import datetime

PORT = 80
BASE_PATH = '/root/labguides/web/'


class labguideRequestHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            BASE_PATH + 'index.html'
        )
    
# ===============================
# Utility Functions
# ===============================


def pS(mtype):
    """
    Function to send output from service file to Syslog
    """
    cur_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mmes = "\t" + mtype
    print("[{0}] {1}".format(cur_dt, mmes.expandtabs(7 - len(cur_dt))))


if __name__ == "__main__":
    app = tornado.web.Application([
        (r'/labguides', labguideRequestHandler),
        (r'/labguides/(.*)', tornado.web.StaticFileHandler, {'path': BASE_PATH})
    ])
    app.listen(PORT)
    print('*** Websocket Server Started on {} ***'.format(PORT))
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.instance().stop()
        print("*** Websocked Server Stopped ***")
