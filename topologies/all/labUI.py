#!/usr/bin/env python3

from ruamel.yaml import YAML
from bs4 import BeautifulSoup
import tornado.ioloop
import tornado.web
import json
import requests
import traceback

PORT = 50020
BASE_PATH = '/home/arista/modules/'
MODULE_FILE = BASE_PATH + 'modules.yaml'

MOD_YAML = YAML().load(open(MODULE_FILE, 'r'))

settings = {
    'static_path': BASE_PATH
}

class topoRequestHandler(tornado.web.RequestHandler):
    def get(self):
        if 'lab' in self.request.arguments:
            lab_module = self.get_argument("lab")
            if 'ucn-' in lab_module or 'cvp-' in lab_module:
                lab, mod = lab_module.split('-')
                if lab in MOD_YAML:
                    if mod in MOD_YAML[lab]:
                        labguide = getLabHTML(lab_module)
                        if labguide:
                            labguide_js = modifyLabScripts(labguide.head.find_all("script",{"type":"text/javascript"}), 'js')
                            labguide_css = modifyLabScripts(labguide.head.find_all("link",{"type":"text/css"}), 'css')
                            # Set Vars for index render
                            self.render(
                                BASE_PATH + 'index.html',
                                JS = labguide_js,
                                CSS = labguide_css,
                                MOD_NAME = MOD_YAML[lab][mod]['name'],
                                NODE_IP = getPublicIP(),
                                MOD_IMG = 'labguides/_images/modules/{0}'.format(MOD_YAML[lab][mod]['image']),
                                NODES = MOD_YAML[lab][mod]['nodes'],
                                LABGUIDE = parseLabHTML(labguide, lab, mod)
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

def parseLabHTML(html, lab_tag, mod_tag):
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
        # Update the image path:
        html_img['src'] = html_img['src'].replace('_images', 'labguides/_images')
    for html_a in parsed.find_all("a"):
        if '_images' in html_a['href']:
            html_a['href'] = html_a['href'].replace('_images', 'labguides/_images')
    return(parsed)
    

if __name__ == "__main__":
    app = tornado.web.Application([
        (r'/module', topoRequestHandler),
        (r'/module/(.*)', tornado.web.StaticFileHandler, {'path': BASE_PATH })
    ],)
    app.listen(PORT)
    print('*** Websocket Server Started on {} ***'.format(PORT))
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.instance().stop()
        print("*** Websocked Server Stopped ***")
