
L2 EVPN
=======

**To access the command line of particular switch, click on that switch in the topology diagram at the top of the lab guide.**

1. On **leaf3**, configure ArBGP. **(Already configured and enabled on the switch)**

    .. code-block:: html

        configure
        service routing protocols model multi-agent

2. Configure interfaces on **leaf3**.

    .. code-block:: html

        configure
        interface Port-Channel4
          description HOST2
          switchport mode access
          switchport access vlan 12
        !
        interface Ethernet1
          shutdown
        !
        interface Ethernet2
          description SPINE1
          no switchport
          ip address 172.16.200.10/30
        !
        interface Ethernet3
          description SPINE2
          no switchport
          ip address 172.16.200.26/30
        !
        interface Ethernet4
          description HOST2
          channel-group 4 mode active
          lacp timer fast
        !
        interface Ethernet5
          shutdown
        !
        interface Loopback0
          ip address 172.16.0.5/32
        !
        interface Loopback1
          ip address 3.3.3.3/32
        !

3. Add Underlay BGP configurations on **Leaf3**

    .. code-block:: html

        configure
        router bgp 65103
          router-id 172.16.0.5
          maximum-paths 2 ecmp 2
          neighbor SPINE peer group
          neighbor SPINE bfd
          neighbor SPINE remote-as 65001
          neighbor SPINE maximum-routes 12000
          neighbor 172.16.200.9 peer group SPINE
          neighbor 172.16.200.25 peer group SPINE
          redistribute connected
        !

4. Verify Underlay

   1. On each leaf and spine

    .. code-block:: html

        show ip bgp summary
        show ip route bgp

5. On **leaf3**, build BGP Overlay

    .. code-block:: html

        configure
        router bgp 65103
          neighbor SPINE-EVPN-TRANSIT peer group
          neighbor SPINE-EVPN-TRANSIT update-source Loopback0
          neighbor SPINE-EVPN-TRANSIT ebgp-multihop
          neighbor SPINE-EVPN-TRANSIT send-community
          neighbor SPINE-EVPN-TRANSIT remote-as 65001
          neighbor SPINE-EVPN-TRANSIT maximum-routes 0
          neighbor 172.16.0.1 peer group SPINE-EVPN-TRANSIT
          neighbor 172.16.0.2 peer group SPINE-EVPN-TRANSIT
        !
        address-family evpn
          neighbor SPINE-EVPN-TRANSIT activate
        !
        address-family ipv4
          no neighbor SPINE-EVPN-TRANSIT activate
        !

6. Verify overlay

   1. On **leaf1** and **leaf3**

        .. code-block:: html

            show bgp evpn summary

7. Configure L2EVPN

   1. On **leaf3**: add VLAN 12, and interface vxlan1

        .. code-block:: html

            configure
            vlan 12
            !
            interface Vxlan1
              vxlan source-interface Loopback1
              vxlan udp-port 4789
              vxlan vlan 12 vni 1200
            !

   2. On **leaf3**: add mac vrf

        .. code-block:: html

            configure
            router bgp 65103
              vlan 12
                rd 3.3.3.3:12
                route-target both 1:12
                redistribute learned
            !

8. Verify VXLAN and L2EVPN

   1. On **leaf1** and **leaf3** verify the IMET table

        .. code-block:: text

            show interface vxlan1
            show bgp evpn route-type imet

   2. Log into **host1** and ping **host2**

        .. code-block:: text

            ping 172.16.112.202
        
   3. On **leaf1** and **leaf3**

        .. code-block:: text

            show bgp evpn route-type mac-ip
            show mac address-table dynamic

**LAB COMPLETE!**
