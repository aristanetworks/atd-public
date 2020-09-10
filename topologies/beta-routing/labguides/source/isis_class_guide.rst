IS-IS Class Guide
=====================

.. image:: images/IS-IS_Topology_Image.png
   :align: center

Lab 1: Configure IS-IS as a Single Flood Domain
==========================================================

  .. image:: images/IS-IS_Lab1_and_Lab2.png
    :align: center

.. note:: IP addressing is already configured for all labs.
  
Prep:
----------

  #. On lab jumphost, type ‘labs’ to get to the ‘Additional Labs’ menu

  #. Type ‘isis-lab-guide’ in order to get to the ISIS Lab Guide labs

  #. Type ‘lab1’ in this menu in order to begin deploying configurations for this lab.
  
  #. Wait until you are prompted that the lab deployment is complete. This will take some time.

Tasks:
---------

  #. Configure EOS1 to EOS6 links to be in a single area and flood domain.

    #. Enable ipv4 routing
    
    #. Use area “0000”
    
    #. Use IS-IS Instance name of “1”
    
    #. Match the system-id of each device to the name of the device (Eg. EOS1’s last system-id hextet will be “0001” and EOS6’s will be “0006”)
    
    #. Advertise all loopbacks
    
    #. Ensure there are no pseudonodes in the environment

  #. All intermediate systems should have all routes from other intermediate systems
  
  #. All intermediate system loopbacks should be able to reach each other
  
  #. Look at the isis database details
  
    #. Are there any pseudonodes? If so, why?
    #. Are there multiple link state databases? If so, why?
    #. Make note of reachability information. What types of reachability are being advertised?
  
  #. Look at the routing table and make a note of what it looks like currently
    
    #. How many routes are there in the ‘show ip route summary?’



Lab 2: Loopback Only Advertisements in LSPs
==========================================================

  .. image:: images/IS-IS_Lab1_and_Lab2.png
    :align: center

Prep:
----------

  .. note:: If you are continuing from Lab 1, you can skip these steps and go directly to “Tasks.”

  #. On lab jumphost, type ‘labs’ to get to the ‘Additional Labs’ menu

  #. Type ‘isis-lab-guide’ in order to get to the IS-IS Lab Guide labs

  #. Type ‘lab2’ in this menu in order to begin deploying configurations for this lab.
  
  #. Wait until you are prompted that the lab deployment is complete. This will take some time.

Tasks:
---------

  #. Configure IS-IS on  EOS1 to EOS6 so that only loopback reachability is advertised in LSPs
    
    #. Route maps should not be used
  
  #. All intermediate systems should have only loopback routes from other intermediate systems
  
  #. All intermediate system loopbacks should be able to reach each other
  
  #. Look at the IS-IS database details
    
    #. Make note of reachability information. What types of reachability are being advertised?
    
    #. How did this change from the last section?

  #. Look at the routing table and make a note of what it looks like currently

    #. How many routes are there in the ‘show ip route summary?’

    #. How did the routing table change from the last section?


Lab 3: Broadcast Network
==========================================================

  .. image:: images/IS-IS_Lab3.png
    :align: center

Prep:
----------

  .. note:: If you are continuing from Lab 2, you can skip these steps and go directly to “Tasks.”

  #. On lab jumphost, type ‘labs’ to get to the ‘Additional Labs’ menu

  #. Type ‘isis-lab-guide’ in order to get to the ISIS Lab Guide labs

  #. Type ‘lab3’ in this menu in order to begin deploying configurations for this lab.
  
  #. Wait until you are prompted that the lab deployment is complete. This will take some time.

Tasks:
---------
  
  #. Configure IS-IS between EOS11, EOS12, and EOS13 using VLAN 100

    #. Enable ipv4 routing

    #. Use area “0000”

    #. Use ISIS Instance name of “1”

    #. Continue using a single flood domain

    #. Match the system-id of each device to the name of the device (Eg. EOS11’s last system-id hextet will be “0011” and EOS13’s will be “0013”)
  
  #. Advertise loopbacks into IS-IS
  
  #. Only loopbacks should be advertised into the global routing table.
  
  #. Look at IS-IS neighbors

    #. How many adjacencies do you have per device?

  #. Look at the IS-IS database

    #. How does the IS-IS Database differ on the broadcast network?

    #. Are there any pseudonodes?

    #. If yes: How can you distinguish the pseudonode from other adjacencies?


Appendix A: Configurations
==========================================================

Lab 1: Configure IS-IS as a Single Flood Domain
------------------------------------------------------

**EOS1:**

    .. code-block:: html

      ip routing
      !
      interface Ethernet1
        isis enable 1
        isis circuit-type level-2
        isis network point-to-point
      !
      interface Ethernet4
        isis enable 1
        isis circuit-type level-2
        isis network point-to-point
      !
      interface Ethernet5
        isis enable 1
        isis circuit-type level-2
        isis network point-to-point
      !
      interface Loopback0
        isis enable 1
      !
      router isis 1
        net 49.0000.0000.0000.0001.00
        is-type level-2
        address-family ipv4 unicast

**EOS2:**

    .. code-block:: html

      ip routing
      !
      interface Ethernet1
        isis enable 1
        isis circuit-type level-2
        isis network point-to-point
      !
      interface Ethernet2
        isis enable 1
        isis circuit-type level-2
        isis network point-to-point
      !
      interface Ethernet3
        isis enable 1
        isis circuit-type level-2
        isis network point-to-point
      !
      interface Ethernet4
        isis enable 1
        isis circuit-type level-2
        isis network point-to-point
      !
      interface Ethernet5
        isis enable 1
        isis circuit-type level-2
        isis network point-to-point
      !
      interface Loopback0
        isis enable 1
      !
      router isis 1
        net 49.0000.0000.0000.0002.00
        is-type level-2
        address-family ipv4 unicast

**EOS3:**

    .. code-block:: html

      ip routing
      !
      interface Ethernet3
        isis enable 1
        isis circuit-type level-2
        isis network point-to-point
      !
      interface Ethernet4
        isis enable 1
        isis circuit-type level-2
        isis network point-to-point
      !
      interface Ethernet5
        isis enable 1
        isis circuit-type level-2
        isis network point-to-point
      !
      interface Loopback0
        isis enable 1
      !
      router isis 1
        net 49.0000.0000.0000.0003.00
        is-type level-2
        address-family ipv4 unicast

**EOS4:**

    .. code-block:: html

      ip routing
      !
      interface Ethernet3
        isis enable 1
        isis circuit-type level-2
        isis network point-to-point
      !
      interface Ethernet4
        isis enable 1
        isis circuit-type level-2
        isis network point-to-point
      !
      interface Ethernet5
        isis enable 1
        isis circuit-type level-2
        isis network point-to-point
      !
      interface Loopback0
        isis enable 1
      !
      router isis 1
        net 49.0000.0000.0000.0004.00
        is-type level-2
        address-family ipv4 unicast

**EOS5:**

    .. code-block:: html

      ip routing
      !
      interface Ethernet1
        isis enable 1
        isis circuit-type level-2
        isis network point-to-point
      !
      interface Ethernet2
        isis enable 1
        isis circuit-type level-2
        isis network point-to-point
      !
      interface Ethernet3
        isis enable 1
        isis circuit-type level-2
        isis network point-to-point
      !
      interface Ethernet4
        isis enable 1
        isis circuit-type level-2
        isis network point-to-point
      !
      interface Ethernet5
        isis enable 1
        isis circuit-type level-2
        isis network point-to-point
      !
      interface Loopback0
        isis enable 1
      !
      router isis 1
        net 49.0000.0000.0000.0005.00
        is-type level-2
        address-family ipv4 unicast

**EOS6:**

    .. code-block:: html

      ip routing
      !
      interface Ethernet1
        isis enable 1
        isis circuit-type level-2
        isis network point-to-point
      !
      interface Ethernet4
        isis enable 1
        isis circuit-type level-2
        isis network point-to-point
      !
      interface Ethernet5
        isis enable 1
        isis circuit-type level-2
        isis network point-to-point
      !
      interface Loopback0
        isis enable 1
      !
      router isis 1
        net 49.0000.0000.0000.0006.00
        is-type level-2
        address-family ipv4 unicast

Lab 2: Loopback Only Advertisements in LSPs
------------------------------------------------------

**All Nodes (EOS1 to EOS6):**

    .. code-block:: html

      interface Loopback0
        isis passive
      !
      router isis 1
        advertise passive-only

Lab 3: Broadcast Network
-----------------------------

**EOS11:**

    .. code-block:: html
      
      ip routing
      !
      interface Loopback0
        isis enable 1
        isis passive
      !
      interface vlan100
        isis enable 1
        isis circuit-type level-2
      !
      router isis 1
        net 49.0000.0000.0000.0011.00
        is-type level-2
        advertise passive-only
        address-family ipv4 unicast

**EOS12:**

    .. code-block:: html
      
      ip routing
      !
      interface Loopback0
        isis enable 1
        isis passive
      !
      interface vlan100
        isis enable 1
        isis circuit-type level-2
      !
      router isis 1
        net 49.0000.0000.0000.0012.00
        is-type level-2
        advertise passive-only
        address-family ipv4 unicast

**EOS13:**

    .. code-block:: html

      ip routing
      !
      interface Loopback0
        isis enable 1
        isis passive
      !
      interface vlan100
        isis enable 1
        isis circuit-type level-2
      !
      router isis 1
        net 49.0000.0000.0000.0013.00
        is-type level-2
        advertise passive-only
        address-family ipv4 unicast
   
