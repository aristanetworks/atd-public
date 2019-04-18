#!/usr/bin/env python

"""
Version: 1.0
Author: @networkRob

"""

from ruamel.yaml import YAML
from os.path import exists
from time import sleep
import syslog

#SERVICE_FILE = '/tmp/atd/labvm/services/serviceUpdater.yml'
SERVICE_FILE = '../serviceUpdater.yml'
timer_sleep = 60


def pS(mstat,mtype):
    """
    Function to send output from service file to Syslog
    """
    mmes = "\t" + mtype
    #syslog.syslog("[{0}] {1}".format(mstat,mmes.expandtabs(7 - len(mstat))))
    print("[{0}] {1}".format(mstat,mmes.expandtabs(7 - len(mstat))))

def main():
    # Check for serviceUpdater.yml file
    timer_count = 0
    while not exists(SERVICE_FILE):
        timer_count += 1
        pS("INFO","{0} is not available, trying again in {1} seconds.".format(SERVICE_FILE.split('/')[::-1][0],timer_sleep))
        sleep(timer_sleep)
    pS("OK","{0} has been found".format(SERVICE_FILE.split('/')[::-1][0]
    ))

if __name__ == '__main__':
    # Open Syslog
    syslog.openlog(logoption=syslog.LOG_PID)
    pS("OK","Starting...")

    # Start the main Service
    main()

    pS("OK","Complete!")
    # Close Syslog
    syslog.closelog()