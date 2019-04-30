Advanced Networking for Media Engineers
=======================================

.. image:: images/media_mcast_01.png
   :align: center

.. note:: To simplify the training using our multicast topology, this exercise will disable Leaf2 and Leaf3.  We will be using CloudVision Portal (CVP) to deploy configlets to configure this topology.

1. Log into the **LabAccess** jumpserver:
    1.1. Type ``multicast`` or option ``18`` at the prompt. The script will pre-configure the topology with the exception of Leaf4 and Hosts 1 & 2

2. On Host 1 and Host 2 disable unused interfaces for this lab
    2.1. Using the jump host, connect to Host 1 and host 2 and clear the configuration currently assigned to the interfaces.  Issue the following command to clear the currently assigned configuration.

        .. code-block:: text

            Host 2 example:
            What would you like to do? 8

            host2>enable
            host2#conf
            host2(config)#default interface ethernet 1-32

    2.2. Confirm that the interfaces on the hosts have been cleared using the following command

        .. code-block:: text

            host2(config)#show run sect interface

            !!Output should state blank information under the interfaces 1 to 32

            interface Port-Channel1
               no switchport
               ip address 172.16.112.202/24
            !
            interface Port-Channel2
               no switchport
               ip address 172.16.116.100/24
            !
            interface Ethernet1
            !
            interface Ethernet2
            !
             .... output omitted for brevity ...
            interface Ethernet31
            !
            interface Ethernet32
            !
            interface Management1
              ip address 192.168.0.32/24

3. Create Vlan 66 & SVI for host access vlan on Leaf 4 (using CVP Configlet Builder)
    3.1. On CVP we will be creating a configlet called Leaf 4 VLAN to disable & default the interfaces to prepare the device for this lab.

        .. code-block:: text

            On CVP we will be going to the Configlets section from the main menu of CVP.


        .. image:: images/CVPConfiglets.png
            :align: center

        .. code-block:: text

            On the top right side of the configlets page there is a + sign
            click on this to open a submenu and select configlets.

        .. image:: images/CVPConfiglets2.png
            :align: center

        .. code-block:: text

            This will bring up a create configlet menu.  Here we can create the
            configlet to disable & remove any configuration from the previous
            labs.  First name this configlet, for this configlet it will be
            named Leaf 4 VLAN. On the configuration section type the following
            commands below. Then save the configuration using the green save
            button at the bottom of the page.

        .. image:: images/CVPLeaf4Vlan.png
            :align: center

        .. code-block:: text

            !!Configlet commands provided below
            interface Vlan66
               no autostate
               ip address 172.16.66.1./24
               ip pim sparse-mode

        .. code-block:: text

            Once the configlet is saved we can now apply the newly created
            configlet to Leaf 4. On the main menu of CVP select Network
            Provisioning to bring us to the configlet hierarchy view.

        .. image:: images/CVPNetworkProvisioning.png
            :align: center

        .. code-block:: text

            On the Network Provisioning view right click on Leaf 4,
            select Manage then Configlet from the submenus. This will bring
            us to the configlet assignment page.

        .. image:: images/CVPConfigletMenu.png
            :align: center

        .. code-block:: text

            On the Configlet assignment page we can browse through the configlets
            on the left hand pane. Select the newly created configlet Leaf 4 Vlan
            and it will be added to the proposed configuration pane in the right
            hand side.  You can expand out the configlet to ensure that it is the
            correct configlet being assigned.  Once ready click on the
            green Validate button.

        .. image:: images/CVPManageConfiglet.png
            :align: center

        .. code-block:: text

            This will bring us into the Validate and Compare page. We can
            confirm the proposed configuration on the left hand pane with
            the current running configuration on the right hand pane.  In
            the center will show you the new proposed designed configuration
             highlighting the changes that will occur.  Select save once ready.

        .. image:: images/CVPValidateCompare.png
            :align: center

        .. code-block:: text

            This will bring us back to the network provisioning page. You
            will now notice a green halo below Leaf 4.  This identifies
            that there are pending changes that need to be saved.  Select
            the green save button on the bottom of the page to generate a Task.

        .. image:: images/CVPSave.png
            :align: center

        .. code-block:: text

            This will create a Yellow “T” on Leaf 4. This identifies that
            there is a task pending to be executed on Leaf 4.

        .. image:: images/CVPTaskPending.png
            :align: center

        .. code-block:: text

            Going back to the Main menu, select Change Control.

        .. image:: images/CVPCCM1.png
            :align: center

        .. code-block:: text

            We can create a change control to execute the Leaf 4 VLAN configlet.
            Using the change control procedure generates a snapshot of the switch
            before and after the configuration changes. As well it enables you to
            create the change control task to execute automatically if
            configured.  On the Change Management page select the + to create a
            change control task.

        .. image:: images/CVPCCM2.png
            :align: center

        .. code-block:: text

            This brings up all the pending tasks that we can incorporate into a
            single change control task. In this instance we have one task, select
            it and click on the green Add button.

        .. image:: images/CVPCCM3.png
            :align: center

        .. code-block:: text

            Once selected we are back in the Create Change Control Menu.  Create
            a name to this change control, and we have the option to save the
            change control task to execute at a later time or execute the new
            change control.  In this lab we will select Execute to start the
            change control right away.

        .. image:: images/CVPCCM4.png
            :align: center

        .. code-block:: text

            Once Execute is selected it will run the change control running
            though 3 steps, creating a snapshot before the changes are applied,
            applying the changes and a snapshot on after the changes are applied.

        .. image:: images/CVPCCM5.png
            :align: center

        .. code-block:: text

            On a completed change control will be a screen similar to below.
            You can view the snapshot comparison here to compare pre and post
            config changes.

        .. image:: images/CVPCCM6.png
            :align: center

        .. code-block:: text

            Verification of this step can be done using CVP Telemetry, From the
            main menu select CVP telemetry. Select Devices from the upper menu, then
            Leaf 4 then the switching label on the left hand pane.

        .. image:: images/CVPCCM7.png
            :align: center

4. Create connectivity for Host 2 on Leaf 4
    4.1.  On Leaf 4, interface Ethernet 5 is attached to Host 2, associate the port as access vlan 66.

        .. code-block:: text

            Using the steps in task 3 we can create a configlet to create the
            connectivity to Host 2.  Create a configlet called Leaf 4 Port Level
            and follow the previous steps to create and apply the configlet to
            Leaf 4.

        .. image:: images/CVPPortLevel.png
            :align: center
        .. code-block:: text

            !Configlet provided below.

            interface Ethernet5
               switchport access vlan 66

        Verification of this step can be done using CVP Telemetry, From the main menu select CVP telemetry.  Devices from the upper menu, Leaf 4 then the Interfaces > Ethernet label on the left hand pane. We can drill down to ethernet 5. This view is the live port level view of Ethernet 5, on the quick statistics panes in the top we see that the port is associated to vlan 66.

        .. image:: images/CVPPortLevelVerify.png
            :align: center

5. Create uplink connectivity to Spine 2
    5.1.  On Leaf 4, Ethernet 3 is connected to Spine 2. Create a routed port for uplink access

        Using the steps in task 2.1 we can create a configlet to create the connectivity the spine for uplink to the network.  Create a configlet called Leaf 4 Uplink and follow the previous steps to create and apply the configlet to Leaf 4.

        .. image:: images/CVPL4Uplink.png
            :align: center

        .. code-block:: text

           interface Ethernet3
              no switchport
              ip address 172.16.200.26/30
              ip pim sparse-mode

        Verification of this step can be done using CVP Telemetry, From the main menu select CVP telemetry.  Devices from the upper menu, Leaf 4 then the Interfaces > Routed Ports label on the left hand pane. We can view all routed interfaces from this view.

        .. image:: images/CVPL4UplinkVerify1.png
            :align: center

        As well we can view the routing table as well to view the routes. This also so a quick highlight of the recent routing table changes. Select IPv4 Routing Table from the left hand pane.

        .. image:: images/CVPL4UplinkVerify2.png
            :align: center

6.  Enable OSPF & verify connectivity
    6.1.  On Leaf 4, create a loopback interface & assign an IP to be used as the Router-ID. On Leaf 3, enable the OSPF routing process and assign the networks to be advertised

    Using the steps in task 3 we can create a configlet to create the OSPF configuration on Leaf 3.  Create a configlet called Leaf 4 OSPF Configuration and follow the previous steps to create and apply the configlet to Leaf 4.

        .. image:: images/CVPL4OSPFConfig.png
            :align: center

        .. code-block:: text

            !Configlet provided below.

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

    Verification of this step can be done using CVP Telemetry, From the main menu select CVP telemetry.  Devices from the upper menu, Leaf 4 then the Routing > IPv4 Routing Table label on the left hand pane. We can view a searchable IPv4 Routing table.

        .. image:: images/CVPL4OSPFVerify.png
            :align: center

    6.2. Issue a ``show ip route`` command on Leaf 1.  Output should show the following networks from Leaf 4 being advertised and shows a Full/BR state with Leaf 4, its neighbor.

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


7. Prepare Connectivity on Host 1 & Host 2
    7.1 On Host 1, we will need to setup a default route for the host to communicate. On Host 1 type the following commands to prepare the host

    .. code-block:: text

        What would you like to do? 7
        host1>ena
        host1#conf t
        host1(config)#configure
        host1(config)#no interface port-Channel 1-2
        host1(config)#default interface ethernet 1-32
        host1(config)#show run section interface
        interface Ethernet1
        !
        interface Ethernet2
        !
        interface Ethernet3
        !
        interface Ethernet4
        !
        interface Management1
           ip address 192.168.0.31/24
        !
        ! Configuration of Host 1 below
        !
        host1(config)#no ip route 0.0.0.0/0 172.16.115.1
        host1(config)#ip route 0.0.0.0/0 172.16.55.1
        host1(config)#interface ethernet 3
        host1(config-if-Et3)#no switchport
        host1(config-if-Et3)#ip address 172.16.55.2/24
        host1(config-if-Et3)#show ip route

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
         S      0.0.0.0/0 [1/0] via 172.16.55.1, Ethernet3

         C      172.16.55.0/24 is directly connected, Ethernet3
         C      192.168.0.0/24 is directly connected, Management1

        host1(config-if-Et3)#show ip interface brief
        Interface              IP Address         Status     Protocol         MTU
        Ethernet3              172.16.55.2/24     up         up              1500
        Management1            192.168.0.31/2
        host1(config-if-Et3)#


    7.2 On Host 2, we will need to setup a default route for the host to communicate. On Host 2 type the following commands to prepare the host

        .. code-block:: text

            What would you like to do? 8
            host2>ena
            host2#conf t
            host2(config)#no interface port-Channel 1-2
            host2(config)#default interface ethernet 1-32
            host2(config)#show run sect interface
            interface Ethernet1
            !
            interface Ethernet2
            !
            .... Output omitted for Brevity...
            interface Ethernet31
            !
            interface Ethernet32
            !
            interface Management1
               ip address 192.168.0.32/24
            !
            !Configuration of Host 2 below
            !
            host2(config)#no ip route 0.0.0.0/0 172.16.115.1
            host2(config)#ip route 0.0.0.0/0 172.16.66.1
            host2(config)#interface ethernet 4
            host2(config-if-Et4)#no switchport
            host2(config-if-Et4)#ip address 172.16.66.2/24
            host2(config-if-Et4)#show ip route

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
             S      0.0.0.0/0 [1/0] via 172.16.66.1, Ethernet4

             C      172.16.66.0/24 is directly connected, Ethernet4
             C      192.168.0.0/24 is directly connected, Management1

            host2(config-if-Et4)#

    7.3	Issue a ping command from host2 in network 172.16.66.0/24 to host 1 on 172.16.55.0/2

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

8.	Enable Multicast (CVP Configlet Builder)

    8.1.  On Leaf 4, enable multicast routing using the following commands;  We will be enabling multicast routing on Leaf 4 and assigning the interfaces to participate in multicast routing.  As well we will define the RP address on the switch in a single configlet.

        .. code-block:: text

            Using the steps in task 2.1 we can create a configlet to create
             the multicast configuration for Leaf 4.  Create a configlet called
             Leaf 4 Multicast and follow the previous steps to create and apply
             the configlet to Leaf 4.

        .. image:: images/CVPL4Mcast.png
            :align: center

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

        .. code-block:: text

            Verification of this step can be done using CVP Telemetry, From the
            main menu select CVP telemetry.  Devices from the upper menu, Leaf 4
            then the Routing > IPv4 Routing Table label on the left hand pane. We
            can view a searchable IPv4 Multicast Routing table.  This would be
            comparative to the show ip mroute CLI command.

        .. image:: images/CVPL4McastCVPview.png
            :align: center


9. Start Server on the Host 1
    9.1 On Host 1, Enter the bash prompt on from the CLI prompt and enable the source.  This will run for 1800 seconds

        .. code-block:: text

            What would you like to do? 7
            host1>ena
            host1#bash
            [arista@host1 ~]$ /mnt/flash/mcast.source.sh

10. Start Receiver on Host 2
    10.1 On Host 2, Enter the bash prompt on from the CLI prompt and enable the receiver.

        .. code-block:: text

            What would you like to do? 8
            host2>ena
            host2#conf t
            host2#bash
            [arista@host2 ~]$ /mnt/flash/mcast.receiver.sh

11. Observe the multicast table on Leaf 1
    11.1 On Leaf 1, observe the multicast table for the source using the CLI or using CVP Telemetry in Step 8.1

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

12. Observe the multicast table on Leaf 4
    12.1 On Leaf 4, observe the multicast table for the receiver using the CLI or using CVP Telemetry in Step 8.1

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