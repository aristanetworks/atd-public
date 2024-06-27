Layer 3 Leaf-Spine with OSPF
============================

..
   NOTE TO THE EDITOR OF THIS LAB GUIDE FOR DUAL DC!!!! I REMOVED THE VLANs CONFIGLET SO YOU NEED TO ADD A STEP TO CREATE VLAN 34

.. thumbnail:: images/l3ls-ospf/nested_l3ls-ospf_topo_1.png
   :align: center

      Click image to enlarge

.. note:: The manually-entered commands below that are part of this lab are
          equivalent to ``L3LS-OSPF_s1-leaf4_complete``.


1. Log into the **LabAccess** jumpserver:

   a. Type ``l3ls-ospf`` at the prompt. The script will configure the datacenter with the exception of **s1-leaf4**.

      .. note::
         Did you know the “l3ls-ospf” script is composed of Python code that
         uses the CloudVision Portal REST API to automate the provisioning of
         CVP Configlets. The configlets that are configured via the REST API
         are ``L3LS-OSPF_s1-spine1``, ``L3LS-OSPF_s1-spine2``, ``L3LS-OSPF_s1-leaf1``,
         ``L3LS-OSPF_s1-leaf2``, ``L3LS-OSPF_s1-leaf3``, ``L3LS-OSPF_s1-leaf4``.

#. Configure SVI and VARP Virtual IP on the **s1-leaf4** switch using the following criteria

   a. Create the vARP MAC Address in Global Configuration mode
   
      .. note::

         Arista EOS utilizes the Industry-Standard CLI. When entering configuration commands, be 
         sure to first type ``configure`` to enter configuration mode.

      .. code-block:: text

         ip virtual-router mac-address 00:1c:73:00:00:34

   #. Create the VLAN, SVI and the Virtual Router Address

      .. code-block:: text

         vlan 134
            name Host_Network_134
         !
         interface vlan 134
            ip address 10.111.134.3/24
            ip virtual-router address 10.111.134.1

   #. Validate the configuration with the following:

      .. code-block:: text
         :emphasize-lines: 1,9

         s1-leaf4#show ip interface brief 
                                                                                        Address
         Interface         IP Address            Status       Protocol           MTU    Owner  
         ----------------- --------------------- ------------ -------------- ---------- -------
         Management0       192.168.0.15/24       up           up                1500           
         Vlan134           10.111.134.3/24       up           up                1500           
         Vlan4094          10.255.255.2/30       up           up                1500           

         s1-leaf4#show ip virtual-router
         IP virtual router is configured with MAC address: 001c.7300.0034
         IP virtual router address subnet routes not enabled
         MAC address advertisement interval: 30 seconds

         Protocol: U - Up, D - Down, T - Testing, UN - Unknown
                  NP - Not Present, LLD - Lower Layer Down

         Interface       Vrf           Virtual IP Address       Protocol       State 
         --------------- ------------- ------------------------ -------------- ------
         Vl134           default       10.111.134.1             U              active

#. Configure OSPF on the **s1-leaf4** switch using the following criteria

   a. Based on the diagram, configure L3 interfaces to **s1-spine1/s1-spine2** and interface Loopback0

      .. code-block:: text

         interface Ethernet2
            description L3 Uplink - s1-spine1
            no switchport
            ip address 10.111.1.7/31
         !
         interface Ethernet3
            description L3 Uplink - s1-spine2
            no switchport
            ip address 10.111.2.7/31
         !
         interface Loopback0
            description Management and Router-id
            ip address 10.111.254.4/32

   #. Validate the configuration with the following:

      .. code-block:: text
         :emphasize-lines: 1
         
         s1-leaf4#show ip interface brief
                                                                                       Address
         Interface         IP Address            Status       Protocol            MTU    Owner  
         ----------------- --------------------- ------------ -------------- ----------- -------
         Ethernet2         10.111.1.7/31         up           up                 1500           
         Ethernet3         10.111.2.7/31         up           up                 1500           
         Loopback0         10.111.254.4/32       up           up                65535           
         Management0       192.168.0.15/24       up           up                 1500           
         Vlan134           10.111.134.3/24       up           up                 1500           
         Vlan4094          10.255.255.2/30       up           up                 1500           

   #. Based on the diagram, enable OSPF and configure the interfaces
      on **s1-leaf4**. Connections to **s1-spine1/s1-spine2** and **s1-leaf3** with be part of Area 0.
      
      .. note:: 
         In EOS, process-level configuration happens with the OSPF context and peer-specific
         configuration such as Area and Authentication happen under the interface.

      .. code-block:: text

         interface Ethernet2
            ip ospf area 0.0.0.0
            ip ospf network point-to-point
         !
         interface Ethernet3
            ip ospf area 0.0.0.0
            ip ospf network point-to-point
         !
         interface Vlan4094
            ip ospf area 0.0.0.0
            ip ospf network point-to-point
         !
         router ospf 100
            router-id 10.111.254.4
      
      .. note:: 
         We are leveraging OSPF Point-to-Point networks to eliminate the need for DR elections
         on non-broadcast networks.

   #. Validate the configuration and process status.

      .. code-block:: text
         :emphasize-lines: 1,5,18

         s1-leaf4(config-router-ospf)#show active 
         router ospf 100
            router-id 10.111.254.4
            max-lsa 12000
         s1-leaf4(config-router-ospf)#show run interfaces Ethernet 2-3
         interface Ethernet2
            description L3 Uplink - s1-spine1
            no switchport
            ip address 10.111.1.7/31
            ip ospf area 0.0.0.0
            ip ospf network point-to-point
         interface Ethernet3
            description L3 Uplink - s1-spine2
            no switchport
            ip address 10.111.2.7/31
            ip ospf area 0.0.0.0
            ip ospf network point-to-point
         s1-leaf4(config-router-ospf)#show ip ospf summary 
         OSPF instance 100 with ID 10.111.254.4, VRF default
         Time since last SPF: 122 s
         Max LSAs: 12000, Total LSAs: 1
         Type-5 Ext LSAs: 0
         ID               Type   Intf   Nbrs (full) RTR LSA NW LSA  SUM LSA ASBR LSA TYPE-7 LSA
         0.0.0.0          normal 3      0    (0   ) 1       0       0       0       0    

#. Enable OSPF Authentication on **s1-leaf4** to peer to **s1-spine1/s1-spine2** and **s1-leaf3**

   a. Add the following Authentication commands to OSPF Interfaces on **s1-leaf4**:

      .. code-block:: text

         interface Ethernet2
            ip ospf authentication message-digest
            ip ospf message-digest-key 1 sha512 Arista123!
         !
         interface Ethernet3
            ip ospf authentication message-digest
            ip ospf message-digest-key 1 sha512 Arista123!
         !
         interface Vlan4094
            ip ospf authentication message-digest
            ip ospf message-digest-key 1 sha512 Arista123!

   #. Verify that peering is established to directly connected neighbors.

      .. code-block:: text
         :emphasize-lines: 1

         s1-leaf4(config-if-Vl4094)#show ip ospf neighbor
         Neighbor ID     Instance VRF      Pri State                  Dead Time   Address         Interface
         10.111.0.1      100      default  0   FULL                   00:00:38    10.111.1.6      Ethernet2
         10.111.0.2      100      default  0   FULL                   00:00:37    10.111.2.6      Ethernet3
         10.111.254.3    100      default  1   FULL                   00:00:31    10.255.255.1    Vlan4094

   #. Enable OSPF Advertisement of local networks on **s1-leaf4**.

      .. code-block:: text

         interface Loopback0
            ip ospf area 0.0.0.0
         !
         interface Vlan134
            ip ospf area 0.0.0.0

   #. However, we do not want to form OSPF adjacencies on these interfaces, so enable passive-interface functionality on **s1-leaf4**.

      .. code-block:: text

         router ospf 100
            passive-interface default
            no passive-interface Ethernet2
            no passive-interface Ethernet3
            no passive-interface Vlan4094

   #. Check the OSPF Database and IP route tables on **s1-leaf4** as well as each of the **Spines** and **Leafs**

      .. code-block:: text
         :emphasize-lines: 1,14,26,69,70,73,90

            s1-leaf4#show ip ospf database 
            
                        OSPF Router with ID(10.111.254.4) (Instance ID 100) (VRF default)
            
            
                             Router Link States (Area 0.0.0.0)
            
            Link ID         ADV Router      Age         Seq#         Checksum Link count
            10.111.0.2      10.111.0.2      356         0x80000011   0x4670   6
            10.111.0.1      10.111.0.1      355         0x80000011   0x3be    6
            10.111.254.3    10.111.254.3    358         0x80000013   0x691    6
            10.111.254.2    10.111.254.2    1198        0x8000000f   0x58f3   5
            10.111.254.4    10.111.254.4    354         0x80000018   0x3b28   8
            10.111.254.1    10.111.254.1    1198        0x8000000f   0x5ff8   5
            
                             Network Link States (Area 0.0.0.0)
            
            Link ID         ADV Router      Age         Seq#         Checksum
            10.255.255.2    10.111.254.2    3600        0x80000116   0x6448  
            10.111.2.3      10.111.254.2    1198        0x80000002   0x5ded  
            10.111.2.1      10.111.254.1    1198        0x80000002   0x6de1  
            10.111.2.5      10.111.254.3    1198        0x80000002   0x4df9  
            10.111.1.1      10.111.254.1    1198        0x80000002   0x6ae6  
            10.111.1.5      10.111.254.3    1198        0x80000002   0x4afe  
            10.111.1.3      10.111.254.2    1198        0x80000002   0x5af2  
            s1-leaf4#show ip ospf database detail 10.111.254.1
            
                        OSPF Router with ID(10.111.254.4) (Instance ID 100) (VRF default)
            
              LS Age: 1294
              Options: (E DC)
              LS Type: Router Links
              Link State ID: 10.111.254.1
              Advertising Router: 10.111.254.1
              LS Seq Number: 0x8000000f
              Checksum: 0x5ff8
              Length: 84
              Number of Links: 5
            
                Link connected to: a Transit Network
                 (Link ID) Designated Router address: 10.111.1.1
                 (Link Data) Router Interface address: 10.111.1.1
                  Number of TOS metrics: 0
                   TOS 0 Metrics: 10
            
            
                Link connected to: a Stub Network
                 (Link ID) Network/subnet number: 10.111.254.1
                 (Link Data) Network Mask: 255.255.255.255
                  Number of TOS metrics: 0
                   TOS 0 Metrics: 10
            
            
                Link connected to: a Transit Network
                 (Link ID) Designated Router address: 10.111.2.1
                 (Link Data) Router Interface address: 10.111.2.1
                  Number of TOS metrics: 0
                   TOS 0 Metrics: 10
            
            
                Link connected to: a Transit Network
                 (Link ID) Designated Router address: 10.255.255.2
                 (Link Data) Router Interface address: 10.255.255.1
                  Number of TOS metrics: 0
                   TOS 0 Metrics: 10
            
            
                Link connected to: a Stub Network
                 (Link ID) Network/subnet number: 10.111.112.0
                 (Link Data) Network Mask: 255.255.255.0
                  Number of TOS metrics: 0
                   TOS 0 Metrics: 10
            s1-leaf4#show ip route 10.111.112.0/24
            
            VRF: default
            Source Codes:
                   C - connected, S - static, K - kernel,
                   O - OSPF, IA - OSPF inter area, E1 - OSPF external type 1,
                   E2 - OSPF external type 2, N1 - OSPF NSSA external type 1,
                   N2 - OSPF NSSA external type2, B - Other BGP Routes,
                   B I - iBGP, B E - eBGP, R - RIP, I L1 - IS-IS level 1,
                   I L2 - IS-IS level 2, O3 - OSPFv3, A B - BGP Aggregate,
                   A O - OSPF Summary, NG - Nexthop Group Static Route,
                   V - VXLAN Control Service, M - Martian,
                   DH - DHCP client installed default route,
                   DP - Dynamic Policy Route, L - VRF Leaked,
                   G  - gRIBI, RC - Route Cache Route,
                   CL - CBF Leaked Route
            
             O        10.111.112.0/24 [110/30]
                       via 10.111.1.6, Ethernet2
                       via 10.111.2.6, Ethernet3

      .. note:: ECMP is automatically enabled in OSPF as it is an IGP.

#. Validate connectivity from **s1-host1** to **s1-host2**. From **s1-host1** execute:

   .. code-block:: text

      ping 10.111.134.202
      traceroute 10.111.134.202

   a. Verify **s1-leaf4**'s IP address is in the traceroute path, either interface 10.111.1.7 via **s1-spine1** or interface 10.111.2.7 via **s1-spine2**.
      If traffic is hashing via **s1-leaf3**'s 10.111.1.5 or 10.111.2.5 interfaces perform the optional ``shutdown`` steps below on **s1-leaf3**

      .. code-block:: text

         interface Ethernet2-3
            shutdown

   #. Rerun traceroute/verification from **s1-host1** to **s1-host2** then revert the ``shutdown`` changes on **s1-leaf3**

      .. code-block:: text

         interface Ethernet2-3
            no shutdown

#. Other OSPF features to play with if you have time:

   a. Route Redistribution: For fun, do a ``watch 1 diff show ip route | begin
      Gateway`` on **s1-leaf1** and let that run while you execute the
      following commands on **s1-leaf4**. You will see the new route being
      injected into the route table of **s1-leaf1**.

      .. code-block:: text

         ip route 0.0.0.0/0 Null0
         !
         router ospf 100
            redistribute static

   #. BFD: BFD is a low-overhead, protocol-independent mechanism which adjacent
      systems can use instead for faster detection of faults in the path between
      them. BFD is a simple mechanism which detects the liveness of a connection
      between adjacent systems, allowing it to quickly detect failure of any
      element in the connection. Note that BFD is not running on the other devices 
      so the BFD neighbor will not come up until you configure it on multiple devices.

      .. code-block:: text

         router ospf 100
            bfd default

#. Troubleshooting BGP:

   .. code-block:: text

      show ip ospf summary
      show ip ospf
      show ip ospf neighbor <neighbor_ip>
      show run section ospf
      show log

**LAB COMPLETE!**
