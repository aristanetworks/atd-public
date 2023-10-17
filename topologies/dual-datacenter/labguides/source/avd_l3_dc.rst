AVD L3 DC Labs
===================
The goal of these labs are to demonstrate how to use AVD to deploy and configure EVPN/VXLAN Datacenter networks.

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

    a. Open the ``sites/dc1/group_vars/dc1.yml`` file 

        .. image:: images/avd_l3_dc/Setup_Select_DC1yml.PNG
            :align: center
    |


    b. Edit the ``ansible_password:`` field with your lab password: ``{REPLACE_PWD}`` 

        .. image:: images/avd_l3_dc/Setup_DC1_Password.PNG
            :align: center


|

**Lab #1: Building and Deploying DC1**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In this lab you will configure DC1 using AVD and then deploy DC1 using CloudVision

|

#. **Open Cloudvision from your initial Lab page**

    .. warning:: Cloudvision can take 10-15 minutes to boot after initial lab deployment

    .. image:: images/avd_l3_dc/Lab1_Open_CVP.PNG
        :align: center

    |

    Login to Cloudvision. Username: ``arista``, Password: ``{REPLACE_PWD}``

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


        Your view should appear similar to the following

        .. image:: images/avd_l3_dc/Lab1_S1filter_before.PNG
            :align: center

        .. note:: The current topology is very basic because DC1 is undeployed


#. **Open the Device view and look at S1-Leaf1**

    a. Select ``Configuration`` and look at the current running config 

        .. note:: S1-Leaf1 currently contains only a basic minimal configuration. Enough to allow Ansible to login and push a full configuration.
    
    b. Select ``Routing -> BGP`` and look and verify there are no BGP peers 



#. **Return to your Programmability IDE**

    You will build and then deploy the entirety of DC1 using a makefile 

    .. note:: The makefile contains recipes to allow you to run the lab playbooks using a simple command syntax

#. **Build and deploy DC1 using the makefile**

    Run the following command:

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

    Now that the configurations have been created, we will deploy them using Cloudvision

    Run the following command:

    .. code-block:: text

        make deploy_dc1_cvp

    If the playbook ran successfully, you should see output similar to the following:

    .. code-block:: text

        INSERT TEXT HERE

#. **Return to Cloudvision**

    a. Go the **Device** view of S1-Leaf1 and view the ``Routing -> BGP`` output

        .. note:: S1-Leaf1 should now have several BGP peers in the Established state
    
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

**This** is the power automation can bring you. 

|
|

**Lab #2: Building and Deploying DC2**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In this lab you will configure DC2 using AVD and then deploy DC2 using CloudVision while going through the normal change control process

|

#. **Set the Ansible password for DC2**

    Once again, we are going to add your lab password: ``{REPLACE_PWD}`` to the ``dc2.yml`` file 

    a. Open the ``sites/dc2/group_vars/dc2.yml`` file 

    b. Edit the ``ansible_password:`` field with your lab password: ``{REPLACE_PWD}`` 

#. **Build DC2 using the makefile**

    Run the following command:

    .. code-block:: text

        make build_dc2

    This time, there will be errors when trying to build the DC2 configs

        .. image:: images/avd_l3_dc/Lab2_inventory_failure.PNG
            :align: center

    These errors are the result of the IP addresses for Leafs 1-4 being incorrect in the DC2 inventory file

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

    We are going to deploy DC2 using Cloudvision similar to how we deployed DC1, but this time we will also go through the full change control process within Cloudvision.

    Run the following command:

    .. code-block:: text

        make deploy_dc2_cvp

    The command should execute successfully, but we need to go through the change control process within Cloudvision to deploy the change.

#. **Create, approve, and execute the change within Cloudvision**

    Go back to Cloudvision, then go to ``Provisioning > Tasks`` 

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

    a. Go the **Device** view of S1-Leaf2 and view the ``Routing -> BGP`` output

        .. note:: S1-Leaf1 should have several BGP peers in the Established state
    
    b. Go the **Topology** view, create a new filter for DC2

            .. code-block:: text

                Container:dc2_fabric

Lab #2: Summary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Congratulations!**

You built DC2, fixed errors with the DC2 Ansible inventory file, went through a full Cloudvision change control, and verified it was deployed successfully. 

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

    We are going to verify the VLANs were successfully deployed to the switches. 

    a. Go the **Device** view of S1-Leaf1 and view the ``Switching -> VXLAN`` output

    b. go the **Device** view of S1-Leaf1 and view the ``System -> Configuration`` output

        .. note:: Notice how S1-Leaf1 not only has VLAN 100 and 200, but also that Layer 3 VLAN interfaces, and the VXLAN to VNI mapping were all configured as well. 

#. **View the outputs from AVD's Documentation and Validate State functions**

    AVD will auto-generate network documentation everytime you build a new configuration, presenting the device and fabric level documentation in an easy to read format that is easily underestandable by non-expert administrators. 

    a. Within the IDE, open the output from: ``/sites/dc1/documentation/devices/s1-leaf1.md``

    b. Within the IDE, open the output from: ``/sites/dc1/documentation/fabric/dc1_fabric_documentation.md``


    AVD also has the ability to run a series of tests on your network after deployment to verify the current network state

    c. Within the IDE, open the output from: ``/sites/dc1/reports/fabric/dc1_fabric_state.md``

        .. note:: Your example report will include multiple errors. 

|

Lab #3: Summary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Congratulations!**

You deployed new VLANs to DC1 directly through eAPI access to the switches, verified it was deployed successfully, then looked at examples of AVD documentation and reporting.

|


**Lab #4: Adding a pair border leafs to DC1**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In this lab you will edit several YAML files to add a new row to DC1 in order to add a new pair of border leaf switches.

|

#. **Add the new switches to the DC1 inventory file**

    Open the ``/sites/dc1/inventory.yml`` file and uncomment out the lines for ``s1-brdr1`` and ``s1-brdr2``

        .. image:: images/avd_l3_dc/Lab4_inventory.PNG
            :align: center

#. **Edit the DC1 fabric file to add the configuration parameters for the new border leaf switches**

    Open the ``/sites/dc1/dc1_fabric.yml`` file and uncomment out the following lines: 
    
        .. code-block:: text

            79-136
            182-191
            195-204
    
#. **Build and Deploy DC1 using the makefiles**

    Now that the inventory and fabric variables have been set, we need to re-build and redploy DC1.

    a. Build DC1 using the makefile

        .. code-block:: text

            make build_dc1

    b. Deploy DC1 using the makefile 

        .. code-block:: text

            make deploy_dc1_cvp

#. **Verify the DC1 border leaf switches were successfully deployed within Cloudvision**

    a. Go the **Device** view of s1-brdr1 and view the ``Routing -> BGP`` output

        .. note:: You should see s1-brdr1 in the BGP established state with its BGP peers

    b. Go the **Topology** view, create a filter for DC1

            .. code-block:: text

                Container:dc1_fabric

        .. note:: You should see a total of 8 devices now

Lab #4: Summary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Congratulations!**

You successfully added the configurations required for a new border leaf pair to DC1, built and deployed them using makefiles, then verified the changes within Cloudvision
