L3 EVPN
=======

.. image:: images/l3evpn.png
   :align: center

.. note:: Based on limitations in vEOS-LAB data plane, EVPN with Multi-homing via MLAG is unsupported.  As such, this lab exercise will not enable MLAG.

1. Log into the  **LabAccess**  jumpserver:

   1. Type ``l3evpn`` at the prompt. The script will configure the datacenter with the exception of **leaf3**

2. On **leaf3**, configure EOS to Mutli-Agent and add loopback0

   1. **leaf3** enable the Multi-Agent **(Already configured and enabled on the switch)**

        .. code-block:: text

            configure
            service routing protocols model multi-agent

   2. **leaf3** Underlay Interface configurations. Note the interfaces to **host2** change from previous L2EVPN lab

        .. code-block:: text

            configure
            interface Ethernet1
              shutdown
            !
            interface Ethernet2
              no switchport
              ip address 172.16.200.10/30
            !
            interface Ethernet3
              no switchport
              ip address 172.16.200.26/30
            !
            interface Ethernet4
              shutdown
            !
            interface Ethernet5
              channel-group 5 mode active
              no shutdown
            !
            interface Loopback0
              ip address 172.16.0.5/32
            !
            interface Loopback1
              ip address 3.3.3.3/32
              ip address 99.99.99.99/32 secondary
            !

   3. On **leaf3** Add Underlay BGP configurations

        .. code-block:: text

            configure
            router bgp 65103
              router-id 172.16.0.5
              maximum-paths 2 ecmp 2
              neighbor SPINE peer group
              neighbor SPINE remote-as 65001
              neighbor SPINE bfd
              neighbor SPINE maximum-routes 12000
              neighbor 172.16.200.9 peer group SPINE
              neighbor 172.16.200.25 peer group SPINE
              redistribute connected

3. Verify Underlay on **every** leaf and spine:

    .. code-block:: text

        show ip bgp summary
        show ip route bgp

4. On **leaf3**, build BGP Overlay

    .. code-block:: text

        configure
        router bgp 65103
          neighbor SPINE-EVPN-TRANSIT peer group
          neighbor SPINE-EVPN-TRANSIT next-hop-unchanged
          neighbor SPINE-EVPN-TRANSIT update-source Loopback0
          neighbor SPINE-EVPN-TRANSIT ebgp-multihop
          neighbor SPINE-EVPN-TRANSIT send-community extended
          neighbor SPINE-EVPN-TRANSIT remote-as 65001
          neighbor SPINE-EVPN-TRANSIT maximum-routes 0
          neighbor 172.16.0.1 peer group SPINE-EVPN-TRANSIT
          neighbor 172.16.0.2 peer group SPINE-EVPN-TRANSIT
        !
        address-family evpn
          bgp next-hop-unchanged
          neighbor SPINE-EVPN-TRANSIT activate
        !
        address-family ipv4
          no neighbor SPINE-EVPN-TRANSIT activate
        !

5. Verify overlay on **leaf1** and **leaf3**:

    .. code-block:: text

        show bgp evpn summary

6. Configure L3EVPN

   1. Configure the VRF

        .. code-block:: text

            configure
            vrf instance vrf1
            !
            ip routing vrf vrf1
            !
            router bgp 65103
              vrf vrf1
                rd 3.3.3.3:1001
                route-target import evpn 1:1001
                route-target export evpn 1:1001
                redistribute connected
                redistribute static
              exit
            !
            exit

   2. Configure vrf interfaces (start in global configuration mode not BGP)

        .. code-block:: text

            interface Port-Channel5
              switchport access vlan 2003
              no shutdown
            !
            interface Vlan2003
              mtu 9000
              no autostate
              vrf vrf1
              ip address virtual 172.16.116.1/24
            !
            interface Loopback901
              vrf vrf1
              ip address 200.200.200.2/32
            !

   3. Map VRF to VNI

        .. code-block:: text

            configure
            interface Vxlan1
              vxlan source-interface Loopback1
              vxlan udp-port 4789
              vxlan vrf vrf1 vni 1001
            !

7. Verify VRF on Leaf 1 and 3 (note route resolution over VNI and dynamic VLAN to VNI mapping)

   1. On **leaf1** and **leaf3**

        .. code-block:: text

            show interface vxlan1

   2. Log into **host1** and ping **host2**

        .. code-block:: text

            ping 172.16.116.100
        
   3. On **leaf1** and **leaf3**

        .. code-block:: text

            show ip route vrf vrf1
            show mac address-table dynamic

**LAB COMPLETE!**
