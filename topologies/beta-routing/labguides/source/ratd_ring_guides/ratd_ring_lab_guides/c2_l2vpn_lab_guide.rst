Deploy L2VPN Service for Customer-2
=====================================================

.. image:: ../../images/ratd_ring_images/ratd_ring_c2_l2vpn.png
   :align: center

|

#. If you did not fully complete the previous Customer-1 L3VPN lab, log into the **LabAccess** jumpserver to prepare the 
   lab environment.

   #. Type ``c2l2vpn-ring`` or Lab Option 5 at the Ring Routing Labs prompt. The script will configure the topology 
      with the necessary base IPv4 addressing, IS-IS IGP, enable SR extensions for MPLS and BGP EVPN.

#. Customer-2 is attached to five Service Provider nodes, **EOS3**, **EOS4**, **EOS6**, **EOS7** and **EOS8**. These 
   will be **PE** nodes. Since this customer will require a Layer 2 VPN Service, create a VLAN for their traffic and 
   use EVPN to advertise the customer MAC addresses to other interested PEs.

   #. First, create a local VLAN with an ID of ``20`` on each of the PE nodes.

      .. note::

         Similar to the L3VPN, we are using MPLS to create VPNs in the Service Provider network. The only difference here 
         is the VPN is providing a switched LAN service as opposed to a router service. Again, the VLAN only needs to be 
         created on the nodes attached to the customer the VLAN is for; in this case Customer-2.

      .. code-block:: text

         vlan 20
            name Customer2_E-LAN

   #. Place the interface attached to the **CE** node for Customer-2 into VLAN ``20`` on **EOS7** to attach it to the E-LAN 
      service.

      .. note::

         We are providing an untagged service. If a tagged service was required, we would configure a dot1q trunk instead.

      .. code-block:: text

         interface Ethernet2
            switchport access vlan 20
            spanning-tree portfast

   #. Repeat the above step to place the interfaces attached to Customer-2 **CE** nodes into VLAN ``20`` on **EOS3**, 
      **EOS4**, **EOS6**, and **EOS8**. In addition, configure these interfaces for an Active-Active LACP Port-Channel.

      .. note::

         Normally, you cannot have two interfaces on separate routers as part of a single LAG without an additional 
         protocol between them such as MLAG. In this case, we will configure BGP EVPN to properly signal this LAG later 
         in the lab.  For now, just create the base Port-Channel configuration for the interface.
      
      **EOS3**

      .. code-block:: text

         interface Port-Channel9
            description CE-EOS9
            switchport access vlan 20
            spanning-tree portfast
         !
         interface Ethernet1
            channel-group 9 mode active
      
      **EOS4**

      .. code-block:: text

         interface Port-Channel9
            description CE-EOS9
            switchport access vlan 20
            spanning-tree portfast
         !
         interface Ethernet1
            channel-group 9 mode active
      
      **EOS6**

      .. code-block:: text

         interface Port-Channel14
            description CE-EOS14
            switchport access vlan 20
            spanning-tree portfast
         !
         interface Ethernet6
            channel-group 9 mode active
      
      **EOS8**

      .. code-block:: text

         interface Port-Channel14
            description CE-EOS14
            switchport access vlan 20
            spanning-tree portfast
         !
         interface Ethernet4
            channel-group 9 mode active

   #. Configure BGP EVPN to advertise reachability of any MACs learned in VLAN ``20`` from the customer by setting 
      an **RD** and an **RT**, within BGP on **EOS7**. It should have a unique **RD** following the format of 
      **<Loopback0 IP>** ``:2`` and the **RT** on all routers in the VPN should match as ``2:20``. Additionally, 
      ensure BGP is configured for ECMP where applicable.

      .. note::

         The **RD** and **RT** serves the same function for the L2VPN as they do for the L3VPN, providing a unified 
         approach to VPN control-plane configuration. The ``redistribute learned`` command ensures that any locally 
         learned MACs will be advertised to the Route Reflector using BGP EVPN.

      .. code-block:: text

         router bgp 100
            maximum-paths 2
            !
            vlan 20
               rd 7.7.7.7:2
               route-target both 2:20
               redistribute learned

   #. Repeat the above step on the remain PEs, **EOS3**, **EOS4**, **EOS6**, and **EOS8**, adjusting the **RD** as 
      necessary while keeping the **RT** consistent.

      **EOS3**

      .. code-block:: text

         router bgp 100
            maximum-paths 2
            !
            vlan 20
               rd 3.3.3.3:2
               route-target both 2:20
               redistribute learned

      **EOS4**

      .. code-block:: text

         router bgp 100
            maximum-paths 2
            !
            vlan 20
               rd 4.4.4.4:2
               route-target both 2:20
               redistribute learned

      **EOS6**

      .. code-block:: text

         router bgp 100
            maximum-paths 2
            !
            vlan 20
               rd 6.6.6.6:2
               route-target both 2:20
               redistribute learned

      **EOS8**

      .. code-block:: text

         router bgp 100
            maximum-paths 2
            !
            vlan 20
               rd 8.8.8.8:2
               route-target both 2:20
               redistribute learned

   #. Now, configure the previously created Port-Channel interfaces on **EOS3**, **EOS4**, **EOS6**, and **EOS8** 
      to use EVPN All-Active to enable both PEs in each LAG to actively forward traffic for the CE node.

      .. note::

         EVPN A-A utilizes BGP to negotiate LAG membership and Designated Forwarder roll for each LAG using an unique 
         Ethernet Segment Identifier, or **ESI**, for each LAG as well as a specific RT. To ensure the attached CE device 
         sees both PEs as a single LACP system, we also statically set the ``lacp system-id`` to be the same on both PEs 
         for the LAG.

      **EOS3**

      .. code-block:: text

         interface Port-Channel9
            !
            evpn ethernet-segment
               identifier 0000:0200:0200:1000:0304
               route-target import 00:02:00:01:00:20
            lacp system-id 0000.0000.0034

      **EOS4**

      .. code-block:: text

         interface Port-Channel9
            !
            evpn ethernet-segment
               identifier 0000:0200:0200:1000:0304
               route-target import 00:02:00:01:00:20
            lacp system-id 0000.0000.0034

      **EOS6**

      .. code-block:: text

         interface Port-Channel14
            !
            evpn ethernet-segment
               identifier 0000:0200:0200:2000:0608
               route-target import 00:02:00:02:00:20
            lacp system-id 0000.0000.0068

      **EOS8**

      .. code-block:: text

         interface Port-Channel14
            !
            evpn ethernet-segment
               identifier 0000:0200:0200:2000:0608
               route-target import 00:02:00:02:00:20
            lacp system-id 0000.0000.0068

#. Now, configure the Customer-2 CE nodes to connect to each other over the emulated LAN service.

   #. Since the Service Provider is providing a Layer 2 service, configure the CE on **EOS9**, **EOS10**, and **EOS14** 
      interfaces as part of a common subnet as if they were attached to a common Layer 2 switch. For dual-homed CEs, 
      configure this link as an LACP Port-Channel.

      **EOS9**

      .. code-block:: text

         interface Port-Channel9
            description PEs: EOS3,EOS4
            no switchport
            ip address 10.0.0.9/24
         !
         interface Ethernet1
            channel-group 9 mode active
         !
         interface Ethernet2
            channel-group 9 mode active
         !
         router ospf 200
            network 0.0.0.0/0 area 0.0.0.0
            max-lsa 12000

      .. note::

         On **EOS10** we manually adjust the MAC address just to avoid any potential overlap in the virutalized lab 
         environment.

      **EOS10**

      .. code-block:: text

         interface Ethernet1
            mac-address 00:00:00:00:10:10
            no switchport
            ip address 10.0.0.10/24
         !
         router ospf 200
            network 0.0.0.0/0 area 0.0.0.0
            max-lsa 12000

      **EOS14**

      .. code-block:: text

         interface Port-Channel14
            description PEs: EOS6,EOS8
            no switchport
            ip address 10.0.0.14/24
         !
         interface Ethernet1
            channel-group 14 mode active
         !
         interface Ethernet2
            channel-group 14 mode active
         !
         router ospf 200
            network 0.0.0.0/0 area 0.0.0.0
            max-lsa 12000

#. With all PE and CE nodes configured, verify Layer 2 connectivity between CE nodes **EOS9**, **EOS10** and **EOS14**.

   #. Verify that all CE interfaces are able to resolve ARP for their peers and that dual-homed CEs have succesfully 
      negotiated an LACP Port-Channel

      .. note::

         The Service Provider network is emulating the behavior of a Layer 2 switch and as such should be transparent to 
         the Layer 3 operations between the CE nodes.

      .. code-block:: text

         show ip arp
         show port-channel summary

   #. Verify OSPF adjacencies have formed between the CEs and routes have been exchanged.

      .. code-block:: text

         show ip ospf neighbor
         show ip route

   #. Test connectivity between CE Loopback0 interfaces from **EOS9** to **EOS14**.

      .. code-block:: text

         ping 14.14.14.14 source 9.9.9.9

#. Finally, verify the EVPN control-plane and MPLS data-plane for the customer L2VPN.

   #. Verify the local MAC address-table on **EOS3** as an example.

      .. note::

         The MACs tied to port ``Mt1``, or MPLStunnel1 are remote EVPN learned MACs.

      .. code-block:: text

         show mac address-table vlan 20
   
   #. Verify the EVPN Type-2 route advertisements on **EOS3**.

      .. note::

         The key fields to track, again similar to the L3VPN, are the **RD** which denotes the originator of the specified 
         EVPN Type-2 (MAC-IP) route, the **RT** which denotes the associated Customer VRF and the assigned **MPLS label**, 
         which represents the VPN or VLAN label that EOS dynamically assigns.  Additionally, any MAC learned via an EVPN 
         A-A Port-Channel will have the associated **ESI** value populated.

      .. code-block:: text

         show bgp evpn summary
         show bgp evpn route-type mac-ip detail

   #. Display the EVPN Type-3 route advertisements on **EOS3**.

      .. note::

         Each PE node in the lab should send a Type-3 **IMET** route to express their interest in receiving BUM traffic 
         for VLAN 20.

      .. code-block:: text

         show bgp evpn route-type imet detail
   
   #. Validate the control-plane for the local LACP Port-Channel on **EOS3**.

      .. note::

         When viewing the EVPN instance, note that  one of the two routers in the ES has been elected the 
         ``Designated forwarder`` for BUM traffic for the CE LAG.

      .. code-block:: text

         show port-channel summary
         show bgp evpn route-type ethernet-segment esi 0000:0200:0200:1000:0304 detail 
         show bgp evpn instance

   #. Verify Layer 2 ECMP towards remotely attached CE MAC of **EOS14** towards **EOS6** and **EOS8** from **EOS3**.

      .. note::

         For this step, the MAC address of **EOS14** will vary per lab. Log into **EOS14** and view the MAC of the LAG on 
         **EOS14** with the command ``show interface Port-Channel14``.  That MAC should be substituted in the below commands 
         where you see the MAC ``041b.5d09.3f85``.

      .. code-block:: text

         show mac address-table address 041b.5d09.3f85
         show bgp evpn route-type mac-ip 041b.5d09.3f85
         show bgp evpn route-type auto-discovery esi 0000:0200:0200:2000:0608 detail
         show l2rib output mac 041b.5d09.3f85


**LAB COMPLETE!**