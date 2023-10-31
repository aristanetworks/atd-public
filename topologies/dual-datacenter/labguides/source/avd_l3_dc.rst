AVD L3 DC Labs
===================
The goal of these labs are to introduce and demonstrate how to use AVD to deploy and configure a Layer 3 Leaf Spine EVPN/VXLAN Datacenter network.

There are 4 labs in total:
    1. Deploying DC1, using AVD + CloudVision
    2. Deploying DC2, troubleshooting connectivity issues with AVD, and going through a full CloudVision change control process
    3. Adding new VLANs to DC1, using AVD deploying through eAPI, along with an overview of AVD Documentation and State Validation 
    4. Adding a new row of border leaves to DC1, and an example of how AVD generates configuration through hierarchy and node types

After completing these labs you should have a working understanding of what AVD can do for you. For a more in-depth training with AVD, talk to your SE about attending an Arista CI Workshop.

Visit https://aristanetworks.github.io/avd-workshops/ for more information.

|

#. **Connect to the Programmability IDE**
    Connect to the **Programmability IDE** service. This IDE is running VS Code. If prompted for a password, enter in your
    lab password: ``{REPLACE_PWD}``

        .. image:: images/avd_l3_dc/Setup_ProgrammabilityIDE.png
            :align: center
        |

#. **Open a terminal and change directory to the AVD_L3_DC folder**
    Open a terminal by clicking on the top left icon > Terminal > New Terminal, or by pressing **CTRL+Shift+`** 
    Change your working directory to ``avd_l3_dc``

    .. code-block:: text

        cd labfiles/avd_l3_dc


#. **Set the Ansible password for DC1**
    We are going to add your lab password: ``{REPLACE_PWD}`` to the ``dc1.yml`` file 

    a. Open the ``/labfiles/avd_l3_dc/sites/dc1/group_vars/dc1.yml`` file 

        .. image:: images/avd_l3_dc/Setup_Select_DC1yml.PNG
            :align: center
    |


    b. Edit the ``ansible_password:`` field with your lab password: ``{REPLACE_PWD}`` 

        .. image:: images/avd_l3_dc/Setup_DC1_Password.PNG
            :align: center


|

**Lab #1: Building and Deploying DC1**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In this lab you will configure DC1 using AVD, and then deploy DC1 using CloudVision.

First we will generate the configuration using AVD, push that configuration to CloudVision using AVD, then deploy that configuration to the devices using CloudVision.

|

#. **Open CloudVision (CVP) from your initial Lab page**

    .. warning:: CloudVision can take 10-15 minutes to boot after initial lab deployment

    .. image:: images/avd_l3_dc/Lab1_Open_CVP.PNG
        :align: center

    |

    Login to CloudVision. Username: ``arista``, Password: ``{REPLACE_PWD}``

    .. image:: images/avd_l3_dc/Lab1_CVP_Login.PNG
        :align: center


#. **Open the topology view and filter based on tags for DC1**

    a. Click on the topology view

        .. image:: images/avd_l3_dc/Lab1_open_CVP_topology_view.PNG
            :align: center


    b. Apply a filter to specify viewing only DC1 devices

        .. image:: images/avd_l3_dc/Lab1_CVP_Filter.PNG
            :align: center
        |
        .. image:: images/avd_l3_dc/Lab1_CVP_Filter2.PNG
            :align: center
        |


        The topology view should now only display devices that are in the DC1 container that exists within CloudVision.  
        Your view should appear similar to the following:

        .. image:: images/avd_l3_dc/Lab1_S1filter_before.PNG
            :align: center

        .. note:: The switch interlinks are down in this view, because they are not configured and up yet. 


#. **Open the Device view and look at s1-leaf1**

    a. Click on ``Devices``, then select ``s1-leaf1``. On the device view for s1-leaf1, select ``Configuration`` under ``System``, then examine the current running configuration.

        .. note:: s1-leaf1 currently contains only a basic minimal configuration. Enough to allow Ansible to login and push a full configuration.
    
    b. While ``s1-leaf1`` is still being viewed, select ``Routing -> BGP`` and look and verify there are no BGP peers 

        .. image:: images/avd_l3_dc/Lab1_No_BGP_Peers.PNG
            :align: center

#. **Return to your Programmability IDE**

    You will build and then deploy the entirety of DC1 using a makefile 

    .. note:: The makefile contains recipes to allow you to run the lab playbooks using a simple command syntax

#. **Build and deploy DC1 using the makefile**

    Select your terminal window, then type and run the following command:

    .. code-block:: text

        make build_dc1

    .. note:: Make sure your terminal working directory is within the ``/home/coder/project/labfiles/avd_l3_dc`` folder

    If the playbook ran successfully, you should see output similar to the following:

        .. code-block:: text

            PLAY RECAP ***************************************************************************************************************************
            s1-leaf1                   : ok=5    changed=3    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0   
            s1-leaf2                   : ok=5    changed=3    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0   
            s1-leaf3                   : ok=5    changed=3    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0   
            s1-leaf4                   : ok=5    changed=3    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0   
            s1-spine1                  : ok=13   changed=8    unreachable=0    failed=0    skipped=2    rescued=0    ignored=0   
            s1-spine2                  : ok=5    changed=3    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0   

    Now that the configurations have been created, we will push them to CloudVision and have CloudVision automatically deploy to the devices. 

    Run the following command:

    .. code-block:: text

        make deploy_dc1_cvp

    If the playbook ran successfully, you should see output similar to the following:

    .. code-block:: text

        PLAY RECAP ***************************************************************************************************************************
        cvp                        : ok=10   changed=0    unreachable=0    failed=0    skipped=3    rescued=0    ignored=0   

#. **Return to CloudVision**

    a. Go the **Device** view of s1-leaf1 and view the ``Routing -> BGP`` output

        .. image:: images/avd_l3_dc/Lab1_BGP_Peers_Up.PNG
            :align: center

        .. note:: s1-leaf1 should now have several BGP peers in the Established state
    
    b. Go the **Topology** view, you will need to create a new filter because AVD created new containers for the DC1 devices

            .. code-block:: text

                Container:dc1_fabric

        .. note:: Now that DC1 is configured, you should see correct tree structure for DC1

        .. image:: images/avd_l3_dc/Lab1_Topology_after.PNG
            :align: center




Lab #1: Summary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Congratulations!**

You have now deployed an entire datacenter simply by running two make commands. 

**This** is the power of automation! 

|
|

**Lab #2: Building and Deploying DC2**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In this lab you will configure DC2 using AVD and then deploy DC2 using CloudVision while going through the normal change control process.
You will also troubleshoot some common connectivity issues and gain understanding of how to fix them and take a look at Ansible's inventory file.  

|

#. **Set the Ansible password for DC2**

    Once again, we are going to add your lab password: ``{REPLACE_PWD}`` to the ``dc2.yml`` file 

    a. Open the ``labfiles/avd_l3_dc/sites/dc2/group_vars/dc2.yml`` file 

    b. Edit the ``ansible_password:`` field with your lab password: ``{REPLACE_PWD}`` 

#. **Build DC2 using the makefile**

    Run the following command:

    .. code-block:: text

        make build_dc2

    This time, there will be errors when trying to build the DC2 configs

        .. image:: images/avd_l3_dc/Lab2_inventory_failure.PNG
            :align: center

    Looking at the details of the error message, we can see that is a result of not being able to reach the hosts

        .. image:: images/avd_l3_dc/Lab2_NoRoute.PNG
            :align: center

    Looking further at the IP addresses that are trying to be reached, we can see that these IP addresses are wrong and don't match the IP addresses in the Dual Data Center topology diagram. 
    We can fix this by entering the correct IP addresses for Leafs 1-4 in the DC2 inventory file.

#. **Correct the errors in the DC2 inventory.yml file**

    Open the ``sites/dc2/inventory.yml`` file, and edit the IP addresses for Leafs1-4 to the following:

    .. code-block:: text

        s2-leaf1:   192.168.0.22
        s2-leaf2:   192.168.0.23
        s2-leaf3:   192.168.0.24
        s2-leaf4:   192.168.0.25

    |

    .. image:: images/avd_l3_dc/Lab2_inventory_edit.PNG
        :align: center

#. **Re-build DC2 using the makefile**

    Run the following command:

    .. code-block:: text

        make build_dc2

    There should be no errors building the DC2 config this time.

#. **Deploy DC2 using the makefile**

    We are going to deploy DC2 using CloudVision similar to how we deployed DC1, but this time we will also go through the full change control process within CloudVision.

    Run the following command:

    .. code-block:: text

        make deploy_dc2_cvp

    The command should execute successfully, but unlike in Lab 1, CloudVision will not automatically deploy the change. 
    
    We need to go through the change control process within CloudVision to deploy the change this time.

    .. note:: The reason CloudVision didn't auto deploy is because the deploy_dc2_cvp.yml playbook has "execute_tasks:" set to *false*, which requires you to go through the CloudVision change control approval. Whereas in Lab1, the deploy_dc1_cvp.yml had the execute_tasks: set to *true*.

        .. image:: images/avd_l3_dc/Lab2_CVP_Parallel_Tasks.PNG
            :align: center

#. **Create, approve, and execute the change within CloudVision**

    Go back to CloudVision, then go to ``Provisioning > Tasks`` 

        a. Select all the tasks then click on ``Create Change Control``

            .. image:: images/avd_l3_dc/Lab2_CVP_Select_Tasks.PNG
                :align: center

        b. Click on ``Parallel`` arrangement, then ``Create Change Control with 6 Tasks``

            .. image:: images/avd_l3_dc/Lab2_CVP_Parallel_Tasks.PNG
                :align: center

        c. Click on the ``Review and Approve`` button
        
            .. image:: images/avd_l3_dc/Lab2_CVP_Approve.PNG
                :align: center

        d. Click on the ``Execute immediately`` toggle, and then ``Approve and execute`` button
        
            .. image:: images/avd_l3_dc/Lab2_CVP_Execute.PNG
                :align: center

#. **Verify your changes**

    a. Go the **Device** view of s2-leaf1 and view the ``Routing -> BGP`` output

        .. note:: s2-leaf1 should have several BGP peers in the Established state
    
    b. Go the **Topology** view, create a new filter for DC2

            .. code-block:: text

                Container:dc2_fabric

Lab #2: Summary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Congratulations!**

You built DC2, fixed errors with the DC2 Ansible inventory file, went through a full CloudVision change control, and verified it was deployed successfully. 

|
|
|


**Lab #3: Adding new VLANs to DC1**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In this lab you will add new VLANs to DC1, deploy directly to the switches using eAPI, and then get familiar with the AVD ``Documentation`` and ``Validate State`` features

|

#. **Edit DC1's fabric_services to include VLANs 100 and 200**

    a. Open ``/sites/dc1/group_vars/dc1_fabric_services.yml`` file within the IDE

    

    b. Uncomment out the following lines for VLANs 100 and 200

        .. code-block:: text

            100:
                name: VLAN 100 - Lab 3
                description: one hundred
                tags: ['DC']
                enabled: true
                mtu: 9014
                ip_address_virtual: 10.20.100.1/24
            200:
                name: VLAN 200 - Lab 3 
                description: two hundred
                tags: ['DC']
                enabled: true
                mtu: 9014
                ip_address_virtual: 10.20.200.1/24

        .. note:: You can comment or uncomment multiple lines at once by selecting all of them and pressing ``Ctrl+/`` or ``Cmd+/``

#. **Run the makefile to re-build DC1**

    Run the build makefile for DC1 to re-generate the configuration with the additional VLANs

        .. code-block:: text

            make build_dc1

    Run the deploy makefile using eAPI, this option allows you to deploy your configurations directly to your switches        

        .. code-block:: text

            make deploy_dc1_eapi

#. **Verify your changes**

    We are going to verify the VLANs were successfully deployed to the switches, open the device view in CloudVision. You should see red symbols next to s1-leaf1 through s1-leaf4

        .. note:: This warning from CVP indicates that the switches running configuration no longer matches the designed configuration in CVP. The reason for this is we deployed Lab1 using CVP, but we bypassed CVP in Lab3 by deploying directly to the switches, resulting in a configuration mismatch.

    a. Go the **Device** view of s1-leaf1 and view the ``System -> Configuration`` output

        .. note:: Notice how s1-leaf1 not only has VLAN 100 and 200, but also that Layer 3 VLAN interfaces, and the VXLAN to VNI mapping were all configured as well. 

    a. Go the **Device** view of s1-leaf1 and view the ``Switching -> VXLAN`` output

        .. note:: You may be wondering why VXLAN configuration was also added for VLANs 100 and 200. The dc2.yml file specifies that all the switches in the DC are Layer 3 and a VXLAN tunnel endpoint, so when you add a new VLAN, AVD recognizes all the other configuration that will be required to make the VLAN functional in a Layer 3 Leaf-Spine design utilizing VXLAN. 
        

#. **View the outputs from AVD's Documentation and Validate State functions**

    AVD will auto-generate network documentation everytime you build a new configuration, presenting the device and fabric level documentation in an easy to read format that is easily underestandable by non-expert administrators. 

    a. Within the IDE, open the output from: ``/sites/dc1/documentation/devices/s1-leaf1.md``

        .. note:: Right click the file and select "Open Preview" to display the file correctly

    b. Within the IDE, open the output from: ``/sites/dc1/documentation/fabric/dc1_fabric_documentation.md``


    AVD also has the ability to run a series of tests on your network after deployment to verify the current network state

    c. Within the IDE, open the output from: ``/sites/dc1/reports/fabric/dc1_fabric_state.md``

        .. note:: Your example report intetionally includes multiple errors as an example. An in-depth dicussion of this testing is provided in our CI workshops courses.

|

Lab #3: Summary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Congratulations!**

You deployed new VLANs to DC1 directly through eAPI access to the switches, verified it was deployed successfully, then looked at examples of AVD documentation and reporting.

|


**Lab #4: Adding a pair border leafs to DC1**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In this lab you will edit several YAML files to add a new row to DC1 in order to add a new pair of border leaf switches.

Pay attention to how much you *don't* have to configure when setting up a new row. This is because much of the configuration is automatically inherited and generated from both the hierarchy/structure and pre-built node types that exist within AVD.

|

#. **Add the new switches to the DC1 inventory file**

    Open the ``/sites/dc1/inventory.yml`` file and uncomment out the lines for ``s1-brdr1`` and ``s1-brdr2``

        .. image:: images/avd_l3_dc/Lab4_inventory.PNG
            :align: center

#. **Edit the DC1 fabric file to add the configuration parameters for the new border leaf switches**

    Open the ``/sites/dc1/group_vars/dc1_fabric.yml`` file and uncomment out lines 82-110: 
    
        .. image:: images/avd_l3_dc/Lab4_Uncomment_Lines.PNG
            :align: center
    
#. **Build and Deploy DC1 using the makefiles**

    Now that the inventory and fabric variables have been set, we need to re-build and redeploy DC1.

    a. Build DC1 using the makefile

        .. code-block:: text

            make build_dc1

    b. Deploy DC1 using the makefile 

        .. code-block:: text

            make deploy_dc1_cvp

#. **Verify the DC1 border leaf switches were successfully deployed within CloudVision**

    b. Go the **Topology** view, create a filter for DC1

            .. code-block:: text

                Container:dc1_fabric

        .. note:: You should see a total of 8 devices now

        .. image:: images/avd_l3_dc/Lab4_CVP_Topology.PNG
            :align: center

Lab #4: Summary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Congratulations!**

You successfully added the configurations required for a new border leaf pair to DC1, built and deployed them using makefiles, then verified the changes within CloudVision

|
|

**Would you like to know more?**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Arista has workshops designed to teach you the fundamentals of automation and exactly how to deploy using AVD.

**https://aristanetworks.github.io/avd-workshops/**

Speak with your SE about attending one of our Arista CI Workshops in your area.

