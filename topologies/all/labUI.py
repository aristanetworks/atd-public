#!/usr/bin/env python3

from ruamel.yaml import YAML
from bs4 import BeautifulSoup
from os import system
import tornado.ioloop
import tornado.web
import json
import requests
import traceback
import syslog

PORT = 50020
pDEBUG = True
BASE_PATH = '/home/arista/modules/'
ACCESS_PATH = '/etc/ACCESS_INFO.yaml'
MODULE_FILE = BASE_PATH + 'modules.yaml'
LABS_FILE = BASE_PATH + 'labs.yaml'
CONFIGURE_TOPOLOGY = "/usr/local/bin/ConfigureTopology.py"
APP_KEY = 'app'

MOD_YAML = YAML().load(open(MODULE_FILE, 'r'))

ACCESS_YAML = YAML().load(open(ACCESS_PATH, 'r'))

LABS_YAML = YAML().load(open(LABS_FILE, 'r'))

settings = {
    'static_path': BASE_PATH
}

class topoRequestHandler(tornado.web.RequestHandler):
    def get(self):
        if 'lab' in self.request.arguments:
            lab_module = self.get_argument("lab")
            if APP_KEY in ACCESS_YAML:
                # If the app key/value differs, re-configure lab
                if lab_module != ACCESS_YAML[APP_KEY]:
                    if lab_module in LABS_YAML['labs']:
                        lab_topo = LABS_YAML['labs'][lab_module]['topo']
                        pS("INFO", "Re-configuring lab from {0} to {1}".format(ACCESS_YAML[APP_KEY], lab_module))
                        system('nohub $(echo -e "\n" | {0} -t {1} -l {2}) &'.format(CONFIGURE_TOPOLOGY, lab_topo, lab_module))
                        pS("OK", "Done re-configuring the lab.")
                        ACCESS_YAML[APP_KEY] =  lab_module
                        with open(ACCESS_PATH, 'w') as mod_access:
                            YAML().dump(ACCESS_YAML, mod_access)
            if lab_module in MOD_YAML:
                labguide = getLabHTML(lab_module)
                if labguide:
                    labguide_js = modifyLabScripts(labguide.head.find_all("script",{"type":"text/javascript"}), 'js')
                    labguide_css = modifyLabScripts(labguide.head.find_all("link",{"type":"text/css"}), 'css')
                    # Set Vars for index render
                    self.render(
                        BASE_PATH + 'index.html',
                        JS = labguide_js,
                        CSS = labguide_css,
                        MOD_NAME = MOD_YAML[lab_module]['name'],
                        NODE_IP = getPublicIP(),
                        MOD_IMG = 'labguides/_images/{0}'.format(MOD_YAML[lab_module]['image']),
                        NODES = MOD_YAML[lab_module]['nodes'],
                        LABGUIDE = parseLabHTML(labguide, lab_module)
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

def getLabHTML(lab_tag):
    """
    Function to grab original labguide html data.
    """
    try:
        with open('/var/www/html/atd/labguides/{0}.html'.format(lab_tag), 'r') as tmp_html:
            html_parser = BeautifulSoup(tmp_html.read(), 'html.parser')
            return(html_parser)
    except:
        pass

def modifyLabScripts(html, tag_type):
    """
    Function to modify the header script urls.
    """
    if tag_type == 'js':
        tag_name = 'src'
    else:
        tag_name = 'href'
    for tag in html:
        if '_static' in tag[tag_name]:
            tag[tag_name] = 'labguides/{0}'.format(tag[tag_name])
    return(html)

def parseLabHTML(html, lab_tag):
    """
    Function to parse through html document and parse out/remove
    unnecessary data.
    """
    working_html = html.find_all("div", {"class":"container"})
    parsed = working_html[1]
    # Remove the main header
    parsed.select('h1')[0].extract()
    # Remove the lab diagram
    for html_img in parsed.find_all("img"):
        if lab_tag in html_img.get("alt"):
            html_img.extract()
    return(parsed)

def pS(mstat,mtype):
    """
    Function to send output from service file to Syslog
    Parameters:
    mstat = Message Status, ie "OK", "INFO" (required)
    mtype = Message to be sent/displayed (required)
    """
    mmes = "\t" + mtype
    syslog.syslog("[{0}] {1}".format(mstat,mmes.expandtabs(7 - len(mstat))))
    if pDEBUG:
        print("[{0}] {1}".format(mstat,mmes.expandtabs(7 - len(mstat))))
    

if __name__ == "__main__":
    # Open Syslog
    syslog.openlog(logoption=syslog.LOG_PID)
    app = tornado.web.Application([
        (r'/module', topoRequestHandler),
        (r'/module/(.*)', tornado.web.StaticFileHandler, {'path': BASE_PATH })
    ],)
    app.listen(PORT)
    pS("OK", '*** Websocket Server Started on {} ***'.format(PORT))
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.instance().stop()
        pS("INFO", "*** Websocked Server Stopped ***")
