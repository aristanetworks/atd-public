
L2 EVPN
=======

.. thumbnail:: images/l2evpn/nested_l2evpn_topo_dual_dc.png
   :align: center

      Click image to enlarge

.. note:: This lab exercise is focused on the EVPN-VXLAN configuration. IP addresses, MLAG and BGP Underlay are already configured.

1. Log into the  **LabAccess**  jumpserver:

   Type ``l2evpn`` at the prompt. The script will configure the datacenter with the exception of **s1-leaf4**

#. On **s1-leaf4**, configure ArBGP. **(Already configured and enabled on the switch)**

   .. code-block:: html

      service routing protocols model multi-agent

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
         :emphasize-lines: 1

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

#. Configure L2EVPN service on **s1-leaf4**

   a. Add the VLAN 112 with the VNI 112 association
   
      .. code-block:: html

         interface Vxlan1
            vxlan vlan 112 vni 112

   #. Add the mac vrf EVPN configuration for VLAN 112 

      .. code-block:: html

         router bgp 65103
            vlan 112
               rd auto
               route-target both 112:112
               redistribute learned
   
   #. Check the interface Vxlan config

      .. code-block:: text
         :emphasize-lines: 1

         s1-leaf4(config-macvrf-12)#sh vxlan config-sanity detail 
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
           VXLAN Routing                       OK    VXLAN Routing not enabled                         
         CVX Configuration Check               OK                                                      
           CVX Server                          OK    Not in controller client mode                     
         MLAG Configuration Check              OK    Run 'show mlag config-sanity' to verify MLAG config
           Peer VTEP IP                        OK                                                      
           MLAG VTEP IP                        OK                                                      
           Peer VLAN-VNI                       OK                                                      
           Virtual VTEP IP                     OK

   #. Check the VXLAN dataplane

      .. code-block:: text
        :emphasize-lines: 1,2

           s1-leaf4(config-router-bgp)#sh int vxlan 1
           Vxlan1 is up, line protocol is up (connected)
             Hardware is Vxlan
            Source interface is Loopback1 and is active with 10.111.253.3
            Replication/Flood Mode is headend with Flood List Source: EVPN
             Remote MAC learning via EVPN
            VNI mapping to VLANs
            Static VLAN to VNI mapping is 
              [112, 112]       
             Note: All Dynamic VLANs used by VCS are internal VLANs.
                   Use 'show vxlan vni' for details.
             Static VRF to VNI mapping is not configured
             Headend replication flood vtep list is:
             112 10.111.253.1   
            MLAG Shared Router MAC is 0000.0000.0000 

#. Verify VXLAN and L2EVPN

   a. On **s1-leaf1** (and/or **s1-leaf2**) verify the IMET table

      .. code-block:: text
        :emphasize-lines: 1

         s1-leaf1#sh bgp evpn route-type imet 
         BGP routing table information for VRF default
         Router identifier 10.111.254.1, local AS number 65101
         Route status codes: s - suppressed, * - valid, > - active, E - ECMP head, e - ECMP
                             S - Stale, c - Contributing to ECMP, b - backup
                             % - Pending BGP convergence
         Origin codes: i - IGP, e - EGP, ? - incomplete
         AS Path Attributes: Or-ID - Originator ID, C-LST - Cluster List, LL Nexthop - Link Local Nexthop

                   Network                Next Hop              Metric  LocPref Weight  Path
         * >Ec   RD: 10.111.254.3:112 imet 10.111.253.3
                                         10.111.253.3          -       100     0       65100 65102 i
         *  ec   RD: 10.111.254.3:112 imet 10.111.253.3
                                         10.111.253.3          -       100     0       65100 65102 i
         * >Ec   RD: 10.111.254.4:112 imet 10.111.253.3
                                         10.111.253.3          -       100     0       65100 65102 i
         *  ec   RD: 10.111.254.4:112 imet 10.111.253.3
                                         10.111.253.3          -       100     0       65100 65102 i
         * >     RD: 10.111.254.1:112 imet 10.111.253.1
                                         -                     -       -       0       i
      .. code-block:: text
        :emphasize-lines: 1

        s1-leaf1#sh interfaces vxlan 1
        Vxlan1 is up, line protocol is up (connected)
          Hardware is Vxlan
          Source interface is Loopback1 and is active with 10.111.253.1
          Replication/Flood Mode is headend with Flood List Source: EVPN
          Remote MAC learning via EVPN
          VNI mapping to VLANs
          Static VLAN to VNI mapping is 
            [112, 112]       
          Note: All Dynamic VLANs used by VCS are internal VLANs.
                Use 'show vxlan vni' for details.
          Static VRF to VNI mapping is not configured
          Headend replication flood vtep list is:
          112 10.111.253.3   
          MLAG Shared Router MAC is 0000.0000.0000

   #. Log into **s1-host1** and ping **s2-host2**

      .. code-block:: text
        :emphasize-lines: 1

        s1-host1#ping 10.111.112.202
        PING 10.111.112.202 (10.111.112.202) 72(100) bytes of data.
        80 bytes from 10.111.112.202: icmp_seq=1 ttl=64 time=16.8 ms
        80 bytes from 10.111.112.202: icmp_seq=2 ttl=64 time=14.7 ms
        80 bytes from 10.111.112.202: icmp_seq=3 ttl=64 time=16.8 ms
        80 bytes from 10.111.112.202: icmp_seq=4 ttl=64 time=16.7 ms
        80 bytes from 10.111.112.202: icmp_seq=5 ttl=64 time=15.2 ms
        --- 10.111.112.202 ping statistics ---
        5 packets transmitted, 5 received, 0% packet loss, time 61ms
          
   #. On **s1-leaf1** and **s1-leaf4**

        .. code-block:: text

          s1-leaf1#show mac address-table dynamic 
          Mac Address Table
          ------------------------------------------------------------------

          Vlan    Mac Address       Type        Ports      Moves   Last Move
          ----    -----------       ----        -----      -----   ---------
          112    001c.73c0.c616    DYNAMIC     Po5        1       0:00:41 ago
          112    001c.73c0.c617    DYNAMIC     Vx1        1       0:00:41 ago
          Total Mac Addresses for this criterion: 2

                    Multicast Mac Address Table
          ------------------------------------------------------------------

          Vlan    Mac Address       Type        Ports
          ----    -----------       ----        -----
          Total Mac Addresses for this criterion: 0
         
        .. code-block:: text

          s1-leaf1#show bgp evpn route-type mac-ip 
          BGP routing table information for VRF default
          Router identifier 10.111.254.1, local AS number 65101
          Route status codes: s - suppressed, * - valid, > - active, E - ECMP head, e - ECMP
                              S - Stale, c - Contributing to ECMP, b - backup
                              % - Pending BGP convergence
          Origin codes: i - IGP, e - EGP, ? - incomplete
          AS Path Attributes: Or-ID - Originator ID, C-LST - Cluster List, LL Nexthop - Link Local Nexthop

                    Network                Next Hop              Metric  LocPref Weight  Path
          * >     RD: 10.111.254.1:112 mac-ip 001c.73c0.c616
                                          -                     -       -       0       i
          * >     RD: 10.111.254.1:112 mac-ip 001c.73c0.c616 10.111.112.201
                                          -                     -       -       0       i
          * >Ec   RD: 10.111.254.3:112 mac-ip 001c.73c0.c617
                                          10.111.253.3          -       100     0       65100 65102 i
          *  ec   RD: 10.111.254.3:112 mac-ip 001c.73c0.c617
                                          10.111.253.3          -       100     0       65100 65102 i
          * >Ec   RD: 10.111.254.4:112 mac-ip 001c.73c0.c617
                                          10.111.253.3          -       100     0       65100 65102 i
          *  ec   RD: 10.111.254.4:112 mac-ip 001c.73c0.c617
                                          10.111.253.3          -       100     0       65100 65102 i

**LAB COMPLETE!**
