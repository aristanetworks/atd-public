L3 EVPN
=======

.. thumbnail:: images/l3evpn/nested_l3evpn_topo_dual_dc.png
   :align: center

      Click image to enlarge``

.. note:: 
  - This lab exercise is focused on the EVPN-VXLAN configuration for EVPN L3 services (Symmetric IRB).
  - The goal is to provide inter-subnet routing capability between 2 subnets belonging to the same VRF.
  - IP addresses, MLAG and BGP Underlay are already configured.

1. Log into the  **LabAccess**  jumpserver:

   Type ``l3evpn`` at the prompt. The script will configure the datacenter with the exception of **s1-leaf4**

#. On **s1-leaf4**, check if ArBGP is configured.

   .. code-block:: text
      :emphasize-lines: 1,2

       s1-leaf4#sh run section service
       service routing protocols model multi-agent

   .. note:: By default, EOS is using GateD routing process. Activating ArBGP is requiring a reboot.``

#. On **s1-leaf4**, check the following operational states before configuring EVPN constructs:

   a. Verify EOS MLAG operational details.

      .. code-block:: text
         :emphasize-lines: 1
      
          s1-leaf4#show mlag
          MLAG Configuration:              
          domain-id                          :                MLAG
          local-interface                    :            Vlan4094
          peer-address                       :        10.255.255.1
          peer-link                          :       Port-Channel1
          peer-config                        :        inconsistent

          MLAG Status:                     
          state                              :              Active
          negotiation status                 :           Connected
          peer-link status                   :                  Up
          local-int status                   :                  Up
          system-id                          :   02:1c:73:c0:c6:14
          dual-primary detection             :            Disabled
          dual-primary interface errdisabled :               False
                                                              
          MLAG Ports:                      
          Disabled                           :                   0
          Configured                         :                   0
          Inactive                           :                   0
          Active-partial                     :                   0
          Active-full                        :                   1

          s1-leaf4#show mlag interfaces 
                                                                                      local/remote
            mlag       desc                                 state       local       remote          status
          ---------- ------------------------------ ----------------- ----------- ------------ ------------
                5       MLAG Downlink - s1-host2       active-full         Po5          Po5           up/up
          
   b. Verify BGP operational details for Underlay:
   
      .. code-block:: text
         :emphasize-lines: 1

          s1-leaf4(config-router-bgp)#sh ip bgp summary
          BGP summary information for VRF default
          Router identifier 10.111.254.4, local AS number 65102
         Neighbor Status Codes: m - Under maintenance
         Neighbor     V AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State   PfxRcd PfxAcc
         10.111.1.6   4 65100              9        12    0    0 00:00:07 Estab   6      6
         10.111.2.6   4 65100              9        12    0    0 00:00:07 Estab   5      5
         10.255.255.1 4 65102              8        10    0    0 00:00:07 Estab   10     10  
    
      .. note:: You might see 3 underlay sessions.

   c. Check the ip routing table:

      .. code-block:: text
         :emphasize-lines: 1,25,26,28,29,30,31

          s1-leaf4(config-router-bgp)#sh ip route

          VRF: default
          Codes: C - connected, S - static, K - kernel, 
                O - OSPF, IA - OSPF inter area, E1 - OSPF external type 1,
                E2 - OSPF external type 2, N1 - OSPF NSSA external type 1,
                N2 - OSPF NSSA external type2, B - Other BGP Routes,
                B I - iBGP, B E - eBGP, R - RIP, I L1 - IS-IS level 1,
                I L2 - IS-IS level 2, O3 - OSPFv3, A B - BGP Aggregate,
                A O - OSPF Summary, NG - Nexthop Group Static Route,
                V - VXLAN Control Service, M - Martian,
                DH - DHCP client installed default route,
                DP - Dynamic Policy Route, L - VRF Leaked,
                G  - gRIBI, RC - Route Cache Route

          Gateway of last resort is not set

          B E      10.111.0.1/32 [200/0] via 10.111.1.6, Ethernet2
          B E      10.111.0.2/32 [200/0] via 10.111.2.6, Ethernet3
          C        10.111.1.6/31 is directly connected, Ethernet2
          B E      10.111.1.0/24 [200/0] via 10.111.1.6, Ethernet2
          C        10.111.2.6/31 is directly connected, Ethernet3
          B E      10.111.2.0/24 [200/0] via 10.111.2.6, Ethernet3
          B I      10.111.112.0/24 [200/0] via 10.255.255.1, Vlan4094
          B E      10.111.253.1/32 [200/0] via 10.111.1.6, Ethernet2
                                           via 10.111.2.6, Ethernet3
          B I      10.111.253.3/32 [200/0] via 10.255.255.1, Vlan4094
          B E      10.111.254.1/32 [200/0] via 10.111.1.6, Ethernet2
                                           via 10.111.2.6, Ethernet3
          B E      10.111.254.2/32 [200/0] via 10.111.1.6, Ethernet2
                                           via 10.111.2.6, Ethernet3
          B I      10.111.254.3/32 [200/0] via 10.255.255.1, Vlan4094
          C        10.111.254.4/32 is directly connected, Loopback0
          C        10.255.255.0/30 is directly connected, Vlan4094
          C        192.168.0.0/24 is directly connected, Management0

      .. note:: You can notice that s1-leaf4 has 2 paths for reaching s1-leaf1 or s1-leaf2 loopacks.

#. On **s1-leaf4**, build the control-plane and the data-plane:
   
   a. Configure the EVPN control plane: 

      .. code-block:: html

        router bgp 65102
           neighbor SPINE-EVPN peer group
           neighbor SPINE-EVPN remote-as 65100
           neighbor SPINE-EVPN update-source Loopback0
           neighbor SPINE-EVPN ebgp-multihop 3
           neighbor SPINE-EVPN send-community standard extended
           neighbor 10.111.0.1 peer group SPINE-EVPN
           neighbor 10.111.0.2 peer group SPINE-EVPN
           !
           address-family evpn
              neighbor SPINE-EVPN activate

      .. note:: 
        - BGP EVPN session will use interface Loopback0
        - Extended community have to be activated in order to manage BGP EVPN NLRI 

   #. Check the EVPN control plane: 

      .. code-block:: text
         :emphasize-lines: 1

         s1-leaf4(config-router-bgp)#sh bgp evpn summary 
         BGP summary information for VRF default
         Router identifier 10.111.254.4, local AS number 65102
         Neighbor Status Codes: m - Under maintenance
         Neighbor   V AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State   PfxRcd PfxAcc
         10.111.0.1 4 65100              6         5    0    0 00:00:03 Estab   2      2
         10.111.0.2 4 65100              6         4    0    0 00:00:03 Estab   2      2

      .. note:: Two EVPN sessions are now established toward the spines.

   #. Configure the interface Vxlan with the appropriate Loopback1: 

      .. code-block:: html

         interface Vxlan1
            vxlan source-interface Loopback1

   #. Check the Vxlan dataplane:
   
      .. code-block:: text
         :emphasize-lines: 1,2

         s1-leaf4(config-if-Vx1)#sh int vxlan 1
         Vxlan1 is down, line protocol is down (notconnect)
         Hardware is Vxlan
         Source interface is Loopback1 and is active with 10.111.253.3
         Replication/Flood Mode is not initialized yet
         Remote MAC learning via Datapath
         VNI mapping to VLANs
         Static VLAN to VNI mapping is not configured
         Static VRF to VNI mapping is not configured
         MLAG Shared Router MAC is 0000.0000.0000
      
      .. note:: Interface Vxlan1 is still inactive until L2 or L3 services will be added.

#. Configure L3EVPN service on **s1-leaf4**

   a. Configure the VRF

      .. code-block:: text

         vrf instance TENANT
         !
         ip routing vrf TENANT
         !
         router bgp 65102
            rd auto
            vrf TENANT
               route-target import evpn 5001:5001
               route-target export evpn 5001:5001
               redistribute connected
         !

   #. Configure vrf interfaces (start in global configuration mode not BGP)

      .. code-block:: text

         vlan 134
         !
         interface Vlan134
            description Host Network
            vrf TENANT
            ip address virtual 10.111.134.1/24
         !
         interface vxlan 1
            vxlan vlan 134 vni 134
         !

      .. note:: 
        - `ip address virtual` is generally used to conserve IP addresses in VXLAN deployments and can be used to provide an Anycast gateway.
        - An alternative is to use `ip virtual router` to avoid the provisioning of a VXLAN for `vlan 134` - Please consult the Aristat documentation for further details.

   #. Map VRF to VNI

      .. code-block:: text

         interface Vxlan1
            vxlan source-interface Loopback1
            vxlan virtual-router encapsulation mac-address mlag-system-id
            vxlan vrf TENANT vni 5001
         !

      .. note::
          - this is S-IRB setup : a specific "L3" VNI is associated to "TENANT" vrf.
          - all "routed" flows between leafs will be encapsulated with VNI 5001
          - `vxlan virtual-router encapsulation mac-address mlag-system-id` is for faster convergence and avoid unnecessary peer-link crossing 

   #. Check the interface Vxlan config

      .. code-block:: text
        :emphasize-lines: 1,14,15

        s1-leaf4#sh vxlan config-sanity detail 
        Category                            Result  Detail                                            
        ---------------------------------- -------- --------------------------------------------------
        Local VTEP Configuration Check        OK                                                      
          Loopback IP Address                 OK                                                      
          VLAN-VNI Map                        OK                                                      
          Routing                             OK                                                      
          VNI VRF ACL                         OK                                                      
          Decap VRF-VNI Map                   OK                                                      
          VRF-VNI Dynamic VLAN                OK                                                      
        Remote VTEP Configuration Check       OK                                                      
          Remote VTEP                         OK                                                      
        Platform Dependent Check              OK                                                      
          VXLAN Bridging                      OK                                                      
          VXLAN Routing                       OK                             
        CVX Configuration Check               OK                                                      
          CVX Server                          OK    Not in controller client mode                     
        MLAG Configuration Check              OK    Run 'show mlag config-sanity' to verify MLAG config
          Peer VTEP IP                        OK                                                      
          MLAG VTEP IP                        OK                                                      
          Peer VLAN-VNI                       OK                                                      
          Virtual VTEP IP                     OK

   #. Check the VXLAN dataplane

      .. code-block:: text
        :emphasize-lines: 1,9,11,15

        s1-leaf4#show interfaces vxlan 1
        Vxlan1 is up, line protocol is up (connected)
          Hardware is Vxlan
          Source interface is Loopback1 and is active with 10.111.253.3
          Replication/Flood Mode is headend with Flood List Source: EVPN
          Remote MAC learning via EVPN
          VNI mapping to VLANs
          Static VLAN to VNI mapping is 
            [134, 134]       
          Dynamic VLAN to VNI mapping for 'evpn' is
            [4093, 5001]     
          Note: All Dynamic VLANs used by VCS are internal VLANs.
                Use 'show vxlan vni' for details.
          Static VRF to VNI mapping is 
          [TENANT, 5001]
          MLAG Shared Router MAC is 021c.73c0.c614

      .. note::
        - EOS has allocated a dynamic VLAN to the L3 VNI for internal purposes (range is configurable)
        - we can notice the VRF/VNI asociation as well as the vlan/VNI association

#. Verify VXLAN and EVPN

   #. On **s1-leaf1** and **s1-leaf3** (and/or **s1-leaf2/4**) verify BGP EVPN control plane for RT-5

      .. code-block:: text
        :emphasize-lines: 1,11

        s1-leaf1#sh bgp evpn route-type ip-prefix ipv4 detail 
        BGP routing table information for VRF default
        Router identifier 10.111.254.1, local AS number 65101
        BGP routing table entry for ip-prefix 10.111.112.0/24, Route Distinguisher: 10.111.254.1:1
        Paths: 1 available
          Local
            - from - (0.0.0.0)
              Origin IGP, metric -, localpref -, weight 0, valid, local, best, redistributed (Connected)
              Extended Community: Route-Target-AS:5001:5001 TunnelEncap:tunnelTypeVxlan EvpnRouterMac:02:1c:73:c0:c6:12
              VNI: 5001
        BGP routing table entry for ip-prefix 10.111.134.0/24, Route Distinguisher: 10.111.254.3:1
        Paths: 2 available
          65100 65102
            10.111.253.3 from 10.111.0.1 (10.111.0.1)
              Origin IGP, metric -, localpref 100, weight 0, valid, external, ECMP head, ECMP, best, ECMP contributor
              Extended Community: Route-Target-AS:5001:5001 TunnelEncap:tunnelTypeVxlan EvpnRouterMac:02:1c:73:c0:c6:14
              VNI: 5001
          65100 65102
            10.111.253.3 from 10.111.0.2 (10.111.0.2)
              Origin IGP, metric -, localpref 100, weight 0, valid, external, ECMP, ECMP contributor
              Extended Community: Route-Target-AS:5001:5001 TunnelEncap:tunnelTypeVxlan EvpnRouterMac:02:1c:73:c0:c6:14
              VNI: 5001
        BGP routing table entry for ip-prefix 10.111.134.0/24, Route Distinguisher: 10.111.254.4:1
        Paths: 2 available
          65100 65102
            10.111.253.3 from 10.111.0.2 (10.111.0.2)
              Origin IGP, metric -, localpref 100, weight 0, valid, external, ECMP head, ECMP, best, ECMP contributor
              Extended Community: Route-Target-AS:5001:5001 TunnelEncap:tunnelTypeVxlan EvpnRouterMac:02:1c:73:c0:c6:14
              VNI: 5001
          65100 65102
            10.111.253.3 from 10.111.0.1 (10.111.0.1)
              Origin IGP, metric -, localpref 100, weight 0, valid, external, ECMP, ECMP contributor
              Extended Community: Route-Target-AS:5001:5001 TunnelEncap:tunnelTypeVxlan EvpnRouterMac:02:1c:73:c0:c6:14
              VNI: 5001

      .. note::
        - **s1-leaf4** is learning `10.111.134.0/24` from `10.111.254.3` and `10.111.254.4` with RT-5 EVPN message
        - Please note the `TunnelTypeVxlan`, the `EvpnRouterMac` and the L3 `VNI` values for each entries              

      .. code-block:: text
        :emphasize-lines: 1,4

        s1-leaf3#sh bgp evpn route-type ip-prefix ipv4 detail 
        BGP routing table information for VRF default
        Router identifier 10.111.254.3, local AS number 65102
        BGP routing table entry for ip-prefix 10.111.112.0/24, Route Distinguisher: 10.111.254.1:1
        Paths: 2 available
          65100 65101
            10.111.253.1 from 10.111.0.1 (10.111.0.1)
              Origin IGP, metric -, localpref 100, weight 0, valid, external, ECMP head, ECMP, best, ECMP contributor
              Extended Community: Route-Target-AS:5001:5001 TunnelEncap:tunnelTypeVxlan EvpnRouterMac:02:1c:73:c0:c6:12
              VNI: 5001
          65100 65101
            10.111.253.1 from 10.111.0.2 (10.111.0.2)
              Origin IGP, metric -, localpref 100, weight 0, valid, external, ECMP, ECMP contributor
              Extended Community: Route-Target-AS:5001:5001 TunnelEncap:tunnelTypeVxlan EvpnRouterMac:02:1c:73:c0:c6:12
              VNI: 5001
        BGP routing table entry for ip-prefix 10.111.112.0/24, Route Distinguisher: 10.111.254.2:1
        Paths: 2 available
          65100 65101
            10.111.253.1 from 10.111.0.1 (10.111.0.1)
              Origin IGP, metric -, localpref 100, weight 0, valid, external, ECMP head, ECMP, best, ECMP contributor
              Extended Community: Route-Target-AS:5001:5001 TunnelEncap:tunnelTypeVxlan EvpnRouterMac:02:1c:73:c0:c6:12
              VNI: 5001
          65100 65101
            10.111.253.1 from 10.111.0.2 (10.111.0.2)
              Origin IGP, metric -, localpref 100, weight 0, valid, external, ECMP, ECMP contributor
              Extended Community: Route-Target-AS:5001:5001 TunnelEncap:tunnelTypeVxlan EvpnRouterMac:02:1c:73:c0:c6:12
              VNI: 5001
        BGP routing table entry for ip-prefix 10.111.134.0/24, Route Distinguisher: 10.111.254.3:1
        Paths: 1 available
          Local
            - from - (0.0.0.0)
              Origin IGP, metric -, localpref -, weight 0, valid, local, best, redistributed (Connected)
              Extended Community: Route-Target-AS:5001:5001 TunnelEncap:tunnelTypeVxlan EvpnRouterMac:02:1c:73:c0:c6:14
              VNI: 5001

      .. note::
        - **s1-leaf3** is learning `10.111.112.0/24` from `10.111.254.1` and `10.111.254.2` with RT-5 EVPN message
        - Please note the `TunnelTypeVxlan`, the `EvpnRouterMac` and the L3 `VNI` values for each entries

   #. On **s1-leaf1** and **s1-leaf3** (and/or **s1-leaf2/4**) verify the IP routing table for vrf TENANT

      .. code-block:: text
        :emphasize-lines: 1,19

        s1-leaf1#sh ip route vrf TENANT 

        VRF: TENANT
        Codes: C - connected, S - static, K - kernel, 
              O - OSPF, IA - OSPF inter area, E1 - OSPF external type 1,
              E2 - OSPF external type 2, N1 - OSPF NSSA external type 1,
              N2 - OSPF NSSA external type2, B - Other BGP Routes,
              B I - iBGP, B E - eBGP, R - RIP, I L1 - IS-IS level 1,
              I L2 - IS-IS level 2, O3 - OSPFv3, A B - BGP Aggregate,
              A O - OSPF Summary, NG - Nexthop Group Static Route,
              V - VXLAN Control Service, M - Martian,
              DH - DHCP client installed default route,
              DP - Dynamic Policy Route, L - VRF Leaked,
              G  - gRIBI, RC - Route Cache Route

        Gateway of last resort is not set

        C        10.111.112.0/24 is directly connected, Vlan112
        B E      10.111.134.0/24 [200/0] via VTEP 10.111.253.3 VNI 5001 router-mac 02:1c:73:c0:c6:14 local-interface Vxlan1

      .. note::
        - remote prefixe `10.111.134.0/24` is reachable via logical VTEP `10.111.253.3` with VNI 5001

      .. code-block:: text
        :emphasize-lines: 1,18

        s1-leaf3#sh ip route vrf TENANT 

        VRF: TENANT
        Codes: C - connected, S - static, K - kernel, 
              O - OSPF, IA - OSPF inter area, E1 - OSPF external type 1,
              E2 - OSPF external type 2, N1 - OSPF NSSA external type 1,
              N2 - OSPF NSSA external type2, B - Other BGP Routes,
              B I - iBGP, B E - eBGP, R - RIP, I L1 - IS-IS level 1,
              I L2 - IS-IS level 2, O3 - OSPFv3, A B - BGP Aggregate,
              A O - OSPF Summary, NG - Nexthop Group Static Route,
              V - VXLAN Control Service, M - Martian,
              DH - DHCP client installed default route,
              DP - Dynamic Policy Route, L - VRF Leaked,
              G  - gRIBI, RC - Route Cache Route

        Gateway of last resort is not set

        B E      10.111.112.0/24 [200/0] via VTEP 10.111.253.1 VNI 5001 router-mac 02:1c:73:c0:c6:12 local-interface Vxlan1
        C        10.111.134.0/24 is directly connected, Vlan134

      .. note::
        - remote prefixe `10.111.112.0/24` is reachable via logical VTEP `10.111.253.1` with VNI 5001

   #. Log into **s1-host1** and ping **s2-host2**

      .. code-block:: text
        :emphasize-lines: 1

        s1-host1#ping 10.111.134.202
        PING 10.111.134.202 (10.111.134.202) 72(100) bytes of data.
        80 bytes from 10.111.134.202: icmp_seq=1 ttl=62 time=33.1 ms
        80 bytes from 10.111.134.202: icmp_seq=2 ttl=62 time=37.0 ms
        80 bytes from 10.111.134.202: icmp_seq=3 ttl=62 time=43.2 ms
        80 bytes from 10.111.134.202: icmp_seq=4 ttl=62 time=34.6 ms
        80 bytes from 10.111.134.202: icmp_seq=5 ttl=62 time=16.7 ms
        --- 10.111.134.202 ping statistics ---
        5 packets transmitted, 5 received, 0% packet loss, time 65ms

   #. Log into **s1-leaf3** and check the IP routing table

      .. code-block:: text
        :emphasize-lines: 1,17

        s1-leaf3#show ip route vrf TENANT
        VRF: TENANT
        Codes: C - connected, S - static, K - kernel,
              O - OSPF, IA - OSPF inter area, E1 - OSPF external type 1,
              E2 - OSPF external type 2, N1 - OSPF NSSA external type 1,
              N2 - OSPF NSSA external type2, B - Other BGP Routes,
              B I - iBGP, B E - eBGP, R - RIP, I L1 - IS-IS level 1,
              I L2 - IS-IS level 2, O3 - OSPFv3, A B - BGP Aggregate,
              A O - OSPF Summary, NG - Nexthop Group Static Route,
              V - VXLAN Control Service, M - Martian,
              DH - DHCP client installed default route,
              DP - Dynamic Policy Route, L - VRF Leaked,
              G  - gRIBI, RC - Route Cache Route

        Gateway of last resort is not set

        B E      10.111.112.201/32 [200/0] via VTEP 10.111.253.1 VNI 5001 router-mac 02:1c:73:c0:c6:12 local-interface Vxlan1
        B E      10.111.112.0/24 [200/0] via VTEP 10.111.253.1 VNI 5001 router-mac 02:1c:73:c0:c6:12 local-interface Vxlan1
        C        10.111.134.0/24 is directly connected, Vlan134

      .. note::
        - You can notice that a "new route" is now programmed corresponding to `s1-host1` : `10.111.112.201/32`

   #. Always on **s1-leaf3**, check now the BGP EVPN control plane for RT-2 

      .. code-block:: text
        :emphasize-lines: 1,28,40

        s1-leaf3#show bgp evpn route-type mac-ip detail 
        BGP routing table information for VRF default
        Router identifier 10.111.254.3, local AS number 65102
        BGP routing table entry for mac-ip 001c.73c0.c616, Route Distinguisher: 10.111.254.1:112
        Paths: 2 available
          65100 65101
            10.111.253.1 from 10.111.0.2 (10.111.0.2)
              Origin IGP, metric -, localpref 100, weight 0, valid, external, ECMP head, ECMP, best, ECMP contributor
              Extended Community: Route-Target-AS:112:112 TunnelEncap:tunnelTypeVxlan
              VNI: 112 ESI: 0000:0000:0000:0000:0000
          65100 65101
            10.111.253.1 from 10.111.0.1 (10.111.0.1)
              Origin IGP, metric -, localpref 100, weight 0, valid, external, ECMP, ECMP contributor
              Extended Community: Route-Target-AS:112:112 TunnelEncap:tunnelTypeVxlan
              VNI: 112 ESI: 0000:0000:0000:0000:0000
        BGP routing table entry for mac-ip 001c.73c0.c616, Route Distinguisher: 10.111.254.2:112
        Paths: 2 available
          65100 65101
            10.111.253.1 from 10.111.0.2 (10.111.0.2)
              Origin IGP, metric -, localpref 100, weight 0, valid, external, ECMP head, ECMP, best, ECMP contributor
              Extended Community: Route-Target-AS:112:112 TunnelEncap:tunnelTypeVxlan
              VNI: 112 ESI: 0000:0000:0000:0000:0000
          65100 65101
            10.111.253.1 from 10.111.0.1 (10.111.0.1)
              Origin IGP, metric -, localpref 100, weight 0, valid, external, ECMP, ECMP contributor
              Extended Community: Route-Target-AS:112:112 TunnelEncap:tunnelTypeVxlan
              VNI: 112 ESI: 0000:0000:0000:0000:0000
        BGP routing table entry for mac-ip 001c.73c0.c616 10.111.112.201, Route Distinguisher: 10.111.254.1:112
        Paths: 2 available
          65100 65101
            10.111.253.1 from 10.111.0.2 (10.111.0.2)
              Origin IGP, metric -, localpref 100, weight 0, valid, external, ECMP head, ECMP, best, ECMP contributor
              Extended Community: Route-Target-AS:112:112 Route-Target-AS:5001:5001 TunnelEncap:tunnelTypeVxlan EvpnRouterMac:02:1c:73:c0:c6:12
              VNI: 112 L3 VNI: 5001 ESI: 0000:0000:0000:0000:0000
          65100 65101
            10.111.253.1 from 10.111.0.1 (10.111.0.1)
              Origin IGP, metric -, localpref 100, weight 0, valid, external, ECMP, ECMP contributor
              Extended Community: Route-Target-AS:112:112 Route-Target-AS:5001:5001 TunnelEncap:tunnelTypeVxlan EvpnRouterMac:02:1c:73:c0:c6:12
              VNI: 112 L3 VNI: 5001 ESI: 0000:0000:0000:0000:0000
        BGP routing table entry for mac-ip 001c.73c0.c616 10.111.112.201, Route Distinguisher: 10.111.254.2:112
        Paths: 2 available
          65100 65101
            10.111.253.1 from 10.111.0.2 (10.111.0.2)
              Origin IGP, metric -, localpref 100, weight 0, valid, external, ECMP head, ECMP, best, ECMP contributor
              Extended Community: Route-Target-AS:112:112 Route-Target-AS:5001:5001 TunnelEncap:tunnelTypeVxlan EvpnRouterMac:02:1c:73:c0:c6:12
              VNI: 112 L3 VNI: 5001 ESI: 0000:0000:0000:0000:0000
          65100 65101
            10.111.253.1 from 10.111.0.1 (10.111.0.1)
              Origin IGP, metric -, localpref 100, weight 0, valid, external, ECMP, ECMP contributor
              Extended Community: Route-Target-AS:112:112 Route-Target-AS:5001:5001 TunnelEncap:tunnelTypeVxlan EvpnRouterMac:02:1c:73:c0:c6:12
              VNI: 112 L3 VNI: 5001 ESI: 0000:0000:0000:0000:0000
        BGP routing table entry for mac-ip 001c.73c0.c617, Route Distinguisher: 10.111.254.3:134
        Paths: 1 available
          Local
            - from - (0.0.0.0)
              Origin IGP, metric -, localpref -, weight 0, valid, local, best
              Extended Community: Route-Target-AS:134:134 TunnelEncap:tunnelTypeVxlan
              VNI: 134 ESI: 0000:0000:0000:0000:0000
        BGP routing table entry for mac-ip 001c.73c0.c617 10.111.134.202, Route Distinguisher: 10.111.254.3:134
        Paths: 1 available
          Local
            - from - (0.0.0.0)
              Origin IGP, metric -, localpref -, weight 0, valid, local, best
              Extended Community: Route-Target-AS:134:134 Route-Target-AS:5001:5001 TunnelEncap:tunnelTypeVxlan
              VNI: 134 L3 VNI: 5001 ESI: 0000:0000:0000:0000:0000

      .. note::
        - you can notice that the BGP control has learnt 2 another RT-2 which include the MAC and the IP of **s1-host1** (dual labels)
        - these RT-2 have been generated by **s1-leaf1** and **s1-leaf2** when the virtual IP has been hitten by the ping 
        - one of the charasteristic of S-IRB is to have individual /32 host routes for each remote host learned on each L2 segment

**LAB COMPLETE!**
