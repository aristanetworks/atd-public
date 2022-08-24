CloudVision Initial Configuration
================================

.. Note:: 

    This must be deployed as a veos topology with the CVP version set to **CVP-2022.1.0-bare**

1. Log into the Arista Test Drive Portal by using SSH  

    .. code-block:: text

       ssh arista@{unique_address}.topo.testdrive.arista.com


or by clicking on "Console Access" on the main ATD screen. Log in with the arista user and the auto-generated password

.. thumbnail:: images/aa-initial_configuration/initial-config-1.png

|

2. Once you're on the Jump host, select option **98. SSH to Devices(SSH)**

|

3. Again, select **98. Shell (shell/bash)**. This will take you to the bash prompt for our jump host 

|

4. Since CVP is not configured and doesn't have an IP yet, we cannot SSH to it. Instead we need to create a Console connection to the VM by using the command **sudo virsh console cvp1** at the arista@devbox:~$ prompt

|

.. code-block::

    *****************************************
    *****Jump Host for Arista Test Drive*****
    *****************************************


    ==========Device SSH Menu==========

    Screen Instructions:

    * Select specific screen - Ctrl + a <number>
    * Select previous screen - Ctrl + a p
    * Select next screen - Ctrl + a n
    * Exit all screens (return to menu) - Ctrl + a \

    Please select from the following options:
    1. host1 (host1)
    2. host2 (host2)
    3. leaf1 (leaf1)
    4. leaf2 (leaf2)
    5. leaf3 (leaf3)
    6. leaf4 (leaf4)
    7. spine1 (spine1)
    8. spine2 (spine2)
    9. cvx01 (cvx01)

    Other Options: 
    96. Screen (screen) - Opens a screen session to each of the hosts
    97. Back to Previous Menu (back)
    98. Shell (shell/bash)
    99. Back to Main Menu (main/exit) - CTRL + c

    What would you like to do? 98
    arista@devbox:~$ sudo virsh console cvp1
    setlocale: No such file or directory
    Connected to domain 'cvp1'
    Escape character is ^] (Ctrl + ])

    CentOS Linux 7 (Core)
    Kernel 5.12.12-1.el7.elrepo.x86_64 on an x86_64

    localhost login: cvpadmin


You should now see the **localhost login:** prompt. 

|

5. Log in using **cvpadmin** as the username. You will then be asked to set a password. 

    .. code-block::

        localhost login: cvpadmin
        Changing password for user root.
        New password: 
        Retype new password: 
        passwd: all authentication tokens updated successfully.

        CVP Installation Menu

        [q]uit [p]rint [s]inglenode [m]ultinode [r]eplace [u]pgrade
        >

|

6. Since we are only setting up one CVP server, select **s** to choose singlenode

|

7. You will now fill in the network settings for your CVP installation. Please enter the following into the fields. You can then select **v** to verify your install prior to applying the changes. 

|

.. Note::

    **CloudVision Deployment Model:** - This is to select whether you would like a default deployment or if you would only like to install wifi-analytics. For this lab, we will select **d** for default 

    **DNS Server Addresses (IPv4 Only):** - comma-separated list of DNS servers. **192.168.0.1** will be acting as our DNS Server, NTP Server, and Default Gateway in our lab. 192.168.0.1 is the IP of our lab jump host that we used to access the CVP VM.

    **DNS Domain Search List:** comma-separated list of DNS domains on your network. We will set this to **atd.lab**

    **Number of NTP Servers:** - Allows you to specify how many NTP servers you have in your environment. We set this to **1** for this lab

    **NTP Server Address:** - comma separated list of NTP servers. enter **192.168.0.1** for this lab

    **Is Auth enabled for NTP Server #1:** - allows you to optionally set authentication parameters for NTP servers in your environment. We do not use authentication, so we will keep the default **n** value

    **Cluster Interface Name:** - Allows you to specify a cluster interface name, This is typically left as the default value

    **Device Interface Name:** - Allows you to specify a device interface name, This is typecally also left as the default value

    **Telemetry Ingest Key:** - This must be the same value for each node in a 3-node cluster. For our sinngle node install, we will just use **atd-lab**

    **CloudVision WiFi Enabled:** - This should be enabled if you are deploying Access Points in your environment. For our lab scenario, we will select the default value **N**

    **Enter a private IP range for the internal cluster network (overlay):** This is the private IP range used for the kubernetes cluster network. This value must be unique; must be /20 or larger; shouldn't be link-local, reserved or multicast. Default value is 10.42.0.0/16. We will accept this default for our lab.

    |

    **Hostname (FQDN):** - This will be the URL you enter to access CloudVision once the deployment is complete. We will set this to **cvp.atd.lab** for this lab

    **IP Address of eth0:** - This will be the IP address of this node. We set this to **192.168.0.5** in this lab

    **Netmask of eth0:** - Our example will be a /24, so we set this to **255.255.255.0**

    **NAT IP Address of eth0:** - This would be set if you are using NAT to access CVP. For the purposes of this lab, we will leave this blank

    **Default Gateway:** - Set this to **192.168.0.1** (our lab jump host)

    **Number of Static Routes:** - Leave blank 

    **TACACS Server IP Address:** - Leave blank



.. code-block:: text
    :emphasize-lines: 12-23, 27-33
    
    CVP Installation Menu

    [q]uit [p]rint [s]inglenode [m]ultinode [r]eplace [u]pgrade
    >s

    Enter the configuration for CloudVision Portal and apply it when done.
    Entries marked with '*' are required.


    Common Configuration:

    CloudVision Deployment Model [d]efault [w]ifi_analytics: d
    DNS Server Addresses (IPv4 Only): 192.168.0.1
    DNS Domain Search List: atd.lab
    Number of NTP Servers: 1
    NTP Server Address (IPv4 or FQDN) #1: 192.168.0.1
    Is Auth enabled for NTP Server #1: n
    Cluster Interface Name: eth0
    Device Interface Name: eth0
    Telemetry Ingest Key: atd-lab
    CloudVision WiFi Enabled: no
    *Enter a private IP range for the internal cluster network (overlay): 10.42.0.0
    /16

    Node Configuration:

    *Hostname (FQDN): cvp.atd.lab
    *IP Address of eth0: 192.168.0.5
    *Netmask of eth0: 255.255.255.0
    NAT IP Address of eth0: 
    *Default Gateway: 192.168.0.1
    Number of Static Routes: 
    TACACS Server IP Address: 

    Singlenode Configuration Menu

    [q]uit [p]rint [e]dit [v]erify [s]ave [a]pply [h]elp ve[r]bose
    >v
    Valid config format.
    Applying proposed config for network verification.
    saved config to /cvpi/cvp-config.yaml
    Running : cvpConfig.py tool...
    Stopping: network
    Running : /bin/sudo /bin/systemctl stop network
    Running : /bin/sudo /bin/systemctl is-active network
    Starting: network
    Running : /bin/sudo /bin/systemctl start network
    [ 4489.294334] warning: `/bin/ping' has both setuid-root and effective capabilities. Therefore not raising all capabilities.
    Valid config.


All of these settings are saved in the /cvpi/cvp-config.yaml file

|

8. Finally, enter **a** to apply the changes and begin CVP installation.

|

9. You should now see the installation running and a lot of scrolling text. This should take about 10 minutes to complete. You know it's close to complete when flannelbr0 shows up.

|

10. When you see the configuration menu on the screen again, we know that CVP has been configured successfully. Go back to the main ATD screen and click on the **CVP** link.

.. thumbnail:: images/aa-initial_configuration/initial-config-3.png
    :width: 50%

|

11. On the login screen, use **cvpadmin** as the username and the password you set in step 5 above

|

12. You will need to change this password at first login, and you will also be asked for an email address. You can put anything you want in this field. Give your cluster a name and Logo on step 3, then click **Finish**.

.. thumbnail:: images/aa-initial_configuration/initial-config-4.png
    :width: 80%
|

13. Log into CVP one more time and you'll be greeted by the Devices screen, along with green check marks indicating that all of our devices are streaming to CVP. Success!

|

14. Now lets set up network-admin and network-operator accounts. Click on the gear in the upper right. Select **Users** under **Access Control**. Fill out the Add User screen and under **Roles** Select **network-admin**. Click **Add**.  Follow this step again, but select **network operator** to set up the network-operator account.


.. thumbnail:: images/aa-initial_configuration/initial-config-5.png
    :width: 70%

|

15. Bonus Step - (Requires an Arista.com account) We can now subscribe to bug alerts, so that CVP will populate compliance data automatically on the **Compliance Overview** screen.

16. Browse to **arista.com** and log in. Once logged in, click on your name on the top bar and select **My Profile**. Copy your Access Token listed at the bottom of the page.


17. Back in CVP, click on the Gear icon in the top right, then select **Compliance Updates** on the left. Paste the Token that was copied from arista.com and click **Save**

.. thumbnail:: images/aa-initial_configuration/initial-config-6.png

|

.. Warning:: 

    This step will error in the ATD environment, but on a standard deployment, where the CVP server can reach the internet, it will complete successfully.



.. Note::
    
    Arista recommends a multinode setup (3 node) for on-prem deployments. For this lab, however, we deployed a singlenode installation to preserve cloud resources. A multinode install is exactly the same as the singlenode setup, you would just repeat the same steps for the secondary and tertiary nodes.




