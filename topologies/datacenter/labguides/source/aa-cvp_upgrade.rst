.. # define a hard line break for HTML
.. |br| raw:: html

   <br />

CloudVision Portal Upgrade
==========================
|br|

.. note::
   This lab requires valid credentials on arista.com to download CVP software upgrades.
   Without an entitled account you will not be able to complete this lab.

|br|

* Retrieve your api access token from arista.com
   
   * navigate to https://www.arista.com/en/users/profile
   * record the api access token for your user account

* Log in to the vs-code Programmability IDE 

  .. thumbnail:: images/connecting/connecting_IDE.png
     :align: center
     :width: 50%

           Click image to enlarge

  |

* In the vs-code window select the upper left menu icon, then select Terminal, then New Terminal

  .. thumbnail:: images/connecting/connecting_vs-code_terminal.png
     :align: center
     :width: 50%

           Click image to enlarge

  |

* Next we will perform the following steps in the Terminal

   #. Check CVP server current version number
   #. Clone example scripts repo
   #. Download the CVP upgrade file from arista.com
   #. Transfer the upgrade file to the CVP server
   #. Start the CVP upgrade Process 
   #. Check CVP server version number to verify upgrade is complete

#. Check CVP server current version number
   
    * SSH to the CVP server at ``192.168.0.5`` as root using password ``cvproot`` 

      .. code-block:: shell

        ➜  project ssh root@192.168.0.5
        root@192.168.0.5's password: 
        Last login: Wed Jul 20 16:01:23 2022 from gateway
        [root@cvp ~]# 

    
    * Check CVP server version with **cvpi** command

      .. code-block:: shell

        [root@cvp ~]# cvpi version


        cvpi version 2021.2.2-base-3-g391d091 go1.13.6
        [root@cvp ~]# 

    * Exit SSH session to the CVP server 

      .. code-block:: shell

        [root@cvp ~]# exit
        logout
        Connection to 192.168.0.5 closed.
        ➜  project 
    
    .. note::
       You should now be back to the terminal session on the ATD jumphost in the vs-code window. Notice the prompt changes back to **➜ project** from the previous step as you exit the SSH session.

#. Clone example scripts repo, and examine the script help option

    .. note::
       This repo will provide a handy script to download the CVP upgrade file **locally** to the ATD jump host.
       This script can also be used outside the ATD lab to download the upgrade file directly to the CVP server.

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

 
    * Invoke the **CVPgetUpgradeV2.py** script with the ``--help`` flag. Notice the ``--token`` and ``--upgrade`` argument options.

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

#. Download the CVP Upgrade file using api access token retrieved earlier

    .. code-block:: shell

        ➜  Get_UpgradeFile_CVP git:(main) python3 CVPgetUpgradeV2.py --token <removed> --upgrade cvp-upgrade-2022.1.1.tgz
        <Response [200]>


        ➜  Get_UpgradeFile_CVP git:(main) ls /tmp/upgrade 
        cvp-upgrade-2022.1.1.tgz

    .. note:: 
       The download will be written to the ``/tmp/upgrade`` folder. 


       The script does not output download progress, and will take some time to complete with the ``<Response [200]>`` code. Please be patient.

#. Transfer the upgrade file to the CVP server

    * Make /tmp/upgrade directory on CVP server
   
      .. code-block:: shell

          ➜  Get_UpgradeFile_CVP git:(main) ssh root@192.168.0.5 mkdir /tmp/upgrade
          root@192.168.0.5's password:  

    * Transfer the CVP upgrade file to the CVP Server

      .. code-block:: shell

          ➜  Get_UpgradeFile_CVP git:(main) scp /tmp/upgrade/cvp-upgrade-2022.1.1.tgz root@192.168.0.5:/tmp/upgrade/
          root@192.168.0.5's password: 
          cvp-upgrade-2022.1.1.tgz                                                                                                25% 1421MB  79.4MB/s   00:52 ETA


#. Start the CVP upgrade Process 

    * SSH to cvp the server, navigate to /tmp/upgrade    

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

      [root@cvp ~]# cvpi version


      cvpi version 2022.1.1-2 go1.17.5
      [root@cvp ~]# 

LAB COMPLETE

   