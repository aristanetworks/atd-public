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
    Open a terminal by clicking on the top left icon > Terminal > New Terminal, or by pressing ``CTRL+Shift+` ``
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

Lab #1: Building and Deploying DC1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In this lab you will configure DC1 using AVD and then deploy DC1 using CloudVision

|

#. **Open Cloudvision from your initial Lab page**

    .. warning:: Cloudvision can take 10-15 minutes to boot after initial lab deployment

    .. image:: images/avd_l3_dc/Lab1_Open_CVP.PNG
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

    Now that the configurations have been created, we will deploy them using Cloudvision

    Run the following command:

    .. code-block:: text

        make deploy_dc1_cvp

    If the playbook ran successfully, you should see output similar to the following:

#. **Return to Cloudvision**

    a. Go the **Device** view of S1-Leaf1 and view ``Routing -> BGP`` output

        .. note:: S1-Leaf1 should now have several BGP peers in the Established statement
    
    b. Go the **Topology** view, you will need to create a new filter because AVD created new containers for the DC1 devices

            .. code-block:: text

                container: FILL IN LATER

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

***END OF LAB 1***
------------


|
|
|
|

Lab #2: Building and Deploying DC2 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In this lab you will configure DC2 using AVD and then deploy DC2 using CloudVision while going through the normal change control process

|

#. **Set the Ansible password for DC2**

    |

    Once again, we are going to add your lab password: ``{REPLACE_PWD}`` to the ``dc2.yml`` file 

    a. Open the ``sites/dc2/group_vars/dc2.yml`` file 

    b. Edit the ``ansible_password:`` field with your lab password: ``{REPLACE_PWD}`` 

#. **Build DC2 using the makefile**

    |

    Run the following command:

    .. code-block:: text

        make build_dc2

    This time, there will be errors when trying to build the DC2 configs

        .. image:: images/avd_l3_dc/Lab2_inventory_failure.PNG
            :align: center

    These errors are the result of the IP addresses for Leafs 1-4 being incorrect in the DC2 inventory file

#. **Correct the errors in the DC2 inventory.yml file**

    |

    Open the ``sites/dc2/inventory.yml`` file, and edit the IP addresses for Leafs1-4 to the following:

    .. code-block:: text

        s2-leaf1:   192.168.0.22
        s2-leaf2:   192.168.0.23
        s2-leaf3:   192.168.0.24
        s2-leaf4:   192.168.0.25

    .. image:: images/avd_l3_dc/Lab2_inventory_failure.PNG
        :align: center

#. **Re-build DC2 using the makefile**

    |

    Run the following command:

    .. code-block:: text

        make build_dc2

    There should be no errors building the DC2 config this time.

#. **Deploy DC2 using the makefile**

    |

    We are going to deploy DC2 using Cloudvision similar to how we deployed DC1, but this time we will also go through the full change control process within Cloudvision.

    Run the following command:

    .. code-block:: text

        make deploy_dc2_cvp

    The command executed successfully, but we need to go through the change control process within Cloudvision to deploy the change.

#. **Create, approve, and execute the change within Cloudvision**

    |

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

    |

    a. Go the **Device** view of S1-Leaf2 and view ``Routing -> BGP`` output

        .. note:: S1-Leaf1 should have several BGP peers in the Established state
    
    b. Go the **Topology** view, create a new filter for DC2

            .. code-block:: text

                container: FILL IN LATER

Lab #2: Summary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Congratulations!**

You built DC2, fixed errors with the DC2 Ansible inventory file, went through a full Cloudvision change control, and verified it was deployed successfully. 

|


Lab #3: Adding new VLANs to DC1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In this lab you will add new VLANs to DC1, and then get familiar with the AVD ``Validate State`` feature


