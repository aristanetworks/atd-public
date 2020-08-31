.. image:: images/arista_logo.png
   :align: center

EVPN Lab Answer Key
=======================

Pre-Lab configuration on all Switches
---------------------------------------

    .. code-block:: html

        service routing-protocols model multi-agent

Lab 1: IP Underlay Control-Plane Buildout
----------------------------------------------

**SPINE1:**

    .. code-block:: html

        route-map RM-CONN-2-BGP permit 10
        match ip address prefix-list PL-LOOPBACKS
        !
        route-map RM-CONN-2-BGP permit 20
        match ip address prefix-list PL-P2P-UNDERLAY
        !
        peer-filter LEAF-AS-RANGE
        10 match as-range 65001-65199 result accept
        !
        ip prefix-list PL-LOOPBACKS seq 10 permit 1.1.1.0/24 eq 32
        ip prefix-list PL-P2P-UNDERLAY seq 10 permit 10.0.0.0/8 le 31
        !
        router bgp 65000
        router-id 1.1.1.201
        no bgp default ipv4-unicast
        maximum-paths 2
        bgp listen range 10.0.0.0/8 peer-group IPv4-UNDERLAY-PEERS peer-filter LEAF-AS-RANGE
        neighbor IPv4-UNDERLAY-PEERS peer group
        neighbor IPv4-UNDERLAY-PEERS password @rista123
        neighbor IPv4-UNDERLAY-PEERS send-community
        neighbor IPv4-UNDERLAY-PEERS maximum-routes 12000 
        redistribute connected route-map RM-CONN-2-BGP
        !
        address-family ipv4
            neighbor IPv4-UNDERLAY-PEERS activate

**SPINE2:**

    .. code-block:: html

        route-map RM-CONN-2-BGP permit 10
        match ip address prefix-list PL-LOOPBACKS
        !
        route-map RM-CONN-2-BGP permit 20
        match ip address prefix-list PL-P2P-UNDERLAY
        !
        peer-filter LEAF-AS-RANGE
        10 match as-range 65001-65199 result accept
        !
        ip prefix-list PL-LOOPBACKS seq 10 permit 1.1.1.0/24 eq 32
        ip prefix-list PL-P2P-UNDERLAY seq 10 permit 10.0.0.0/8 le 31
        !
        router bgp 65000
        router-id 1.1.1.202
        no bgp default ipv4-unicast
        maximum-paths 2
        bgp listen range 10.0.0.0/8 peer-group IPv4-UNDERLAY-PEERS peer-filter LEAF-AS-RANGE
        neighbor IPv4-UNDERLAY-PEERS peer group
        neighbor IPv4-UNDERLAY-PEERS password @rista123
        neighbor IPv4-UNDERLAY-PEERS send-community
        neighbor IPv4-UNDERLAY-PEERS maximum-routes 12000 
        redistribute connected route-map RM-CONN-2-BGP
        !
        address-family ipv4
            neighbor IPv4-UNDERLAY-PEERS activate

**LEAF1:**

    .. code-block:: html

        route-map RM-CONN-2-BGP permit 10
        match ip address prefix-list PL-LOOPBACKS
        !
        route-map RM-CONN-2-BGP permit 20
        match ip address prefix-list PL-P2P-UNDERLAY
        !
        ip prefix-list PL-LOOPBACKS seq 10 permit 1.1.1.0/24 eq 32
        ip prefix-list PL-LOOPBACKS seq 20 permit 2.2.2.0/24 eq 32
        ip prefix-list PL-P2P-UNDERLAY seq 10 permit 10.0.0.0/8 le 31
        !
        router bgp 65012
        router-id 1.1.1.101
        no bgp default ipv4-unicast
        maximum-paths 2
        neighbor IPv4-UNDERLAY-PEERS peer group
        neighbor IPv4-UNDERLAY-PEERS remote-as 65000
        neighbor IPv4-UNDERLAY-PEERS password @rista123
        neighbor IPv4-UNDERLAY-PEERS send-community
        neighbor IPv4-UNDERLAY-PEERS maximum-routes 12000 
        neighbor 10.101.201.201 peer group IPv4-UNDERLAY-PEERS
        neighbor 10.101.202.202 peer group IPv4-UNDERLAY-PEERS
        redistribute connected route-map RM-CONN-2-BGP
        !
        address-family ipv4
            neighbor IPv4-UNDERLAY-PEERS activate

**LEAF2:**

    .. code-block:: html

        route-map RM-CONN-2-BGP permit 10
        match ip address prefix-list PL-LOOPBACKS
        !
        route-map RM-CONN-2-BGP permit 20
        match ip address prefix-list PL-P2P-UNDERLAY
        !
        ip prefix-list PL-LOOPBACKS seq 10 permit 1.1.1.0/24 eq 32
        ip prefix-list PL-LOOPBACKS seq 20 permit 2.2.2.0/24 eq 32
        ip prefix-list PL-P2P-UNDERLAY seq 10 permit 10.0.0.0/8 le 31
        !
        router bgp 65012
        router-id 1.1.1.102
        no bgp default ipv4-unicast
        maximum-paths 2
        neighbor IPv4-UNDERLAY-PEERS peer group
        neighbor IPv4-UNDERLAY-PEERS remote-as 65000
        neighbor IPv4-UNDERLAY-PEERS password @rista123
        neighbor IPv4-UNDERLAY-PEERS send-community
        neighbor IPv4-UNDERLAY-PEERS maximum-routes 12000 
        neighbor 10.102.201.201 peer group IPv4-UNDERLAY-PEERS
        neighbor 10.102.202.202 peer group IPv4-UNDERLAY-PEERS
        redistribute connected route-map RM-CONN-2-BGP
        !
        address-family ipv4
            neighbor IPv4-UNDERLAY-PEERS activate

**LEAF3:**

    .. code-block:: html

        route-map RM-CONN-2-BGP permit 10
        match ip address prefix-list PL-LOOPBACKS
        !
        route-map RM-CONN-2-BGP permit 20
        match ip address prefix-list PL-P2P-UNDERLAY
        !
        ip prefix-list PL-LOOPBACKS seq 10 permit 1.1.1.0/24 eq 32
        ip prefix-list PL-LOOPBACKS seq 20 permit 2.2.2.0/24 eq 32
        ip prefix-list PL-P2P-UNDERLAY seq 10 permit 10.0.0.0/8 le 31
        !
        router bgp 65034
        router-id 1.1.1.103
        no bgp default ipv4-unicast
        maximum-paths 2
        neighbor IPv4-UNDERLAY-PEERS peer group
        neighbor IPv4-UNDERLAY-PEERS remote-as 65000
        neighbor IPv4-UNDERLAY-PEERS password @rista123
        neighbor IPv4-UNDERLAY-PEERS send-community
        neighbor IPv4-UNDERLAY-PEERS maximum-routes 12000 
        neighbor 10.103.201.201 peer group IPv4-UNDERLAY-PEERS
        neighbor 10.103.202.202 peer group IPv4-UNDERLAY-PEERS
        redistribute connected route-map RM-CONN-2-BGP
        !
        address-family ipv4
            neighbor IPv4-UNDERLAY-PEERS activate

**LEAF4:**

    .. code-block:: html

        route-map RM-CONN-2-BGP permit 10
        match ip address prefix-list PL-LOOPBACKS
        !
        route-map RM-CONN-2-BGP permit 20
        match ip address prefix-list PL-P2P-UNDERLAY
        !
        ip prefix-list PL-LOOPBACKS seq 10 permit 1.1.1.0/24 eq 32
        ip prefix-list PL-LOOPBACKS seq 20 permit 2.2.2.0/24 eq 32
        ip prefix-list PL-P2P-UNDERLAY seq 10 permit 10.0.0.0/8 le 31
        !
        router bgp 65034
        router-id 1.1.1.104
        no bgp default ipv4-unicast
        maximum-paths 2
        neighbor IPv4-UNDERLAY-PEERS peer group
        neighbor IPv4-UNDERLAY-PEERS remote-as 65000
        neighbor IPv4-UNDERLAY-PEERS password @rista123
        neighbor IPv4-UNDERLAY-PEERS send-community
        neighbor IPv4-UNDERLAY-PEERS maximum-routes 12000 
        neighbor 10.104.201.201 peer group IPv4-UNDERLAY-PEERS
        neighbor 10.104.202.202 peer group IPv4-UNDERLAY-PEERS
        redistribute connected route-map RM-CONN-2-BGP
        !
        address-family ipv4
            neighbor IPv4-UNDERLAY-PEERS activate

Lab 2: EVPN Control-Plane Provisioning
-------------------------------------------------

**SPINE1 and SPINE2:**

    .. code-block:: html

        router bgp 65000
        bgp listen range 1.1.1.0/24 peer-group EVPN-OVERLAY-PEERS peer-filter LEAF-AS-RANGE
        neighbor EVPN-OVERLAY-PEERS peer group
        neighbor EVPN-OVERLAY-PEERS next-hop-unchanged
        neighbor EVPN-OVERLAY-PEERS update-source Loopback0
        neighbor EVPN-OVERLAY-PEERS bfd
        neighbor EVPN-OVERLAY-PEERS ebgp-multihop 3
        neighbor EVPN-OVERLAY-PEERS password @rista123
        neighbor EVPN-OVERLAY-PEERS send-community
        neighbor EVPN-OVERLAY-PEERS maximum-routes 0 
        !
        address-family evpn
            neighbor EVPN-OVERLAY-PEERS activate

**LEAF1 and LEAF2:**

    .. code-block:: html

        router bgp 65012
        neighbor EVPN-OVERLAY-PEERS peer group
        neighbor EVPN-OVERLAY-PEERS remote-as 65000
        neighbor EVPN-OVERLAY-PEERS update-source Loopback0
        neighbor EVPN-OVERLAY-PEERS bfd
        neighbor EVPN-OVERLAY-PEERS ebgp-multihop 3
        neighbor EVPN-OVERLAY-PEERS password @rista123
        neighbor EVPN-OVERLAY-PEERS send-community
        neighbor EVPN-OVERLAY-PEERS maximum-routes 0 
        neighbor 1.1.1.201 peer group EVPN-OVERLAY-PEERS
        neighbor 1.1.1.202 peer group EVPN-OVERLAY-PEERS
        !
        address-family evpn
            neighbor EVPN-OVERLAY-PEERS activate

**LEAF3 and LEAF4:**

    .. code-block:: html

        router bgp 65034
        neighbor EVPN-OVERLAY-PEERS peer group
        neighbor EVPN-OVERLAY-PEERS remote-as 65000
        neighbor EVPN-OVERLAY-PEERS update-source Loopback0
        neighbor EVPN-OVERLAY-PEERS bfd
        neighbor EVPN-OVERLAY-PEERS ebgp-multihop 3
        neighbor EVPN-OVERLAY-PEERS password @rista123
        neighbor EVPN-OVERLAY-PEERS send-community
        neighbor EVPN-OVERLAY-PEERS maximum-routes 0 
        neighbor 1.1.1.201 peer group EVPN-OVERLAY-PEERS
        neighbor 1.1.1.202 peer group EVPN-OVERLAY-PEERS
        !
        address-family evpn
            neighbor EVPN-OVERLAY-PEERS activate

Lab 3: MLAG
------------------

**LEAF1:**

    .. code-block:: html

        interface Loopback1
        description Shared MLAG VTEP Loopback
        ip address 2.2.2.12/32
        !
        Vlan 4093
        name MLAG_iBGP
        vlan 4094
        name MLAGPEER
        trunk group MLAGPEER
        !
        interface Vlan4093
        description MLAG iBGP Peering
        ip address 192.0.0.1/24
        !
        interface Vlan4094
        description MLAG PEER SYNC
        no autostate
        ip address 10.0.0.1/30
        !
        no spanning-tree vlan-id 4094
        !
        interface Ethernet1
        description MLAG Link to LEAF2
        channel-group 1000 mode active
        !
        interface Port-Channel1000
        description MLAG PEER-LINK
        switchport mode trunk
        switchport trunk group MLAGPEER
        !
        mlag configuration
        domain-id 1000
        local-interface Vlan4094
        peer-address 10.0.0.2
        peer-link Port-Channel1000
        reload-delay mlag 330
        reload-delay non-mlag 300
        !
        interface Ethernet4
        description HostA
        channel-group 10 mode active
        !
        interface Port-Channel10
        mlag 10
        spanning-tree portfast
        !
        interface vxlan1
        Vxlan virtual-router encapsulation mac-address mlag-system-id
        !
        router bgp 65012
        neighbor MLAG-IPv4-UNDERLAY-PEER peer group
        neighbor MLAG-IPv4-UNDERLAY-PEER remote-as 65012
        neighbor MLAG-IPv4-UNDERLAY-PEER next-hop-self
        neighbor MLAG-IPv4-UNDERLAY-PEER password @rista123
        neighbor MLAG-IPv4-UNDERLAY-PEER send-community
        neighbor MLAG-IPv4-UNDERLAY-PEER maximum-routes 12000
        neighbor 192.0.0.2 peer group MLAG-IPv4-UNDERLAY-PEER
        !
        address-family ipv4
            neighbor MLAG-IPv4-UNDERLAY-PEER activate

**LEAF2:**

    .. code-block:: html

        interface Loopback1
        description Shared MLAG VTEP Loopback
        ip address 2.2.2.12/32
        !
        Vlan 4093
        name MLAG_iBGP
        vlan 4094
        name MLAGPEER
        trunk group MLAGPEER
        !
        interface Vlan4093
        description MLAG iBGP Peering
        ip address 192.0.0.2/24
        !
        interface Vlan4094
        description MLAG PEER SYNC
        no autostate
        ip address 10.0.0.2/30
        !
        no spanning-tree vlan-id 4094
        !
        interface Ethernet1
        description MLAG Link to LEAF2
        channel-group 1000 mode active
        !
        interface Port-Channel1000
        description MLAG PEER-LINK
        switchport mode trunk
        switchport trunk group MLAGPEER
        !
        mlag configuration
        domain-id 1000
        local-interface Vlan4094
        peer-address 10.0.0.1
        peer-link Port-Channel1000
        reload-delay mlag 330
        reload-delay non-mlag 300
        !
        interface Ethernet4
        description HostA
        channel-group 10 mode active
        !
        interface Port-Channel10
        mlag 10
        spanning-tree portfast
        !
        interface vxlan1
        Vxlan virtual-router encapsulation mac-address mlag-system-id
        !
        router bgp 65012
        neighbor MLAG-IPv4-UNDERLAY-PEER peer group
        neighbor MLAG-IPv4-UNDERLAY-PEER remote-as 65012
        neighbor MLAG-IPv4-UNDERLAY-PEER next-hop-self
        neighbor MLAG-IPv4-UNDERLAY-PEER password @rista123
        neighbor MLAG-IPv4-UNDERLAY-PEER send-community
        neighbor MLAG-IPv4-UNDERLAY-PEER maximum-routes 12000
        neighbor 192.0.0.1 peer group MLAG-IPv4-UNDERLAY-PEER
        !
        address-family ipv4
            neighbor MLAG-IPv4-UNDERLAY-PEER activate

**LEAF3:**

    .. code-block:: html

        interface Loopback1
        description Shared MLAG VTEP Loopback
        ip address 2.2.2.34/32
        !
        Vlan 4093
        name MLAG_iBGP
        vlan 4094
        name MLAGPEER
        trunk group MLAGPEER
        !
        interface Vlan4093
        description MLAG iBGP Peering
        ip address 192.0.0.1/24
        !
        interface Vlan4094
        description MLAG PEER SYNC
        no autostate
        ip address 10.0.0.1/30
        !
        no spanning-tree vlan-id 4094
        !
        interface Ethernet1
        description MLAG Link to LEAF2
        channel-group 1000 mode active
        !
        interface Port-Channel1000
        description MLAG PEER-LINK
        switchport mode trunk
        switchport trunk group MLAGPEER
        !
        mlag configuration
        domain-id 1000
        local-interface Vlan4094
        peer-address 10.0.0.2
        peer-link Port-Channel1000
        reload-delay mlag 330
        reload-delay non-mlag 300
        !
        interface Ethernet4
        description HostC
        channel-group 20 mode active
        !
        interface Port-Channel20
        mlag 20
        spanning-tree portfast
        !
        interface vxlan1
        Vxlan virtual-router encapsulation mac-address mlag-system-id
        !
        router bgp 65034
        neighbor MLAG-IPv4-UNDERLAY-PEER peer group
        neighbor MLAG-IPv4-UNDERLAY-PEER remote-as 65034
        neighbor MLAG-IPv4-UNDERLAY-PEER next-hop-self
        neighbor MLAG-IPv4-UNDERLAY-PEER password @rista123
        neighbor MLAG-IPv4-UNDERLAY-PEER send-community
        neighbor MLAG-IPv4-UNDERLAY-PEER maximum-routes 12000
        neighbor 192.0.0.2 peer group MLAG-IPv4-UNDERLAY-PEER
        !
        address-family ipv4
            neighbor MLAG-IPv4-UNDERLAY-PEER activate

**LEAF4:**

    .. code-block:: html

        interface Loopback1
        description Shared MLAG VTEP Loopback
        ip address 2.2.2.34/32
        !
        Vlan 4093
        name MLAG_iBGP
        vlan 4094
        name MLAGPEER
        trunk group MLAGPEER
        !
        interface Vlan4093
        description MLAG iBGP Peering
        ip address 192.0.0.2/24
        !
        interface Vlan4094
        description MLAG PEER SYNC
        no autostate
        ip address 10.0.0.2/30
        !
        no spanning-tree vlan-id 4094
        !
        interface Ethernet1
        description MLAG Link to LEAF2
        channel-group 1000 mode active
        !
        interface Port-Channel1000
        description MLAG PEER-LINK
        switchport mode trunk
        switchport trunk group MLAGPEER
        !
        mlag configuration
        domain-id 1000
        local-interface Vlan4094
        peer-address 10.0.0.1
        peer-link Port-Channel1000
        reload-delay mlag 330
        reload-delay non-mlag 300
        !
        interface Ethernet4
        description HostC
        channel-group 20 mode active
        !
        interface Port-Channel20
        mlag 20
        spanning-tree portfast
        !
        interface vxlan1
        Vxlan virtual-router encapsulation mac-address mlag-system-id
        !
        router bgp 65034
        neighbor MLAG-IPv4-UNDERLAY-PEER peer group
        neighbor MLAG-IPv4-UNDERLAY-PEER remote-as 65034
        neighbor MLAG-IPv4-UNDERLAY-PEER next-hop-self
        neighbor MLAG-IPv4-UNDERLAY-PEER password @rista123
        neighbor MLAG-IPv4-UNDERLAY-PEER send-community
        neighbor MLAG-IPv4-UNDERLAY-PEER maximum-routes 12000
        neighbor 192.0.0.1 peer group MLAG-IPv4-UNDERLAY-PEER
        !
        address-family ipv4
            neighbor MLAG-IPv4-UNDERLAY-PEER activate

Lab 4: Layer2 VPN Service Provisioning
------------------------------------------

**LEAF1:**

    .. code-block:: html

        interface Vxlan1
        vxlan source-interface Loopback1
        vxlan udp-port 4789
        vxlan vlan 10-30 vni 10010-10030
        !
        vlan 10
        name Ten
        vlan 20
        name Twenty
        !
        router bgp 65012
        vlan-aware-bundle TENANT-A
            rd 1.1.1.101:1
            route-target both 1:1
            redistribute learned
            vlan 10-30
        !
        interface Port-Channel10
        switchport access vlan 10
        mlag 10
        spanning-tree portfast
        !
        interface Ethernet5
        switchport access vlan 20

**LEAF2:**

    .. code-block:: html

        interface Vxlan1
        vxlan source-interface Loopback1
        vxlan udp-port 4789
        vxlan vlan 10-30 vni 10010-10030
        !
        vlan 10
        name Ten
        vlan 20
        name Twenty
        !
        router bgp 65012
        vlan-aware-bundle TENANT-A
            rd 1.1.1.102:1
            route-target both 1:1
            redistribute learned
            vlan 10-30
        !
        interface Port-Channel10
        switchport access vlan 10
        mlag 10
        spanning-tree portfast
        !
        interface Ethernet5
        switchport access vlan 20

**LEAF3:**

    .. code-block:: html

        interface Vxlan1
        vxlan source-interface Loopback1
        vxlan udp-port 4789
        vxlan vlan 10-30 vni 10010-10030
        !
        vlan 10
        name Ten
        vlan 30
        name Thirty
        !
        router bgp 65034
        vlan-aware-bundle TENANT-A
            rd 1.1.1.103:1
            route-target both 1:1
            redistribute learned
            vlan 10-30
        !
        interface Port-Channel20
        switchport access vlan 30
        mlag 20
        spanning-tree portfast
        !
        interface Ethernet5
        switchport access vlan 10

**LEAF4:**

    .. code-block:: html

        interface Vxlan1
        vxlan source-interface Loopback1
        vxlan udp-port 4789
        vxlan vlan 10-30 vni 10010-10030
        !
        vlan 10
        name Ten
        vlan 30
        name Thirty
        !
        router bgp 65034
        vlan-aware-bundle TENANT-A
            rd 1.1.1.104:1
            route-target both 1:1
            redistribute learned
            vlan 10-30
        !
        interface Port-Channel20
        switchport access vlan 30
        mlag 20
        spanning-tree portfast
        !
        interface Ethernet5
        switchport access vlan 10

Lab 5: Layer3 VPN Service Provisioning
-----------------------------------------

**LEAF1:**

    .. code-block:: html

        ip virtual-router mac-address aaaa.bbbb.cccc
        !
        vrf instance A
        !
        ip routing vrf A
        !
        interface vlan10
        vrf A
        ip address virtual 10.10.10.1/24
        !
        interface vlan20
        vrf A
        ip address virtual 20.20.20.1/24
        !  
        interface Vxlan1
        vxlan vrf A vni 50001
        !
        router bgp 65012
        vrf A
            rd 1.1.1.101:1
            route-target import evpn 1:1
            route-target export evpn 1:1
            redistribute connected
        !
        router l2-vpn
        arp selective-install

**LEAF2:**

    .. code-block:: html

        ip virtual-router mac-address aaaa.bbbb.cccc
        !
        vrf instance A
        !
        ip routing vrf A
        !
        interface vlan10
        vrf A
        ip address virtual 10.10.10.1/24
        !
        interface vlan20
        vrf A
        ip address virtual 20.20.20.1/24
        !  
        interface Vxlan1
        vxlan vrf A vni 50001
        !
        router bgp 65012
        vrf A
            rd 1.1.1.102:1
            route-target import evpn 1:1
            route-target export evpn 1:1
            redistribute connected
        !
        router l2-vpn
        arp selective-install

**LEAF3:**

    .. code-block:: html

        ip virtual-router mac-address aaaa.bbbb.cccc
        !
        vrf instance A
        !
        ip routing vrf A
        !
        interface vlan10
        vrf A
        ip address virtual 10.10.10.1/24
        !
        interface vlan30
        vrf A
        ip address virtual 30.30.30.1/24
        !  
        interface Vxlan1
        vxlan vrf A vni 50001
        !
        router bgp 65034
        vrf A
            rd 1.1.1.103:1
            route-target import evpn 1:1
            route-target export evpn 1:1
            redistribute connected
        !
        router l2-vpn
        arp selective-install

**LEAF4:**

    .. code-block:: html

        ip virtual-router mac-address aaaa.bbbb.cccc
        !
        vrf instance A
        !
        ip routing vrf A
        !
        interface vlan10
        vrf A
        ip address virtual 10.10.10.1/24
        !
        interface vlan30
        vrf A
        ip address virtual 30.30.30.1/24
        !
        interface Vxlan1
        vxlan vrf A vni 50001
        !
        router bgp 65034
        vrf A
            rd 1.1.1.104:1
            route-target import evpn 1:1
            route-target export evpn 1:1
            redistribute connected
        !
        router l2-vpn
        arp selective-install

Lab 6: Day-2 Ops
------------------

**Section A:**

LEAF1-4:

    .. code-block:: html

        vlan 25
        name Twenty-Five

LEAF1:

    .. code-block:: html

        interface Ethernet6
        switchport access vlan 25

**Section B:**

LEAF1:

    .. code-block:: html

        vlan 35
        name Thirty-Five
        vlan 40
        name Forty
        !
        vrf instance B
        !
        ip routing vrf B
        !
        interface Vxlan1
        vxlan vlan add 31-40 vni 10031-10040
        vxlan vrf B vni 50002
        !
        interface vlan35
        vrf B
        ip address virtual 35.35.35.1/24
        !
        interface vlan40
        vrf B
        ip address virtual 40.40.40.1/24
        !
        router bgp 65012
        vlan-aware-bundle TENANT-B
            rd 1.1.1.101:2
            route-target both 2:2
            redistribute learned
            vlan 31-40
        !
        vrf B
            rd 1.1.1.101:2
            route-target import evpn 2:2
            route-target export evpn 2:2
            redistribute connected


LEAF2:

    .. code-block:: html

        vlan 35
        name Thirty-Five
        vlan 40
        name Forty
        !
        vrf instance B
        !
        ip routing vrf B
        !
        interface Vxlan1
        vxlan vlan add 31-40 vni 10031-10040
        vxlan vrf B vni 50002
        !
        interface vlan35
        vrf B
        ip address virtual 35.35.35.1/24
        !
        interface vlan40
        vrf B
        ip address virtual 40.40.40.1/24
        !
        router bgp 65012
        vlan-aware-bundle TENANT-B
            rd 1.1.1.102:2
            route-target both 2:2
            redistribute learned
            vlan 31-40
        !
        vrf B
            rd 1.1.1.102:2
            route-target import evpn 2:2
            route-target export evpn 2:2
            redistribute connected

LEAF3:

    .. code-block:: html

        vlan 35
        name Thirty-Five
        vlan 40
        name Forty
        !
        vrf instance B
        !
        ip routing vrf B
        !
        interface Vxlan1
        vxlan vlan add 31-40 vni 10031-10040
        vxlan vrf B vni 50002
        !
        interface vlan35
        vrf B
        ip address virtual 35.35.35.1/24
        !
        interface vlan40
        vrf B
        ip address virtual 40.40.40.1/24
        !
        router bgp 65034
        vlan-aware-bundle TENANT-B
            rd 1.1.1.103:2
            route-target both 2:2
            redistribute learned
            vlan 31-40
        !
        vrf B
            rd 1.1.1.103:2
            route-target import evpn 2:2
            route-target export evpn 2:2
            redistribute connected

LEAF4:

    .. code-block:: html

        vlan 35
        name Thirty-Five
        vlan 40
        name Forty
        !
        vrf instance B
        !
        ip routing vrf B
        !
        interface Vxlan1
        vxlan vlan add 31-40 vni 10031-10040
        vxlan vrf B vni 50002
        !
        interface vlan35
        vrf B
        ip address virtual 35.35.35.1/24
        !
        interface vlan40
        vrf B
        ip address virtual 40.40.40.1/24
        !
        router bgp 65034
        vlan-aware-bundle TENANT-B
            rd 1.1.1.104:2
            route-target both 2:2
            redistribute learned
            vlan 31-40
        !
        vrf B
            rd 1.1.1.104:2
            route-target import evpn 2:2
            route-target export evpn 2:2
            redistribute connected



**Section C:**

LEAF1:

    .. code-block:: html

        interface Loopback201
        vrf A
        ip address 201.0.0.101/32
        !
        ip address virtual source-nat vrf A address 201.0.0.101

LEAF2:

    .. code-block:: html

        interface Loopback201
        vrf A
        ip address 201.0.0.102/32
        !
        ip address virtual source-nat vrf A address 201.0.0.102

LEAF3:

    .. code-block:: html

        interface Loopback201
        vrf A
        ip address 201.0.0.103/32
        !
        ip address virtual source-nat vrf A address 201.0.0.103 

LEAF4:

    .. code-block:: html

        interface Loopback201
        vrf A
        ip address 201.0.0.104/32
        !
        ip address virtual source-nat vrf A address 201.0.0.104