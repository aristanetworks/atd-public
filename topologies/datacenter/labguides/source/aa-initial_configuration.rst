CloudVision Initial Configuraion
================================

1. Log into the Arista Test Drive Portal by using SSH  

    .. code-block:: text

       ssh arista@{unique_address}.topo.testdrive.arista.com


or by clicking on "Console Access" on the main ATD screen. Log in with the arista user and the auto-generated password

.. thumbnail:: images/aa-initial_configuration/initial-config-1.png

|

2. Once you're on the Jump host, select option **98. SSH to Devices(SSH)**

|

3. On the next screen, select **98. Shell (shell/bash)**

|

4. Since CVP is not configured and doesn't have an IP yet, we cannot SSH to it. Instead we need to create a Console connection to the VM by using the command **sudo virsh console cvp1** at the arista@devbox:~$ prompt

|

.. thumbnail:: images/aa-initial_configuration/initial-config-2.png
    :width: 75%

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

.. Note::
    
    Arista recommends a multinode setup (3 node) for on-prem deployments. For this lab, however, we will be deploying a singlenode installation to preserve cloud resources. A multinode install is exactly the same as the singlenode setup, you would just repeat the same steps for the secondary and tertiary nodes.

6. At the prompt, select **s** to choose singlenode

7. You will now fill in the network settings for your CVP installation. Please enter the following into the fields. You can then select **v** to verify your install prior to applying the changes. 

.. code-block:: text
    :emphasize-lines: 12-16
    
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

12. You will need to change this password at first login, and you will also be asked for an email address. You can put anything you want in this field, and then click **Finish**.

|

13. Log into CVP one more time and you'll be greeted by the Devices screen, along with green check marks indicating that all of our devices are streaming to CVP. Success!






