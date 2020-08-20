Layer 3 Leaf-Spine
==================

**To access the command line of particular switch, click on that switch in the topology diagram at the top of the lab guide.**

1. Configure SVI and VARP Virtual IP on the **Leaf4** switch using the following criteria

   1. Create the vARP MAC Address in Global Configuration mode

        .. code-block:: text

            configure
            ip virtual-router mac-address 00:1c:73:00:00:34

   2. Create the SVI and the Virtual Router Address

        .. code-block:: text

            configure
            interface vlan 34
              ip address 172.16.116.3/24
              ip virtual-router address 172.16.116.1

   3. Validate the configuration issue the following commands

        .. code-block:: text

            show ip interface brief
            show ip virtual-router

2. Configure BGP on the **Leaf4** switch using the following criteria

   1. Based on the diagram, configure L3 interfaces to **Spine1/Spine2** and interface Loopback0

        .. code-block:: text

            configure
            interface ethernet2
              description SPINE1
              no switchport
              ip address 172.16.200.14/30

            interface ethernet3
              description SPINE2
              no switchport
              ip address 172.16.200.30/30

            interface loopback0
              ip address 172.16.0.6/32

   2. Validate the configuration issue the following commands

        .. code-block:: text

            show ip interface brief

   3. Based on the diagram, turn on BGP and configure the neighbor
      relationships on **Leaf4**. eBGP to **Spine1/Spine2** and iBGP to **Leaf3**.

        .. code-block:: text

            configure
            router bgp 65002
              router-id 172.16.0.6
              neighbor 172.16.200.13 remote-as 65000
              neighbor 172.16.200.29 remote-as 65000
              neighbor 172.16.34.1 remote-as 65002
              neighbor 172.16.34.1 next-hop-self

      .. note:: Since ``neighbor 172.16.34.1 remote-as 65002`` specifies an iBGP
       peering relationship (because the ASN is the same as this switch
       ``65002``) the receiving switch may not have a route to networks more
       than 1 hop away, hence the switches should each advertise that they are
       the next hop via the ``neighbor 172.16.34.1 next-hop-self`` statement. While this scenario is
       only 2 iBGP peers, in a network fabric with several iBGP peers, a
       switch inside an AS (and not on an edge) may not have a route to a
       switch in any external AS.

   4. Validate the configuration and neighbor establishment

        .. code-block:: text

            show active
            show ip bgp summary

3. Configure networks on **Leaf4** to advertise to **Spine1/Spine2**

   1. Add the following networks to BGP announcements on **Leaf4**:

        .. code-block:: text

            configure
            router bgp 65002
              network 172.16.0.6/32
              network 172.16.116.0/24

   2. Verify all of the **Spines** and **Leafs** see these new network announcements

        .. code-block:: text

            show ip route
            show ip bgp
            show ip route bgp

   3. Add in multiple paths by enabling ECMP, on **Leaf4**, jump into BGP configuration mode and add:

        .. code-block:: text

            configure
            router bgp 65002
              maximum-paths 4 ecmp 4

   4. Check the BGP and IP route tables on each of the **Spines** and **Leafs**

        .. code-block:: text

            show ip bgp
            show ip route
            show ip route bgp

      .. note:: ECMP is now working - notice the new status code in the `show ip bgp` output

4. Validate connectivity from **Host1** to **Host2**. From **Host1** execute:

        .. code-block:: text

            ping 172.16.116.100
            traceroute 172.16.116.100

   1. Verify Leaf4's IP address is in the traceroute path, either interface 172.16.200.14 via spine1 or  interface 172.16.200.30 via spine2.
      If traffic is hashing via leaf3's 172.16.200.10 or 172.16.200.26 interfaces perform the optional ``shutdown`` steps below on **Leaf3**

        .. code-block:: text

            configure
            router bgp 65002
              neighbor 172.16.200.9 shutdown
              neighbor 172.16.200.25 shutdown

   2. Rerun traceroute/verification from **Host1** to **Host2** then revert the ``shutdown`` changes on **Leaf3**

        .. code-block:: text

            configure
            router bgp 65002
              no neighbor 172.16.200.9 shutdown
              no neighbor 172.16.200.25 shutdown

5. Other BGP features to play with if you have time:

   1. Route Redistribution: For fun do a ``watch 1 diff show ip route | begin
      Gateway`` on **Leaf1** & **Leaf2** and let those run while you execute the
      command ``redistribute connected`` below on **Leaf3**. You will see new routes being
      injected into the route tables of **Leaf1** & **Leaf2**.

        .. code-block:: text

            configure
            router bgp 65002
              redistribute connected

   2. Route Maps:

        .. code-block:: text

            configure
              route-map <name> etc

   3. BFD: BFD is a low-overhead, protocol-independent mechanism which adjacent
      systems can use instead for faster detection of faults in the path between
      them. BFD is a simple mechanism which detects the liveness of a connection
      between adjacent systems, allowing it to quickly detect failure of any
      element in the connection.

        .. code-block:: text

            configure
            router bgp 65002
              neighbor <neighbor_ip> bfd

6. Troubleshooting BGP:

    .. code-block:: text

        show ip bgp summary
        show ip bgp
        show ip bgp neighbor x.x.x.x
        show run section bgp
        show log

**LAB COMPLETE!**
