#!/usr/bin/env python

"""
Version: 2.0
Author: @networkRob

Notes/Improvements:
1. Look into consolidating [enable/stop/start/enable]Service() functions and daemonReload() function to where
   they call a single function that makes the Popen() call
2. Need to be able to check incoming new service if there are any PIP dependencies that need to be installed
   ^^^^
   Maybe a seperate service module to check for PIP files to install

"""

import git
import argparse
import hashlib
import syslog
from ruamel.yaml import YAML
from os import listdir, stat, chmod
from os.path import isdir, exists
from shutil import rmtree, copy2
from subprocess import Popen

# Lists for service all service files found and which ones need to be updated
all_services = [] # Holds Service Class objects
up_service_files = [] # Holds service file names to be restarted/started

# Declare the name for the updater file to be used in checking later for reload sequence
UPDATER_NAME = 'atdServiceUpdater'

# Temp path for where repo will be cloned to (include trailing /)
GIT_TEMP_PATH = '/tmp/atd/'
GIT_BRANCH_PATH= '/etc/repo.yaml' # Persistent location to check for branch to test reboot
GIT_PATH = "https://github.com/aristanetworks/atd-public.git"
GIT_BRANCH = "master"

# Declaration for working directories
LOCAL_GIT = "{0}labvm/services".format(GIT_TEMP_PATH)
YAML_PATH = "{0}/serviceUpdater.yml".format(LOCAL_GIT)

SERVICE_PATH = '/lib/systemd/system/'
S_FILE_PATH = '/usr/local/bin/'

class SERVICES():
    global up_service_files

    def __init__(self,ser_name):
        self.name = ser_name # Service Name
        self.tmp_path = LOCAL_GIT + "/" + ser_name # Temp path location
        if isdir(self.tmp_path):
            self.ser_files = listdir(self.tmp_path) # List of service files
            self.ser_hashes = {'tmp':self.getServiceFiles(),'run':{}} # Hashes for all files
            # Check if service files exist locally already
            self._checkExisting()
            # Evaluate if files are already present
            if not self.ser_hashes['run']:
                for new_file in self.ser_files:
                    self._copyFile(new_file,"ADDED")
            else:
                # If service files already existed, compare existing to remote repos
                self.compareFileHashes()
        else:
            pS("iBerg","GitHub directory does not exist for: {0}".format(self.name))
    
    def _checkExisting(self):
        """
        Check to see if service files currently exist
        """
        for file_service in self.ser_files:
            if file_service in listdir(SERVICE_PATH):
                self.ser_hashes['run'][file_service] = self.getFileHash(SERVICE_PATH +  file_service)
            elif file_service in listdir(S_FILE_PATH):
                self.ser_hashes['run'][file_service] = self.getFileHash(S_FILE_PATH +  file_service)

    def compareFileHashes(self):
        """
        Compares the file hashes from the local to GitHub copy
        """
        for file_service in self.ser_files:
            if file_service in listdir(SERVICE_PATH):
                if self.ser_hashes['run'][file_service] != self.ser_hashes['tmp'][file_service]:
                    self._copyFile(file_service,"UPDATED")
                else:
                    pS("OK","Has not changed {0}".format(file_service))
            elif file_service in listdir(S_FILE_PATH):
                if self.ser_hashes['run'][file_service] != self.ser_hashes['tmp'][file_service]:
                    self._copyFile(file_service,"UPDATED")
                else:
                    pS("OK","Has not changed {0}".format(file_service))
            # If file currenlty does not exist copy over to local machine
            else:
                self._copyFile(file_service,"ADDED")

    def _copyFile(self,fname,caction):
        """
        If file needs to be copied, moves from tmp directory to
        either /usr/local/bin or /lib/systemd/system
        """
        NF = True # new file to be restarted
        comPerm = False # Used to if permissions need to be updated
        tmp_fname = fname.split('.')[0] + ".service"
        for esxer in up_service_files:
            if tmp_fname == esxer[0]:
                NF = False
        if caction == "ADDED" and NF:
            up_service_files.append([tmp_fname,"new"])
        elif NF:
            up_service_files.append([tmp_fname,'up"'])
        if '.service' in fname:
            copy2(self.tmp_path + "/" + fname, SERVICE_PATH + fname)
        else:
            if caction == 'UPDATED':
                comPerm = self.comparePermissions(fname)
            else:
                comPerm = '755'
            copy2(self.tmp_path + "/" + fname,S_FILE_PATH + fname)
            if comPerm:
                self.setPermissions(fname,comPerm)    
        pS(caction,fname)
    
    def comparePermissions(self,fname):
        """
        Checks to see if the file permissions are the same compared
        from the local copy to the GitHub copy.  Returns the permissions
        of the local copy.
        """
        exist_perm = oct(stat(S_FILE_PATH + fname).st_mode)
        prop_perm = oct(stat(self.tmp_path + "/" + fname).st_mode)
        if prop_perm != exist_perm:
            return(exist_perm)
        else:
            return(False)

    def setPermissions(self,fname,fperm):
        """
        Sets the passed file permissions to the file.
        """
        perm_mask = int(fperm[-3:],8)
        try:
            chmod(S_FILE_PATH + fname,perm_mask)
            pS("UPDATED","File permission for {}".format(fname))
        except:
            pS("iBerg","Unable to set file perfmission for {}".format(fname))


    def getServiceFiles(self):
        """
        Grabs all files located in the tmp GitHub directory
        """
        service_hash = {}
        for ser_file in self.ser_files:
            service_hash[ser_file] = self.getFileHash(self.tmp_path + "/" + ser_file)
        return(service_hash)

    def getFileHash(self,fname):
        """
        Creates and returns a file hash for the passed file.
        """
        fo = open(fname)
        file_hash = hashlib.sha256(fo.read()).hexdigest()
        fo.close()
        return(file_hash)

def getServiceList():
    """
    Parses the GitHub copy of serviceUpdater.yml to see
    which service files should be updated/added.
    It removes atdServiceUpdater from the list as it will be
    updated seperately
    """
    service_YAML = open(YAML_PATH,'r')
    service_LIST = YAML().load(service_YAML)['serviceUpdaters']
    service_YAML.close()
    service_LIST.pop(service_LIST.index(UPDATER_NAME))
    return(service_LIST)

def cloneGitRepo():
    """
    Clones the specified GitHub repo in the variables:
    GIT_PATH and GIT_BRANCH
    and copies them to a local tmp directory
    """
    if isdir(GIT_TEMP_PATH):
        deleteLocalRepo()
    pS("INFO", "Cloning {0} branch.".format(GIT_BRANCH))
    try:
        git.Repo.clone_from(GIT_PATH,GIT_TEMP_PATH,branch=GIT_BRANCH)
        pS("OK","Cloned repo!")
    except:
        pS("iBerg","Unable to reach: {0}".format(GIT_PATH))
        quit()

def deleteLocalRepo():
    """
    Deletes the local tmp copy of GitHub.
    """
    rmtree(GIT_TEMP_PATH)
    pS("REMOVED","Local repo copy")

def restartServiceFull(serlist):
    """
    Initial function to restart/start/enable services.  Calls
    daemonReload() to reload systmctl. If it's 
    existing service, it will call restartService() function.
    If new service, it will call enableService() and startService()
    """
    daemonReload()
    for sname in serlist:
         # Check if atdServiceUpdater.service
        if sname[0] == UPDATER_NAME + '.service':
            pS("OK","Exiting initial {}, new service instance starting".format(sname[0]))
        if sname[1] != 'new':
            restartService(sname[0])
        else:
            enableService(sname[0])
            startService(sname[0])
        
def stopService(sername):
    """
    Stops the passed service.
    !!! Currently not used anymore !!!
    """
    scmd = ['systemctl','stop',sername]
    stop_service = Popen(scmd)
    stop_service.wait()
    sout, serr = stop_service.communicate()
    if not serr:
        pS("OK","Stopped {0}".format(sername))
        return(True)
    else:
        pS("Error","Stopping {0}".format(sername))
        return(False)

def restartService(sername):
    """
    Restarts the passed service name
    """
    scmd = ['systemctl','restart',sername]
    start_service = Popen(scmd)
    start_service.wait()
    sout, serr = start_service.communicate()
    if not serr:
        pS("OK","Restarted {0}".format(sername))
        return(True)
    else: 
        pS("Error","Restarting {0}".format(sername))
        return(False)

def startService(sername):
    """
    Starts the passed service name
    """
    scmd = ['systemctl','start',sername]
    start_service = Popen(scmd)
    start_service.wait()
    sout, serr = start_service.communicate()
    if not serr:
        pS("OK","Started {0}".format(sername))
        return(True)
    else: 
        pS("Error","Starting {0}".format(sername))
        return(False)

def enableService(sername):
    """
    Enables the passed service name
    """
    scmd = ['systemctl','enable',sername]
    enable_service = Popen(scmd)
    enable_service.wait()
    sout, serr = enable_service.communicate()
    if not serr:
        pS("OK","Enabled {0}".format(sername))
        return(True)
    else: 
        pS("Error","Enabling {0}".format(sername))
        return(False)

def daemonReload():
    """
    Reloads the systemctl daemon, so modified
    services files will be accepted.
    """
    scmd = ['systemctl','daemon-reload']
    dr = Popen(scmd)
    dr.wait()
    dout, derr = dr.communicate()
    if not derr:
        pS("OK","Restarted systemctl daemon")
        return(True)
    else:
        pS("Error","Reloading systemctl daemon")
        return(False)

def pS(mstat,mtype):
    """
    Function to send output from service file to Syslog
    """
    mmes = "\t" + mtype
    syslog.syslog("[{0}] {1}".format(mstat,mmes.expandtabs(7 - len(mstat))))

def main():
    """
    Main function that runs the script.
    """
    global up_service_files
    # Clone remote repo
    cloneGitRepo()

    # Perform a check to see if atdServiceUpdater needs to be updated.
    atd_updater_svc = SERVICES(UPDATER_NAME)

    # If atdServiceUpdater needs to be updated, restart it
    if up_service_files:
        pS("OK","Services to be Restarted: {}".format(", ".join(upser[0] for upser in up_service_files)))
        restartServiceFull(up_service_files)
        # Reset array to empty, most likely not needed as the script will restart
        up_service_files = []

    l_service = getServiceList()
    pS("OK","Services to check: {}".format(", ".join(l_service)))

    # Iterate through all Services in YAML
    for ser in l_service:
        tmp_ser = SERVICES(ser)
        all_services.append(tmp_ser)
        # Enable all services
        daemonReload()
        enableService(ser)
    
    # Check if any files have changed and restart necessary services
    if up_service_files:
        pS("OK","Services to be Restarted: {}".format(", ".join(upser[0] for upser in up_service_files)))
        restartServiceFull(up_service_files)

if __name__ == "__main__":
    # Open Syslog
    syslog.openlog(logoption=syslog.LOG_PID)
    pS("OK","Starting...")

    # Parse through arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--branch", type=str, help="Branch to pull and test against",default=None, required=False)
    args = parser.parse_args()
    if args.branch:
        GIT_BRANCH = args.branch
    elif exists(GIT_BRANCH_PATH):
        tmp_repo_info = open(GIT_BRANCH_PATH, 'r')
        tmp_repo = YAML().load(tmp_repo_info)
        GIT_BRANCH = tmp_repo['atd-public']['branch']
        tmp_repo_info.close()
    else:
        git_yaml = {
            'atd-public': {
                'branch': 'master'
            }
        }
        with open(GIT_BRANCH_PATH, 'w') as gpath:
            YAML().dump(git_yaml, gpath)
    # Start the main Service
    main()

    pS("OK","Complete!")
    # Close Syslog
    syslog.closelog()
