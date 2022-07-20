CloudVision Portal Upgrade
==========================
* <Add in screen capture gif of the process described>
 
* Log into the Arista Test Drive Portal Web interface  

    (link to connecting)

* Log in to the Programmability IDE

   <screenshot of the link>

* In the vs-code window select the upper left menu icon, then select Terminal, then New Terminal

   <screenshot of getting a new terminal>

* Retrieve your api access token from arista.com
   
   * navigate to https://www.arista.com/en/users/profile
   * record the api access token for your user account


* Next we will perform the following steps in the Terminal

   #. Check CVP server current version number
   #. Clone example scripts repo
   #. Download the CVP upgrade file from arista.com
   #. Transfer the upgrade file to the CVP server
   #. Start the CVP upgrade Process 
   #. Check CVP server version number to verify upgrade is complete

#. Check CVP server current version number
   
    * SSH to the CVP server 

      .. code-block:: shell

        ➜  project ssh root@192.168.0.5
        root@192.168.0.5's password: 
        Last login: Wed Jul 20 16:01:23 2022 from gateway
        [root@cvp ~]# 

    
    * grep VERSION from the cvp env file 

      .. code-block:: shell

        [root@cvp ~]# cat /etc/cvpi/env | grep VERSION
        CVP_VERSION=2021.2.2

    * Exit SSH session to the CVP server 

      .. code-block:: shell

        [root@cvp ~]# exit
        logout
        Connection to 192.168.0.5 closed.
        ➜  project 
    .. note::
       You should now be back to the terminal session on the ATD jumphost in the vs-code window. Notice the prompt changes from the previous step as you exit the SSH session.

#. Clone example scripts repo, and examine the script help option

    * Clone the repo

      .. code-block:: shell

        ➜  project 
        ➜  project cd labfiles 
        ➜  labfiles git clone https://github.com/Hugh-Adams/Example_Scripts.git
        Cloning into 'Example_Scripts'...
        remote: Enumerating objects: 464, done.
        remote: Counting objects: 100% (464/464), done.
        remote: Compressing objects: 100% (357/357), done.
        remote: Total 464 (delta 190), reused 368 (delta 102), pack-reused 0
        Receiving objects: 100% (464/464), 1.34 MiB | 10.62 MiB/s, done.
        Resolving deltas: 100% (190/190), done.

    * Navigate to the directory where the script resides 

      .. code-block:: shell

        ➜  labfiles cd Example_Scripts/Tools/Get_UpgradeFile_CVP  
        

        ➜  Get_UpgradeFile_CVP git:(main) ls
        CVPgetUpgrade.py  CVPgetUpgradeV2.py  CVPgetUpgradeV2.py.zip

 
    * Invoke the CVPgetUpgradeV2.py script with the --help flag

      .. code-block:: shell

        ➜  Get_UpgradeFile_CVP git:(main) python3 CVPgetUpgradeV2.py --help
        usage: CVPgetUpgradeV2.py [-h] --upgrade UPGRADE --token TOKEN [--proxyType PROXYTYPE] [--proxyAddr PROXYADDR] [--test] [--nofile]

        optional arguments:
         -h, --help            show this help message and exit
         --upgrade UPGRADE     CloudVision Upgrade File Name i.e. cvp-upgrade-2020.2.3.tgz
         --token TOKEN         User API access token found at https://www.arista.com/en/users/profile
         --proxyType PROXYTYPE
                        Type of proxy http or https
         --proxyAddr PROXYADDR
                               IP address or URL of proxy server
         --test
         --nofile

#. Download the CVP Upgrade file using api access token (destination: /tmp/upgrade)

    .. code-block:: shell

        ➜  Get_UpgradeFile_CVP git:(main) python3 CVPgetUpgradeV2.py --token <removed> --upgrade cvp-upgrade-2022.1.0.tgz
        <Response [200]>


        ➜  Get_UpgradeFile_CVP git:(main) ls /tmp/upgrade 
        cvp-upgrade-2022.1.0.tgz

#. Transfer the upgrade file to the CVP server

    * Make /tmp/upgrade directory on CVP server
   
      .. code-block:: shell

          ➜  Get_UpgradeFile_CVP git:(main) ssh root@192.168.0.5 mkdir /tmp/upgrade
          root@192.168.0.5's password:  

    * Transfer the CVP upgrade file to the CVP Server

      .. code-block:: shell

          ➜  Get_UpgradeFile_CVP git:(main) scp /tmp/upgrade/cvp-upgrade-2022.1.0.tgz root@192.168.0.5:/tmp/upgrade/
          root@192.168.0.5's password: 
          cvp-upgrade-2022.1.0.tgz                                                                                                25% 1421MB  79.4MB/s   00:52 ETA


#. Start the CVP upgrade Process 

    * ssh to cvp the server, navigate to /tmp/upgrade    

      .. code-block:: shell

        ➜  Get_UpgradeFile_CVP git:(main) ssh root@192.168.0.5
        root@192.168.0.5's password: 
        Last login: Tue Jul 19 16:19:47 2022 from gateway

        [root@cvp ~]# cd /tmp/upgrade

    * Change user to cvpadmin, choose upgrade (u)

      .. code-block:: shell

        [root@cvp upgrade]# su cvpadmin

        CVP Installation Menu

        [q]uit [p]rint [s]inglenode [m]ultinode [r]eplace [u]pgrade
        >u
        Bootstrapping upgrade  

        ... ommitted output ...

#. Check CVP server version number to verify upgrade is successful and complete

   .. code-block:: shell

       [root@cvp ~]# cat /etc/cvpi/env | grep VERSION
       CVP_VERSION=2022.1.0

LAB COMPLETE

   