Media STP and SVI Lab
======================

.. image:: images/media-STP.&.SVI.png
   :align: center

.. note:: The Spanning-Tree protocol (STP) was initially invented in 1985 and is one of the oldest networking protocols being used in Layer 2 network topologies today. STP is classified as a network protocol that builds loop-free logical topology for Ethernet (initially bridged) networks.

1. Log into the **LabAccess** jumpserver:

   1. Type ``labs`` at the Main Menu prompt. This will bring up additional lab menu selections.
   2. Type ``media`` at this prompt to open the media lab section (If you were previously in the Media Labs Menu, you can type ``back`` to go back).
   3. Type ``media-vlan`` at the prompt. The script will configure the topology with the exception of **Leaf 4**.

   4. On **Spine 2**, verify spanning-tree operation with the topology, you should see **Spine 1** as the root bridge by viewing the Bridge ID and the interfaces designated as a Root port.  Root ports points towards the root bridge, which in this case would be Spine 1.  When you run the following command which interfaces would you expect to be your root port(s)?

        .. code-block:: text

            show spanning-tree


      **Example:**

         .. code-block:: text

            spine2#show spanning-tree
            MST0
              Spanning tree enabled protocol mstp
              Root ID    Priority    4096
                         Address     2cc2.6056.df93
                         Cost        0 (Ext) 2000 (Int)
                         Port        1 (Ethernet1)
                         Hello Time  2.000 sec  Max Age 20 sec  Forward Delay 15 sec

              Bridge ID  Priority     8192  (priority 8192 sys-id-ext 0)
                         Address     2cc2.6094.d76c
                         Hello Time  2.000 sec  Max Age 20 sec  Forward Delay 15 sec

            Interface        Role       State      Cost      Prio.Nbr Type
            ---------------- ---------- ---------- --------- -------- --------------------
            Et1              root       forwarding 2000      128.1    P2p
            Et2              designated forwarding 2000      128.2    P2p
            Et5              designated forwarding 2000      128.5    P2p
            Et6              designated forwarding 2000      128.6    P2p Edge
            Et7              designated forwarding 2000      128.7    P2p Edge

2. Configure the VLAN and interface types on **Leaf 4** to allow the spanning-tree protocol to operate and have reachability for **Host 2**.


   1. On **Leaf 4** create the Layer 2 instance of vlan 100. Creating this vlan will add itself to the spanning-tree process.

        .. code-block:: text

            configure
            vlan 100
                name v100

      **Example:**

        .. code-block:: text

            leaf4#configure
            leaf4(config)#vlan 100
            leaf4(config-vlan-100)#name v100

      We can verify its creation with the following command.  This command can also show if there are any physical interfaces associated to the vlan.

        .. code-block:: text

             show vlan

      **Example:**

        .. code-block:: text

            leaf4(config-vlan-100)#show vlan
            VLAN  Name                             Status    Ports
            ----- -------------------------------- --------- -------------------------------
            1     default                          active    Et2, Et3, Et4, Et6, Et7, Et8
                                                             Et9, Et10, Et11, Et12, Et13
                                                             Et14, Et15, Et16, Et17, Et18
                                                             Et19, Et20, Et21, Et22, Et23
                                                             Et24, Et25, Et26, Et27, Et28
                                                             Et29, Et30, Et31, Et32
            12    VLAN0012                         active
            34    VLAN0034                         active
            100   v100                             active



   2. Once the vlan is created, we can define on the uplink ports on **Leaf 4** as trunk links, as well allow vlan 100 to pass on the trunk.

        .. code-block:: text

            configure
            interface Ethernet2
              switchport trunk allowed vlan 100
              switchport mode trunk
            !
            interface Ethernet3
              switchport trunk allowed vlan 100
              switchport mode trunk
            !

      **Example:**

        .. code-block:: text

            leaf4(config-vlan-100)#configure
            leaf4(config)#interface ethernet 2-3
            leaf4(config-if-Et2-3)#switchport mode trunk
            leaf4(config-if-Et2-3)#switchport trunk allowed vlan 100

      .. note::
        By default once an interface is configured as a trunk, all vlans will be associated to it. It is good security practice to associate the specific vlans to pass on the trunk links and take part in the spanning-tree process

      Once the interface configuration has been completed for the trunk links, you can verify the spanning-tree topology and see the root bridge is **Spine 1** and the connection to **Spine 2** has been blocked for loop prevention

        .. code-block:: text

            show spanning-tree

      **Example:**

        .. code-block:: text

            leaf4(config-if-Et2-3)#show spanning-tree
            MST0
              Spanning tree enabled protocol mstp
              Root ID    Priority    4096
                         Address     2cc2.6056.df93
                         Cost        0 (Ext) 2000 (Int)
                         Port        2 (Ethernet2)
                         Hello Time  2.000 sec  Max Age 20 sec  Forward Delay 15 sec

            Bridge ID  Priority    32768  (priority 32768 sys-id-ext 0)
                         Address     2cc2.60b5.96d9
                         Hello Time  2.000 sec  Max Age 20 sec  Forward Delay 15 sec

            Interface        Role       State      Cost      Prio.Nbr Type
            ---------------- ---------- ---------- --------- -------- --------------------
            Et2              root       forwarding 2000      128.2    P2p
            Et3              alternate  discarding 2000      128.3    P2p
            Et4              designated forwarding 2000      128.4    P2p Edge
            Et6              designated forwarding 2000      128.6    P2p Edge
            Et7              designated forwarding 2000      128.7    P2p Edge
            Et8              designated forwarding 2000      128.8    P2p Edge
            Et9              designated forwarding 2000      128.9    P2p Edge
            Et10             designated forwarding 2000      128.10   P2p Edge


   3. Once the Layer 2 topology has been setup, we can configure the connection to our host as an access port to allow **Host 2** to pass traffic onto the topology

        .. code-block:: text

            configure
            interface Ethernet4
              switchport access vlan 100

      **Example:**

        .. code-block:: text

            leaf4(config-if-Et2-3)#configure
            leaf4(config)#interface ethernet 4
            leaf4(config-if-Et4)#switchport access vlan 100

3. Validate end-to-end connectivity after configuring the Layer 2 interfaces. Once the spanning tree has converged for the topology we can observe the results.

   1. Validate the vlan port association and spanning-tree topology is correct

        .. code-block:: text

            show vlan
            show spanning-tree

      **Example:**

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
            100   v100                             active    Et2, Et3, Et4


            leaf4(config-if-Et3)#show spanning-tree
            MST0
            Spanning tree enabled protocol mstp
              Root ID    Priority    4096
                         Address     2cc2.6056.df93
                         Cost        0 (Ext) 2000 (Int)
                         Port        2 (Ethernet2)
                         Hello Time  2.000 sec  Max Age 20 sec  Forward Delay 15 sec

              Bridge ID  Priority    32768  (priority 32768 sys-id-ext 0)
                         Address     2cc2.60b5.96d9
                         Hello Time  2.000 sec  Max Age 20 sec  Forward Delay 15 sec

            Interface        Role       State      Cost      Prio.Nbr Type
            ---------------- ---------- ---------- --------- -------- --------------------
            Et2              root       forwarding 2000      128.2    P2p
            Et3              alternate  discarding 2000      128.3    P2p
            Et4              designated forwarding 2000      128.4    P2p Edge
            Et6              designated forwarding 2000      128.6    P2p Edge
            Et7              designated forwarding 2000      128.7    P2p Edge
            Et8              designated forwarding 2000      128.8    P2p Edge
            Et9              designated forwarding 2000      128.9    P2p Edge
            Et10             designated forwarding 2000      128.10   P2p Edge


    You should see the root bridge is towards **Spine 1** and vlan 100 should be associated to interfaces eth2, eth3 and eth4

   2. Log into **Host 2** and verify you can reach the SVI for vlan 100 as well as reachability to **Host 1**

        .. code-block:: text

            SVI (Vlan 100 gateway on Spine 1)
            ping 172.16.46.4

            host2# ping 172.16.46.4
            PING 172.16.46.4 (172.16.46.4) 72(100) bytes of data.
            80 bytes from 172.16.46.4: icmp_seq=1 ttl=64 time=35.3 ms
            80 bytes from 172.16.46.4: icmp_seq=2 ttl=64 time=51.3 ms
            80 bytes from 172.16.46.4: icmp_seq=3 ttl=64 time=49.9 ms
            80 bytes from 172.16.46.4: icmp_seq=4 ttl=64 time=48.9 ms
            80 bytes from 172.16.46.4: icmp_seq=5 ttl=64 time=35.6 ms

            --- 172.16.46.4 ping statistics ---
            5 packets transmitted, 5 received, 0% packet loss, time 73ms
            rtt min/avg/max/mdev = 35.313/44.256/51.377/7.192 ms, pipe 4, ipg/ewma 18.302/39.598 ms


            Host 1
            ping 172.16.15.5

            host2# ping 172.16.15.5
            PING 172.16.15.5 (172.16.15.5) 72(100) bytes of data.
            From 172.16.46.4: icmp_seq=1 Redirect Host(New nexthop: 172.16.15.5)
            80 bytes from 172.16.15.5: icmp_seq=1 ttl=63 time=237 ms
            80 bytes from 172.16.15.5: icmp_seq=2 ttl=63 time=233 ms
            80 bytes from 172.16.15.5: icmp_seq=3 ttl=63 time=250 ms
            80 bytes from 172.16.15.5: icmp_seq=4 ttl=63 time=257 ms
            80 bytes from 172.16.15.5: icmp_seq=5 ttl=63 time=257 ms

            --- 172.16.15.5 ping statistics ---
            5 packets transmitted, 5 received, 0% packet loss, time 43ms
            rtt min/avg/max/mdev = 233.030/247.345/257.699/10.206 ms, pipe 5, ipg/ewma 10.926/243.255 ms

      If all the SVI and STP settings have been completed correctly you should be able to ping the remote host as well as the SVI interface itself configured on **Spine 1** which is also the root bridge for this topology.


 .. admonition:: **Test your knowledge:**

    When you are verifying the spanning-tree topology from **Leaf 4**, what are some of the reasons for the root bridge selection?


**LAB COMPLETE!**

.. admonition:: **Helpful Commands:**

    During the lab you can use the different commands to verify connectivity and behaviour for validation and troubleshooting purposes:

   - show vlan
   - show interfaces trunk
   - show interfaces status
   - show spanning-tree
