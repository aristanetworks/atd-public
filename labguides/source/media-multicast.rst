Advanced Networking for Media Engineers
=======================================

.. image:: images/media_mcast_01.png
   :align: center

.. note:: To simplify the training using our multicast topology, this exercise will disable Leaf2 and Leaf3.  We will be using CloudVision Portal (CVP) to deploy configlets to configure this topology.  This lab is a continuation of the concepts from the previous Broadcast Engineer Labs

1. Log into the **LabAccess** jumpserver:
    1. Type ``multicast`` or option ``18`` at the prompt. The script will pre-configure the topology with the exception of Leaf4 and Hosts 1 & 2

2. Create Vlan 66 & SVI for host access vlan on **Leaf 4**.

    1. On **Leaf 4** we will create an SVI

        .. code-block:: text

            interface Vlan66
               no autostate
               ip address 172.16.66.1./24

3. Create connectivity for Host 2 on Leaf 4

    1.  On Leaf 4, interface Ethernet 5 is attached to Host 2, associate the port as access vlan 66.

        .. code-block:: text

            interface Ethernet5
               switchport access vlan 66

4. Create uplink connectivity to Spine 2

    1.  On Leaf 4, Ethernet 3 is connected to Spine 2. Create a routed port for uplink access

        .. code-block:: text

           interface Ethernet3
              no switchport
              ip address 172.16.200.26/30

5.  Enable OSPF & verify connectivity

    1.  On Leaf 4, create a loopback interface & assign an IP to be used as the Router-ID. On Leaf 3, enable the OSPF routing process and assign the networks to be advertised

        .. code-block:: text

            interface Loopback0
               ip address 172.16.0.5/32
            !
            router ospf 6500
               router-id 172.16.0.5
               passive-interface Loopback0
               passive-interface Vlan66
               network 172.16.0.0/24 area 0.0.0.0
               network 172.16.66.0/24 area 0.0.0.0
               network 172.16.200.24/30 area 0.0.0.0
               max-lsa 12000

    2. Issue a ``show ip route`` command on Leaf 1.  Output should show the following networks from Leaf 4 being advertised and shows a Full/BR state with Leaf 4, its neighbor.

        .. code-block:: text

            What would you like to do? 3
            leaf1>ena
            leaf1#show ip route

            VRF: default
            Codes: C - connected, S - static, K - kernel,
                   O - OSPF, IA - OSPF inter area, E1 - OSPF external type 1,
                   E2 - OSPF external type 2, N1 - OSPF NSSA external type 1,
                   N2 - OSPF NSSA external type2, B I - iBGP, B E - eBGP,
                   R - RIP, I L1 - IS-IS level 1, I L2 - IS-IS level 2,
                   O3 - OSPFv3, A B - BGP Aggregate, A O - OSPF Summary,
                   NG - Nexthop Group Static Route, V - VXLAN Control Service,
                   DH - Dhcp client installed default route

            Gateway of last resort:
            S      0.0.0.0/0 [1/0] via 192.168.0.254, Management1

            O      172.16.0.1/32 [110/20] via 172.16.200.1, Ethernet2
            O      172.16.0.2/32 [110/30] via 172.16.200.1, Ethernet2
            C      172.16.0.3/32 is directly connected, Loopback0
            O      172.16.0.5/32 [110/40] via 172.16.200.1, Ethernet2
            O      172.16.11.0/30 [110/20] via 172.16.200.1, Ethernet2
            C      172.16.55.0/24 is directly connected, Vlan55
            O      172.16.66.0/24 [110/40] via 172.16.200.1, Ethernet2
            C      172.16.200.0/30 is directly connected, Ethernet2
            O      172.16.200.24/30 [110/30] via 172.16.200.1, Ethernet2
            C      192.168.0.0/24 is directly connected, Management1

            leaf1#show ip ospf neighbor
            Neighbor ID     VRF      Pri State                  Dead Time   Address         Interface
            172.16.0.1      default  1   FULL/BDR               00:00:32    172.16.200.1    Ethernet2
            leaf1#


6. Prepare Connectivity on Host 1 & Host 2

    1. On Host 1, we will need to setup a default route for the host to communicate. On Host 1 type the following commands to prepare the host

    .. code-block:: text


        host1(config)#no ip route 0.0.0.0/0 172.16.115.1
        host1(config)#ip route 0.0.0.0/0 172.16.55.1
        host1(config)#interface ethernet 3
        host1(config-if-Et3)#no switchport
        host1(config-if-Et3)#ip address 172.16.55.2/24
        host1(config-if-Et3)#show ip route



    2. On Host 2, we will need to setup a default route for the host to communicate. On Host 2 type the following commands to prepare the host

        .. code-block:: text

            host2(config)#no ip route 0.0.0.0/0 172.16.115.1
            host2(config)#ip route 0.0.0.0/0 172.16.66.1
            host2(config)#interface ethernet 4
            host2(config-if-Et4)#no switchport
            host2(config-if-Et4)#ip address 172.16.66.2/24
            host2(config-if-Et4)#show ip route

    3.	Issue a ping command from host2 in network 172.16.66.0/24 to host 1 on 172.16.55.0/2

        .. code-block:: text

            What would you like to do? 7
            host2>enable
            host2# ping 172.16.55.2
            PING 172.16.55.2 (172.16.55.2) 72(100) bytes of data.
            80 bytes from 172.16.55.2: icmp_seq=1 ttl=60 time=189 ms
            80 bytes from 172.16.55.2: icmp_seq=2 ttl=60 time=185 ms
            80 bytes from 172.16.55.2: icmp_seq=3 ttl=60 time=184 ms
            80 bytes from 172.16.55.2: icmp_seq=4 ttl=60 time=210 ms
            80 bytes from 172.16.55.2: icmp_seq=5 ttl=60 time=209 ms

            --- 172.16.55.2 ping statistics ---
            5 packets transmitted, 5 received, 0% packet loss, time 43ms
            rtt min/avg/max/mdev = 184.314/196.045/210.805/11.583 ms, pipe 5, ipg/ewma 10.761/193.725 ms

7.	Enable Multicast

    1.  On Leaf 4, enable multicast routing using the following commands;  We will be enabling multicast routing on Leaf 4 and assigning the interfaces to participate in multicast routing.  As well we will define the RP address on the switch.

        .. code-block:: text

        .. code-block:: text

            ip multicast-routing
            !
            ip pim rp-address 172.16.0.3
            !
            interface Vlan66
               ip pim sparse-mode
            !
            !
            interface Ethernet3
               ip pim sparse-mode
            !


8. Start Server on the Host 1

    1. Going back to the menu screen, select Host 1. Enter the bash prompt on from the CLI prompt and enable the source.  This will run for 1800 seconds

        .. code-block:: text

            What would you like to do? 7
            host1>ena
            host1#bash
            [arista@host1 ~]$ /mnt/flash/mcast.source.sh

9. Start Receiver on Host 2

    1. Going back to the menu screen, select Host 2. Enter the bash prompt on from the CLI prompt and enable the receiver.

        .. code-block:: text

            What would you like to do? 8
            host2>ena
            host2#conf t
            host2#bash
            [arista@host2 ~]$ /mnt/flash/mcast.receiver.sh

10. Observe the multicast table on Leaf 1

    1. On Leaf 1, observe the multicast table for the source.

        .. code-block:: text

            What would you like to do? 3
            leaf1>enable
            leaf1#show ip mroute

            RPF route: U - From unicast routing table
                       M - From multicast routing table
            239.103.1.1
              0.0.0.0, 0:01:56, RP 172.16.0.3, flags: W
                Incoming interface: Register
                Outgoing interface list:
                  Ethernet2
              172.16.55.2, 0:02:24, flags: SLN
                Incoming interface: Vlan55
                RPF route: [U] 172.16.55.0/24 [0/1]
                Outgoing interface list:
                  Ethernet2
            239.103.1.2
              0.0.0.0, 0:01:56, RP 172.16.0.3, flags: W
                Incoming interface: Register
                Outgoing interface list:
                  Ethernet2
              172.16.55.2, 0:02:24, flags: SLN
            Incoming interface: Vlan55
                RPF route: [U] 172.16.55.0/24 [0/1]
                Outgoing interface list:
                  Ethernet2
            239.103.1.3
              172.16.55.2, 0:02:24, flags: SLN
                Incoming interface: Vlan55
                RPF route: [U] 172.16.55.0/24 [0/1]


11. Observe the multicast table on Leaf 4

    1. On Leaf 4, observe the multicast table for the receiver using the CLI or using CVP Telemetry in Step 8.1

        .. code-block:: text

            What would you like to do? 6
            leaf4>ena
            leaf4#show ip mroute

            RPF route: U - From unicast routing table
                       M - From multicast routing table
            239.103.1.1
              0.0.0.0, 0:00:17, RP 172.16.0.3, flags: W
                Incoming interface: Ethernet3
                RPF route: [U] 172.16.0.3/32 [110/40] via 172.16.200.25
                Outgoing interface list:
                  Vlan66
              172.16.55.2, 0:00:13, flags: S
                Incoming interface: Ethernet3
                RPF route: [U] 172.16.55.0/24 [110/40] via 172.16.200.25
                Outgoing interface list:
                  Vlan66
            239.103.1.2
              0.0.0.0, 0:00:17, RP 172.16.0.3, flags: W
                Incoming interface: Ethernet3
                RPF route: [U] 172.16.0.3/32 [110/40] via 172.16.200.25
                Outgoing interface list:
                  Vlan66
              172.16.55.2, 0:00:13, flags: S
                Incoming interface: Ethernet3
                RPF route: [U] 172.16.55.0/24 [110/40] via 172.16.200.25
                Outgoing interface list:
                  Vlan66

**LAB COMPLETE**