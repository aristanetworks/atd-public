VxLAN
=====

**To access the command line of particular switch, click on that switch in the topology diagram at the top of the lab guide.**

1. On **Leaf3**, configure Port-channels connecting to **Host2**

    .. code-block:: text

        configure
        interface port-channel 4
            description MLAG - HOST2
            switchport access vlan 12
            mlag 4

        interface Ethernet4
            description HOST2
            channel-group 4 mode active
            lacp timer fast

2. Verify MLAG on **Leaf3**

    .. code-block:: text

        show mlag
        show mlag detail
        show mlag interfaces
        show port-channel

3. Validate BGP operation **Leaf3**

    .. code-block:: text

        show run section bgp
        show ip route bgp
        show ip route
        show ip interface brief
        show ip bgp summary

.. note:: ``show ip bgp summary`` will show that the BGP neighbors have moved to ``Estab`` state. Note the iBGP peering between Leaf3 & Leaf4. Also note the route to the shared loopback1 of Leaf1 & Leaf2. This is the remote VTEP on the other side of the leaf-spine network.

4. Create Loopback 1 and the VXLAN VTEP (VTI) interfaces on **Leaf3**

   1. Configuration

        .. code-block:: text

            configure
            interface Loopback1
              ip address 172.16.0.56/32

            interface vxlan 1
              vxlan source-interface loopback 1
              vxlan vlan 12 vni 1212
              vxlan flood vtep 172.16.0.34

      .. note:: ``vxlan flood vtep 172.16.0.34`` adds the shared loopback1 IP address on Leaf1 & Leaf2 to the HER list. Note that for autodiscovery of VTEPs, one must use BGP eVPN (see eVPN labs) or CVX (see CVX lab).

   2. Verification

        .. code-block:: text

            show run interface vxlan 1
            show interface vxlan 1

5. Log into **Host 1** and **Host 2**, ping the vARP VIP and the other host

   1. Host 1 ping tests. From **Host1**:

        .. code-block:: text

            ping 172.16.112.1
            ping 172.16.112.202

      .. note:: The TTL in the ping outputs above. Even though .202 is many
                switches away, it appears locally connected and has the same
                TTL as the ping to .1. It's also interesting to realize that
                due to MLAG hashing of both the ARP requests and ping packet
                flows that pings to the SVI addresses of .2 & .3 may or may not
                work. Do you know why?

   2. Host 1 MAC/ARP information

        .. code-block:: text

            show interface po1 | grep -i Hardware
            show arp

      .. note:: Note the MAC addresses returned by the commands above.

   3. Host 2 ping tests. From **Host2**:

        .. code-block:: text

            ping 172.16.112.1
            ping 172.16.112.201

      .. note:: Note the TTL in the ping outputs above. Even though .201 is many
                switches away, it appears locally connected and has the same TTL
                as the ping to .1. Also note that the vARP VIP (172.16.112.1)
                address & and vARP MAC address (00:1c:73:00:00:ff) are the **same** for both leaf
                pairs - this IP address is known as an AnyCast IP address. If
                a VM was motioning from **Host1** to **Host2** for maintenance,
                the default GW address nor the ARP cache on that VM need to
                change.

   4. Host 2 MAC/ARP information

        .. code-block:: text

            show interface po1 | grep -i Hardware
            show arp

      .. note:: Note the MAC addresses returned by the commands above and
                compare to the prior ``grep`` and ``arp`` commands and see that
                both hosts appear to each other as though they are on the same
                L2 broadcast domain. **For a little extra fun**, as you are
                running the pings from **host1**, on another set of windows
                for **leaf1** & **leaf2** run ``clear counters`` then run
                ``watch 1 diff show int e4 counter`` and see how MLAG hashing
                across the different pings causes the packets to choose a
                particular member of the port-channel in both the outbound &
                inbound ping flows.

6. Verification – on **Leaf 1/2** and **Leaf 3/4**

   1. Verify the MAC addresses and the associated VTEP IP

        .. code-block:: text

            show vxlan vtep
            show vxlan address-table

      .. note:: For ``show vxlan vtep`` & ``show vxlan address-table`` to be
                populated, the above ``pings`` need to have been active very
                recently so that the MAC addresses don't age out, and you'll
                notice that at least 1 (but not necessarily both) of the MLAG
                pair switches (**leaf1** or
                **leaf2**) will have knowledge of the remote VTEP. This is
                because this is the direction the pings (inbound & outbound)
                last hashed.

   2. Verify the MAC address and the associated interface

        .. code-block:: text

            show mac address-table

7. Let’s run some other show commands and tests to poke around VxLAN. On **Leaf1** and **Leaf3** issue the following commands:

    .. code-block:: text

        show interface vxlan 1
        show mac address-table
        show log

**LAB COMPLETE!**
