Advanced Networking for Media Engineers
=======================================

.. image:: images/media_multicast.png
   :align: center

.. note:: To simplify the training using our multicast topology, this exercise will disable Leaf2 and Leaf3.  This lab is a continuation of the concepts from the previous Broadcast Engineer Labs

1. Log into the **LabAccess** jumpserver:
    1. Type ``multicast`` or option ``18`` at the prompt. The script will pre-configure the topology with the exception of Leaf4 and Hosts 1 & 2

2. Create Vlan 46 & SVI for host access vlan on **Leaf 4**.

    1. On **Leaf 4** we will create an vlan and a SVI

        .. code-block:: text

            vlan 46
            !
            interface Vlan46
               no autostate
               ip address 172.16.46.4/24

        **Example:**

        .. code-block:: text

            leaf4(config)#vlan 46
            leaf4(config)#interface vlan 46
            leaf4(config-if-Vl46)#no autostate
            leaf4(config-if-Vl46)#ip address 172.16.46.4/24

        **Verification:**

        .. code-block:: text

            leaf4(config)#show vlan
            VLAN  Name                             Status    Ports
            ----- -------------------------------- --------- -------------------------------
            1     default                          active    Et6, Et7, Et8, Et9, Et10, Et11
                                                             Et12, Et13, Et14, Et15, Et16
                                                             Et17, Et18, Et19, Et20, Et21
                                                             Et22, Et23, Et24, Et25, Et26
                                                             Et27, Et28, Et29, Et30, Et31
                                                             Et32
            12    VLAN0012                         active
            34    VLAN0034                         active
            46    VLAN0046                         active    Cpu


            leaf4(config)#show ip int brief
            Interface              IP Address         Status     Protocol         MTU
            Management1            192.168.0.17/24    down       notpresent      1500
            Vlan46                 172.16.46.4/24     up         up              1500


3. Create connectivity for **Host 2** on **Leaf 4**

    1.  On **Leaf 4**, interface *Ethernet 4* is attached to **Host 2**, associate the port as access vlan 46.

        .. code-block:: text

            interface Ethernet4
               switchport access vlan 46
               no shutdown

        **Example:**

        .. code-block:: text

            leaf4(config-if-Et4)#switchport access vlan 46
            leaf4(config-if-Et4)#no shutdown

        **Verification:**

        .. code-block:: text

            leaf4(config-if-Et4)#show vlan
            VLAN  Name                             Status    Ports
            ----- -------------------------------- --------- -------------------------------
            1     default                          active    Et6, Et7, Et8, Et9, Et10, Et11
                                                             Et12, Et13, Et14, Et15, Et16
                                                             Et17, Et18, Et19, Et20, Et21
                                                             Et22, Et23, Et24, Et25, Et26
                                                             Et27, Et28, Et29, Et30, Et31
                                                             Et32
            12    VLAN0012                         active
            34    VLAN0034                         active
            46    VLAN0046                         active    Cpu, Et4


4. Create uplink connectivity to **Spine 2**

    1.  On **Leaf 4**, *Ethernet 3* is connected to **Spine 2**. Create a routed port for uplink access

        .. code-block:: text

           interface Ethernet3
              no switchport
              ip address 172.16.200.26/30
              no shutdown


        **Example:**

        .. code-block:: text

            leaf4(config-if-Et3)#interface ethernet 3
            leaf4(config-if-Et3)#no switchport
            leaf4(config-if-Et3)#ip address 172.16.200.26/30
            leaf4(config-if-Et3)#no shutdown

        **Verification:**

        .. code-block:: text

            leaf4#sh ip int br
            Interface              IP Address         Status     Protocol         MTU
            Ethernet3              172.16.200.26/30   up         up              1500
            Management1            192.168.0.17/24    down       notpresent      1500
            Vlan46                 172.16.46.4/24     up         up              1500


5.  Enable OSPF & verify connectivity

    1.  On **Leaf 4**, create a loopback interface & assign an IP to be used as the Router-ID. On **Leaf 4**, enable the OSPF routing process and assign the networks to be advertised

        .. code-block:: text

            interface Loopback0
               ip address 172.16.0.5/32
            !
            router ospf 6500
               router-id 172.16.0.5
               passive-interface Loopback0
               passive-interface Vlan46
               network 172.16.0.0/24 area 0.0.0.0
               network 172.16.46.0/24 area 0.0.0.0
               network 172.16.200.24/30 area 0.0.0.0

        **Example:**

        .. code-block:: text

            leaf4(config-if-Et3)#interface loopback 0
            leaf4(config-if-Lo0)#ip address 172.16.0.5/32
            leaf4(config-if-Lo0)#
            leaf4(config-if-Lo0)#router ospf 6500
            leaf4(config-router-ospf)#router-id 172.16.0.5
            leaf4(config-router-ospf)#passive-interface loopback 0
            leaf4(config-router-ospf)#passive-interface vlan46
            leaf4(config-router-ospf)#network 172.16.0.0/24 area 0.0.0.0
            leaf4(config-router-ospf)#network 172.16.46.0/24 area 0.0.0.0
            leaf4(config-router-ospf)#network 172.16.200.24/30 area 0.0.0.0



        **Verification:**

        .. code-block:: text


            leaf4(config-router-ospf)#show ip int br
            Interface              IP Address         Status     Protocol         MTU
            Ethernet3              172.16.200.26/30   up         up              1500
            Loopback0              172.16.0.5/32      up         up             65535
            Management1            192.168.0.17/24    down       notpresent      1500
            Vlan46                 172.16.46.4/24     up         up              1500



    2. Issue a ``show ip route`` command on Leaf 4.  Output should show the following networks from Leaf 1 being advertised and shows a Full/BR state with Leaf 1, its neighbor.


        **Routing Table Example:**


        .. code-block:: text

            leaf4#show ip route

            leaf4(config-router-ospf)#show ip route

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

             O      172.16.0.1/32 [110/30] via 172.16.200.25, Ethernet3
             O      172.16.0.2/32 [110/20] via 172.16.200.25, Ethernet3
             O      172.16.0.3/32 [110/40] via 172.16.200.25, Ethernet3
             C      172.16.0.5/32 is directly connected, Loopback0
             O      172.16.11.0/24 [110/40] via 172.16.200.25, Ethernet3
             C      172.16.46.0/24 is directly connected, Vlan46
             O      172.16.200.0/30 [110/30] via 172.16.200.25, Ethernet3
             C      172.16.200.24/30 is directly connected, Ethernet3
             O      172.16.200.32/30 [110/20] via 172.16.200.25, Ethernet3
             C      192.168.0.0/24 is directly connected, Management1


        **OSPF Neighbor Example:**

        .. code-block:: text

            leaf4(config-router-ospf)#show ip ospf neighbor
            Neighbor ID     VRF      Pri State                  Dead Time   Address         Interface
            172.16.0.2      default  1   FULL/DR                00:00:35    172.16.200.25   Ethernet3


6. Prepare Connectivity on Host 1 & Host 2

    1. On Host 1, we will need to setup a default route for the host to communicate. On Host 1 type the following commands to prepare the host

    .. code-block:: text


        host1(config)#ip route 0.0.0.0/0 172.16.55.1
        host1(config)#interface ethernet 3
        host1(config-if-Et3)#no switchport
        host1(config-if-Et3)#ip address 172.16.55.2/24
        host1(config-if-Et3)#show ip route






    2. On Host 2, we will need to setup a default route for the host to communicate. On Host 2 type the following commands to prepare the host

        .. code-block:: text

            host2(config)#ip route 0.0.0.0/0 172.16.46.1
            host2(config)#interface ethernet 4
            host2(config-if-Et4)#no switchport
            host2(config-if-Et4)#ip address 172.16.46.5/24
            host2(config-if-Et4)#show ip route




        **Verification:**




    3.	Issue a ping command from host2 in network 172.16.46.0/24 to host 1 on 172.16.55.0/2

        .. code-block:: text

            What would you like to do? 7
            host2>enable
            host2# ping 172.16.15.5








7.	Enable Multicast

    1.  On Leaf 4, enable multicast routing using the following commands;  We will be enabling multicast routing on Leaf 4 and assigning the interfaces to participate in multicast routing.  As well we will define the RP address on the switch.


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


        **Example:**
        **Verification:**

        .. code-block:: text

            <TBD>

        **Example:**
        **Verification:**

        .. code-block:: text

            <TBD>


8. Start Server on the Host 1

    1. Going back to the menu screen, select Host 1. Enter the bash prompt on from the CLI prompt and enable the source.  This will run for 1800 seconds

        .. code-block:: text

            What would you like to do? 7
            host1>ena
            host1#bash
            [arista@host1 ~]$ /mnt/flash/mcast.source.sh


        **Example:**
        **Verification:**

        .. code-block:: text

            <TBD>

        **Example:**
        **Verification:**

        .. code-block:: text

            <tbd>


9. Start Receiver on Host 2

    1. Going back to the menu screen, select Host 2. Enter the bash prompt on from the CLI prompt and enable the receiver.

        .. code-block:: text

            What would you like to do? 8
            host2>ena
            host2#conf t
            host2#bash
            [arista@host2 ~]$ /mnt/flash/mcast.receiver.sh

        **Example:**
        **Verification:**

        .. code-block:: text

            <TBD>

        **Example:**
        **Verification:**

        .. code-block:: text

            <TBD>


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