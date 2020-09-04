Media OSPF Lab
==============

.. image:: images/media-OSPF.png
   :align: center

.. note:: Did you know the OSPF algorithm is considered a link-state protocol, based on the Dijkstra Shortest Path Algorithm? It is a common protocol used in a number of widely deployed environments in various industries.

1. Log into the **LabAccess** jumpserver:

   1. Type ``labs`` at the Main Menu prompt. This will bring up additional lab menu selections.
   2. Type ``media`` at this prompt to open the media lab section (If you were previously in the Media Labs Menu, you can type ``back`` to go back).
   3. Type ``media-ospf`` at the prompt. The script will configure the topology with the exception of **Leaf 4**.

   4. On **Spine 2**, verify OSPF operation (it should not be operating correctly) and you will see all the routes currently in the environment.

        .. code-block:: text

            show ip ospf neighbor
            show ip ospf interface
            show ip ospf database
            show ip route



      **Example:**

         .. code-block:: text

            spine2#show ip ospf neighbor
            Neighbor ID     VRF      Pri State                  Dead Time   Address         Interface
            10.127.255.2    default  1   FULL/BDR               00:00:35    10.127.23.2     Ethernet1

            spine2#show ip ospf interface
            Loopback0 is up
              Interface Address 10.127.255.3/32, VRF default, Area 0.0.0.0
              Network Type Broadcast, Cost: 10
              Transmit Delay is 1 sec, State DR, Priority 1
              Designated Router is 10.127.255.3
              No Backup Designated Router on this network
              Timer intervals configured, Hello 10, Dead 40, Retransmit 5
              Neighbor Count is 0 (Passive Interface)
              No authentication
            Ethernet5 is up
              Interface Address 10.127.34.3/24, VRF default, Area 0.0.0.0
              Network Type Broadcast, Cost: 10
              Transmit Delay is 1 sec, State DR, Priority 1
              Designated Router is 10.127.255.3
              No Backup Designated Router on this network
              Timer intervals configured, Hello 10, Dead 40, Retransmit 5
              Neighbor Count is 0
              No authentication
            Ethernet1 is up
              Interface Address 10.127.23.3/24, VRF default, Area 0.0.0.0
              Network Type Broadcast, Cost: 10
              Transmit Delay is 1 sec, State DR, Priority 1
              Designated Router is 10.127.255.3
              Backup Designated Router is 10.127.255.2
              Timer intervals configured, Hello 10, Dead 40, Retransmit 5
              Neighbor Count is 1
              No authentication

            spine2#show ip ospf database

                        OSPF Router with ID(10.127.255.3) (Process ID 100) (VRF default)


                             Router Link States (Area 0.0.0.0)

            Link ID         ADV Router      Age         Seq#         Checksum Link count
            10.127.255.2    10.127.255.2    344         0x80000007   0x5d3    3
            10.127.255.1    10.127.255.1    346         0x80000006   0x2433   3
            10.127.255.3    10.127.255.3    343         0x80000006   0xbe99   3

                             Network Link States (Area 0.0.0.0)

            Link ID         ADV Router      Age         Seq#         Checksum
            10.127.23.3     10.127.255.3    343         0x80000001   0x836e
            10.127.12.2     10.127.255.2    344         0x80000001   0xf40c

            spine2#show ip route

            VRF: default
            Codes: C - connected, S - static, K - kernel,
                   O - OSPF, IA - OSPF inter area, E1 - OSPF external type 1,
                   E2 - OSPF external type 2, N1 - OSPF NSSA external type 1,
                   N2 - OSPF NSSA external type2, B I - iBGP, B E - eBGP,
                   R - RIP, I L1 - IS-IS level 1, I L2 - IS-IS level 2,
                   O3 - OSPFv3, A B - BGP Aggregate, A O - OSPF Summary,
                   NG - Nexthop Group Static Route, V - VXLAN Control Service,
                   DH - DHCP client installed default route, M - Martian,
                   DP - Dynamic Policy Route

            Gateway of last resort:
             S      0.0.0.0/0 [1/0] via 192.168.0.254, Management1

             O      10.127.12.0/24 [110/20] via 10.127.23.2, Ethernet1
             C      10.127.23.0/24 is directly connected, Ethernet1
             C      10.127.34.0/24 is directly connected, Ethernet5
             O      10.127.255.1/32 [110/30] via 10.127.23.2, Ethernet1
             O      10.127.255.2/32 [110/20] via 10.127.23.2, Ethernet1
             C      10.127.255.3/32 is directly connected, Loopback0
             O      172.16.15.0/24 [110/30] via 10.127.23.2, Ethernet1
             C      192.168.0.0/24 is directly connected, Management1


      All the route entries with a preceding "O" was learned by the OSPF protocol on **Spine 2**.

2. Configure OSPF on the **Leaf 4** switch using the following criteria:

   1. Configure the Ethernet 3, Ethernet 4, Loopback 0 interfaces and the OSPF router process on **Leaf4** to be used for OSPF communication to the adjacent devices (**Spine 2** in this case)

        .. code-block:: text

            configure
            interface loopback 0
              ip address 10.127.255.4/32
            interface ethernet 3
              no switchport
              ip address 10.127.34.4/24
            interface ethernet 4
              no switchport
              ip address 172.16.46.4/24
            router ospf 100
              router-id 10.127.255.4

      **Example:**

         .. code-block:: text

            leaf4#configure
            leaf4(config)#int et 3
            leaf4(config-if-Et3)#no switchport
            leaf4(config-if-Et3)#ip address 10.127.34.4/24
            leaf4(config)#int et 4
            leaf4(config-if-Et4)#no switchport
            leaf4(config-if-Et4)#ip address 172.16.46.4/24
            leaf4(config)#int lo 0
            leaf4(config-if-Lo0)#ip address 10.127.255.4/32
            leaf4(config)#router ospf 100
            leaf4(config-router-ospf)#router-id 10.127.255.4


      .. note::
       All interfaces are point-to-point connections in the OSPF lab, no trunk or access ports

   2. Specify the network statement which encompasses all the interfaces that will take part in the OSPF process.

         .. code-block:: text

            configure
            router ospf 100
               network 10.127.0.0/16 area 0.0.0.0
               network 172.16.46.0/24 area 0.0.0.0

      **Example:**

          .. code-block:: text

            leaf4(config)#configure
            leaf4(config)#router ospf 100
            leaf4(config-router-ospf)#network 10.127.0.0/16 area 0.0.0.0
            leaf4(config-router-ospf)#network 172.16.46.0/24 area 0.0.0.0


      .. note::
        All interfaces which fall into the range of the network statement will take part in the OSPF process and listen for and send out hello packets.

   3. Certain interfaces do not need to take part in the OSPF process but we still want the IP's to be advertised out. This is where we leverage the "passive-interface" setting to allow this.  These interfaces will still be associated in the area in which the network statement is associated to.

        .. code-block:: text

            configure
            router ospf 100
              passive-interface loopback0
              passive-interface ethernet4

      **Example:**

         .. code-block:: text

            leaf4(config)#router ospf 100
            leaf4(config-router-ospf)#passive-interface loopback 0
            leaf4(config-router-ospf)#passive-interface ethernet4


   4. Confirm the OSPF neighbor relationship has been established and the routing table on **Leaf 4** has been populated with the appropriate entries.

        .. code-block:: text

            show ip ospf neighbor
            show ip ospf interface
            show ip ospf database
            show ip route

      **Example**

         .. code-block:: text

            leaf4(config-if-Et4)#show ip ospf neighbor
            Neighbor ID     VRF      Pri State                  Dead Time   Address         Interface
            10.127.255.3    default  1   FULL/DR                00:00:31    10.127.34.3     Ethernet3

            leaf4(config-if-Et4)#show ip ospf interface
            Loopback0 is up
              Interface Address 10.127.255.4/32, VRF default, Area 0.0.0.0
              Network Type Broadcast, Cost: 10
              Transmit Delay is 1 sec, State DR, Priority 1
              Designated Router is 10.127.255.4
              No Backup Designated Router on this network
              Timer intervals configured, Hello 10, Dead 40, Retransmit 5
              Neighbor Count is 0 (Passive Interface)
              No authentication
            Ethernet3 is up
              Interface Address 10.127.34.4/24, VRF default, Area 0.0.0.0
              Network Type Broadcast, Cost: 10
              Transmit Delay is 1 sec, State Backup DR, Priority 1
              Designated Router is 10.127.255.3
              Backup Designated Router is 10.127.255.4
              Timer intervals configured, Hello 10, Dead 40, Retransmit 5
              Neighbor Count is 1
              No authentication
            Ethernet4 is up
              Interface Address 172.16.46.4/24, VRF default, Area 0.0.0.0
              Network Type Broadcast, Cost: 10
              Transmit Delay is 1 sec, State DR, Priority 1
              Designated Router is 10.127.255.4
              No Backup Designated Router on this network
              Timer intervals configured, Hello 10, Dead 40, Retransmit 5
              Neighbor Count is 0
              No authentication

            leaf4(config-if-Et4)#sh ip ospf database

                        OSPF Router with ID(10.127.255.4) (Process ID 100) (VRF default)


                             Router Link States (Area 0.0.0.0)

            Link ID         ADV Router      Age         Seq#         Checksum Link count
            10.127.255.1    10.127.255.1    863         0x80000009   0x1e36   3
            10.127.255.2    10.127.255.2    861         0x8000000a   0xfed6   3
            10.127.255.4    10.127.255.4    339         0x80000007   0xde1f   3
            10.127.255.3    10.127.255.3    1181        0x80000009   0x5e46   3

                            Network Link States (Area 0.0.0.0)

            Link ID         ADV Router      Age         Seq#         Checksum
            10.127.23.3     10.127.255.3    860         0x80000004   0x7d71
            10.127.34.3     10.127.255.3    1181        0x80000001   0x26be
            10.127.12.2     10.127.255.2    861         0x80000004   0xee0f

            leaf4(config-if-Et4)#sh ip route

            VRF: default
            Codes: C - connected, S - static, K - kernel,
                   O - OSPF, IA - OSPF inter area, E1 - OSPF external type 1,
                   E2 - OSPF external type 2, N1 - OSPF NSSA external type 1,
                   N2 - OSPF NSSA external type2, B I - iBGP, B E - eBGP,
                   R - RIP, I L1 - IS-IS level 1, I L2 - IS-IS level 2,
                   O3 - OSPFv3, A B - BGP Aggregate, A O - OSPF Summary,
                   NG - Nexthop Group Static Route, V - VXLAN Control Service,
                   DH - DHCP client installed default route, M - Martian,
                   DP - Dynamic Policy Route

            Gateway of last resort:
             S      0.0.0.0/0 [1/0] via 192.168.0.254, Management1

             O      10.127.12.0/24 [110/30] via 10.127.34.3, Ethernet3
             O      10.127.23.0/24 [110/20] via 10.127.34.3, Ethernet3
             C      10.127.34.0/24 is directly connected, Ethernet3
             O      10.127.255.1/32 [110/40] via 10.127.34.3, Ethernet3
             O      10.127.255.2/32 [110/30] via 10.127.34.3, Ethernet3
             O      10.127.255.3/32 [110/20] via 10.127.34.3, Ethernet3
             C      10.127.255.4/32 is directly connected, Loopback0
             O      172.16.15.0/24 [110/40] via 10.127.34.3, Ethernet3
             C      172.16.46.0/24 is directly connected, Ethernet4
             C      192.168.0.0/24 is directly connected, Management1

      The routing table output should list all routing entries in this topology to ensure connectivity.

3. Validate end-to-end connectivity once OSPF neighbor relationship has been established.

   1. Log into **Host 2** and verify connectivity with **Host 1**.

         .. code-block:: text

            ping 172.16.15.5

      **Example:**

         .. code-block:: text

            host2# ping 172.16.15.5
            PING 172.16.15.5 (172.16.15.5) 72(100) bytes of data.
            80 bytes from 172.16.15.5: icmp_seq=1 ttl=60 time=99.5 ms
            80 bytes from 172.16.15.5: icmp_seq=2 ttl=60 time=102 ms
            80 bytes from 172.16.15.5: icmp_seq=3 ttl=60 time=165 ms
            80 bytes from 172.16.15.5: icmp_seq=4 ttl=60 time=161 ms
            80 bytes from 172.16.15.5: icmp_seq=5 ttl=60 time=158 ms

            --- 172.16.15.5 ping statistics ---
            5 packets transmitted, 5 received, 0% packet loss, time 40ms
            rtt min/avg/max/mdev = 99.508/137.682/165.494/29.858 ms, pipe 5, ipg/ewma 10.149/120.314 ms


      If OSPF settings have been configured correctly and the routing table on **Leaf 4** has converged then **Host 1** should be reachable from **Host 2**.

.. admonition:: **Test your knowledge:**

    When inspecting the routing table on **Leaf 4**, why are all the infrastructure IP address in there? What are the positive and negative results of that?


**LAB COMPLETE!**

.. admonition:: **Helpful Commands:**

    During the lab you can use the different commands to verify connectivity and behaviour for validation and troubleshooting purposes:

   - show ip ospf neighbor
   - show ip ospf interface
   - show ip ospf database
   - show ip route
