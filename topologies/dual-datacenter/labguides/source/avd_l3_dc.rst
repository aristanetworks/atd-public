AVD L3 DC Labs
===================
The goal of these labs are to demonstrate how to use AVD to deploy and configure EVPN/VXLAN Datacenter networks.
|

#. Connect to the Programmability IDE
    Connect to the **Programmability IDE** service. This IDE is running VS Code. If prompted for a password, enter in your
    lab password: ``{REPLACE_PWD}``.

        .. image:: images/avd_l3_dc/Setup_ProgrammabilityIDE.png
            :align: center
        |

#. Change directory to the AVD_L3_DC folder
    Change your working directory to ``avd_l3_dc``

    .. code-block:: text

        cd labfiles/avd_l3_dc


#. Set the Ansible password for DC1
    We are going to add your lab password: ``{REPLACE_PWD}`` to the ``dc1.yml`` file 

    a. Open the ``sites/dc1/group_vars/dc1.yml`` file 

    .. thumbnail:: images/avd_l3_dc/Setup_Select_DC1yml.PNG
        :align: center
    |


    b. Edit the ``ansible_password:`` field with your lab password: ``{REPLACE_PWD}`` 

    .. image:: images/avd_l3_dc/Setup_DC1_Password.PNG
        :align: center


|

Lab #1: Building and Deploying DC1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In this lab you will configure DC1 using AVD and then deploy DC1 using CloudVision
|

#. Open Cloudvision from your initial Lab page

    .. warning:: Cloudvision can take 10-15 minutes to boot after initial lab deployment

    .. image:: images/avd_l3_dc/Lab1_Open_CVP.PNG
        :align: center



#. Open the topology view and filter based on tags for DC1 

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

        .. note:: The current topology view will be very basic due to DC1 being undeployed


#. Open the device view and look at S1-Leaf1

    a. Select ``Configuration`` and look at the current running config 

        .. note:: S1-Leaf1 currently contains only a basic minimal configuration. Enough to allow Ansible to login and push a full configuration.
    
    b. Select ``Routing -> BGP`` and look and verify there are no BGP peers 



#. Return to your  ``Programmability IDE``

    You will build and then deploy the entirety of DC1 using a makefile 

    .. note:: The makefile contains recipes to allow you to run the lab playbooks using a simple command syntax

#. Build DC1 using the makefile 

    .. code-block:: text

        make build_dc1

    .. note:: Make sure your terminal working directory is within the AVD_L3_DC folder



    If the playbook ran successfully, you should see output similar to the following:

        .. code-block:: text

            PLAY RECAP ***************************************************************************************************************************
            s1-leaf1                   : ok=5    changed=3    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0   
            s1-leaf2                   : ok=5    changed=3    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0   
            s1-leaf3                   : ok=5    changed=3    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0   
            s1-leaf4                   : ok=5    changed=3    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0   
            s1-spine1                  : ok=13   changed=8    unreachable=0    failed=0    skipped=2    rescued=0    ignored=0   
            s1-spine2                  : ok=5    changed=3    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0   




#. Return to Cloudvision

    a. Go the ``Device`` view of S1-Leaf1 and view ``Routing -> BGP`` output
        .. note:: S1-Leaf1 should now have several BGP peers in the Established statement
    
    b. Go the ``Topology`` view, re-apply the DC1 filter
        .. note:: Now that DC1 is configured, you should see correct tree structure for DC1

        .. image:: images/avd_l3_dc/Lab1_Topology_after.PNG
            :align: center




Lab #1: Summary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Congratulations, you have now deployed an entire datacenter simply by running the ``make build_dc1`` command. This is the power automation can bring you. 





Lab #2: Building and Deploying DC2 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

