
L2 EVPN
=======

.. image:: images/l2evpn.png
   :align: center

.. note:: Based on limitations in **vEOS-LAB** data plane, EVPN with
          Multi-homing via MLAG is unsupported. As such, this lab exercise will
          not enable MLAG.

1. Log into the  **LabAccess**  jumpserver:

   1. Type ``l2evpn`` at the prompt. The script will configure the datacenter with the exception of **leaf3**

2. On **leaf3**, configure ArBGP. **(Already configured and enabled on the switch)**

    .. code-block:: html

        configure
        service routing protocols model multi-agent

3. Configure interfaces on **leaf3**.

    .. code-block:: html

        configure
        interface Port-Channel4
          switchport mode access
          switchport access vlan 12
        !
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
          channel-group 4 mode active
          lacp rate fast
        !
        interface Ethernet5
          shutdown
        !
        interface Loopback0
          ip address 172.16.0.5/32
        !
        interface Loopback1
          ip address 3.3.3.3/32
          ip address 99.99.99.99/32 secondary
        !

4. Add Underlay BGP configurations on **Leaf3**

    .. code-block:: html

        configure
        router bgp 65103
          router-id 172.16.0.5
          maximum-paths 2 ecmp 2
          neighbor SPINE peer group
          neighbor SPINE fall-over bfd
          neighbor SPINE remote-as 65001
          neighbor SPINE maximum-routes 12000
          neighbor 172.16.200.9 peer group SPINE
          neighbor 172.16.200.25 peer group SPINE
          redistribute connected
        !

5. Verify Underlay

   1. On each leaf and spine

    .. code-block:: html

        show ip bgp summary
        show ip route bgp

6. On **leaf3**, build BGP Overlay

    .. code-block:: html

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
          neighbor SPINE-EVPN-TRANSIT activate
        !
        address-family ipv4
          no neighbor SPINE-EVPN-TRANSIT activate
        !

7. Verify overlay

   1. On **leaf1** and **leaf3**

        .. code-block:: html

            show bgp evpn summary

8. Configure L2EVPN

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

9. Verify VXLAN and L2EVPN

   1. On **leaf1** and **leaf3** verify the IMET table

        .. code-block:: text

            show interface vxlan1
            show bgp evpn route-type imet

   2. Log into **host1** and ping **host2**

        .. code-block:: text

            enable
            ping 172.16.112.202

   3. On **leaf1** and **leaf3**

        .. code-block:: text

            show bgp evpn route-type mac-ip
            show mac address-table dynamic

**LAB COMPLETE!**
