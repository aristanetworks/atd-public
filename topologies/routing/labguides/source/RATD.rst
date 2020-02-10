Routing ATD Lab Guide
=====================

.. image:: images/RATD-Topo-Image.png
   :align: center

1.	Deploy IS-IS as the Service Provider Underlay IGP
==========================================================

   .. image:: images/RATD-Section1+2-Image.png
      :align: center
  
   a.	IS-IS will be leveraged to carry underlay IPv4 prefix reachability information
  
   b.	All nodes should be within the same flooding domain
  
   c.	All nodes should only maintain a Level-2 database
  
   d.	Ensure that there are no unnecessary Pseudonodes within the topology
  
   e.	(Optional) Only advertise reachability information for /32 loopback interfaces into the LSDB
  
   f.	Once this task has been completed, all Service Provider nodes should be able to ping all other node loopback addresses

2.	Establish MPLS transport label distribution via Segment-Routing
=========================================================================

   a.	Enable Segment-Routing extensions to IS-IS, leveraging MPLS data plane encapsulation
   
   b.	The Segment Routing Global Block (SRBG) label range should be 900,000 – 965,535 on all Service Provider nodes
   
   c.	Each node should have a globally unique Node SID equal to 900,000 + NodeID
 
      i.	For example, EOS1 should have a Node SID of 900,001
   
   d.	Review IS-IS adjacency SIDs on EOS2 and EOS5
 
      i.	Is there overlap?
 
      ii.	If so, will this present an issue? Why or Why not?
   
   e.	Validate that all Service Provider nodes have a globally unique Node SID
   
   f.	To protect against black holes, and reduce convergence time:
 
      i.	Enable the equivalent of IGP Sync and Session-Protection within the Segment-Routing domain
   
   g.	Once this task has been completed, all Service Provider nodes should have an LSP established for reachability between loopbacks

       .. code-block:: text

         ping mpls segment-routing ip x.x.x.x/32 source y.y.y.y

       .. code-block:: text

         traceroute mpls segment-routing ip x.x.x.x/32 source y.y.y.y

3.	Prepare to offer VPN services to customers via MP-BGP EVPN control-plane
==================================================================================

   .. image:: images/RATD-Section3-Image.png
      :align: center
 
   a.	BGP Autonomous System 100 is leveraged by the Service Provider
 
   b.	Do all nodes within the Service Provider need to run BGP? Why, or why not?
  
   c.	Enable BGP EVPN peering within the service provider
  
      i.	BGP Router-ID should be Loopback0 32-bit value
  
      ii.	Loopback0 IP address should be used for all BGP peerings
  
      iii.	All PE nodes must be capable of advertising and receiving reachability information to/from all other PE nodes
  
      iv.	A full mesh of peerings must not be used to accomplish this task
  
      v.	EOS5 should act as the peering point for all PE nodes
  
      vi.	Disable any unnecessary BGP AFI/SAFI peerings
  
      vii.	Use MPLS as the data-plane encapsulation / VPN label distribution

4.	Prepare for Customer-1 Layer3 VPN Services
===================================================================================

   .. image:: images/RATD-Section4+5+6+7-Image.png
      :align: center
   
   a.	Customer-1 CE Nodes: EOS11, EOS13, EOS15
   
   b.	On all PE nodes that are connected to Customer-1 CE nodes:
   
      i.	Define VRF “A”
   
         1.	IPv4 Unicast Forwarding
   
         2.	Route-Target for import and export should be 1:1
   
         3.	Route-Distinguisher should be X.X.X.X:1 (X = Node-ID)
   
      ii.	Place the appropriate interfaces on the PE nodes into VRF “A”

5.	Configure Customer-1 CE devices
=========================================================================
   
   a.	EOS11, EOS12 and EOS13 should all run OSPF process 100 in area 0
   
   b.	Advertise all connected interfaces into OSPF using a network statement
   
   c.	Once this task is complete; EOS11, EOS12, and EOS13 should be able to ping each other’s loopbacks and directly connected interfaces

6.	Establish PE-CE peering with Customer-1
=========================================================================
   
   a.	EOS11 EOS12 should be in BGP AS 123
      
      i.	EOS11 and EOS12 should originate the following networks via BGP (any method of network origination is acceptable)
      
         1.	11.11.11.11/32
      
         2.	12.12.12.12/32
      
         3.	13.13.13.13/32
   
   b.	EOS15 should be in BGP AS 15
   
      i.	EOS15 should originate the following networks via BGP (any method of network origination is acceptable)
   
         1.	15.15.15.15/32
   
   c.	Establish eBGP IPv4 Unicast peering between Customer-1 CE and Service Provider PE devices. These peerings should be within the Customer-1 VPN (VRF)
   
   d.	EOS12 should have the following output from a ‘show ip route ospf’ command:
      
      .. image:: images/RATD_Section6_Task_D.png
         :align: center   
   
   e.	EOS15 should have the following output from a ‘show ip route bgp’ command:

      .. image:: images/RATD_Section6_Task_E.png
         :align: center   
 
   f.	Once this task is complete, all Customer-1 CE devices should be able to ping each other’s Loopback0 interface when sourcing the pings from their own Loopback0 interface

7.	L3VPN Multi-Pathing
=========================================================================
  
   a.	When pinging from EOS15 to EOS12, multiple paths should be leveraged across the Service Provider; distributing the load between EOS1 and EOS6
  
   b.	It is ok to adjust the isis metric on the link between EOS6 and EOS8 in order to force multi-pathing to occur
  
   c.	EOS8 should have the following output from a ‘show ip route vrf A 12.12.12.12’ command (label may vary, this is ok):
  
      .. image:: images/RATD_Section7_Task_C.png
         :align: center   

8.	Prepare for Customer-2 Layer2 VPN E-LAN Services
=========================================================================

   .. image:: images/RATD-Section8+9.png
      :align: center
   
   a.	Customer-2 CE Nodes: EOS9, EOS10, EOS14
   
   b.	On all PE nodes that are connected to Customer-2 CE nodes:
   
      i.	Create VLAN 20
   
      ii.	Define the ‘VLAN 20’ MAC VRF
   
         1.	Route-Target for import and export should be 2:20
   
         2.	Route-Distinguisher should be X.X.X.X:20 (X = Node-ID)
   
      iii.	Configure the appropriate interfaces on the PE Nodes as access interfaces in VLAN 20
   
      iv.	Ensure that all known MAC addresses in VLAN 20 are originated/advertised via BGP to other PE Nodes
   
   c.	EOS14 and EOS9 will be dual-homed to their PE nodes via an LACP port-channel
   
      i.	Both links should be active for egress, as well as ingress traffic
   
      ii.	MLAG must not be used to accomplish this task

9.	Configure the Customer-2 CE Nodes
=========================================================================
 
   a.	EOS9, EOS10 and EOS14 should all run OSPF process 200 in area 0
 
   b.	Advertise all connected interfaces into OSPF using a network statement
 
   c.	All traffic to/from multi-homed L2VPN locations should be load balanced across all PE-CE links into that location
 
   d.	EOS3 and EOS6 should have the following output from a ‘show l2rib input bgp vlan 20’ command:	
 
      i.	Note: MAC addresses and Labels may differ in your output, this is ok. The key output is 2-way load balancing to MAC addresses that exist at remote dual-homed sites
 
      ii.	EOS3:
 
         .. image:: images/RATD_Section9_Task_D_EOS3.png
            :align: center   
      
      iii.	EOS6:
      
         .. image:: images/RATD_Section9_Task_D_EOS6.png
            :align: center

   e.	Once this task is complete; EOS9, EOS10 and EOS14 should all form OSPF adjacencies with each other. These devices should all be able to ping each other’s Loopback0 interfaces when sourcing the ping from their Loopback0 interface

10. Configure Customer-3 E-LINE Service
=========================================================================

   .. image:: images/RATD-Section10-Image.png
      :align: center

   a.	Customer-3 requires that EOS16 and EOS17 appear as directly Layer2 adjacent to each other
   
   b.	Configure a P2P E-LINE service enabling this functionality
   
   c.	This solution should not require any VLAN tagging from the CE devices
   
   d.	When this task is complete EOS16 and EOS17 should form an OSPF adjacency with each other, and be able to ping each other’s loopbacks

11.	Prepare for Customer-4 Layer3 VPN Services
=========================================================================

   .. image:: images/RATD-Section11+12-Image.png
      :align: center
  
   a.	Customer-4 CE Nodes: EOS18, EOS19
  
   b.	On all PE nodes that are connected to Customer-4 CE nodes:
  
      i.	Define VRF “B”
  
         1.	IPv4 Unicast Forwarding
  
         2.	Route-Target for import and export should be 2:2
  
         3.	Route-Distinguisher should be X.X.X.X:2 (X = Node-ID)
  
      ii.	Place the appropriate interfaces on the PE nodes into VRF “B”

12.	Establish PE-CE peering with Customer-4
=========================================================================
 
   a.	EOS18 and EOS19 should be in BGP AS 200
   
      i.	EOS18 should originate the following network via BGP (any method of network origination is acceptable)
   
         1.	18.18.18.18/32
   
      ii.	EOS19 should originate the following network via BGP (any method of network origination is acceptable)
   
         1.	19.19.19.19/32
   
   b.	Establish eBGP IPv4 Unicast peering between Customer-4 CE and Service Provider PE devices.
   
   c.	Once this task is complete, Customer-4 CE devices should be able to ping each other’s Loopback0 interface when sourcing the pings from their own Loopback0 interface

13.	Offer Centralized Services to L3VPN Customers
=========================================================================

   .. image:: images/RATD-Section13-Image.png
      :align: center
  
   a.	EOS20 is providing a centralized service to L3VPN customers
   
   b.	This service is accessible via 20.20.20.20/32
   
   c.	The service should only be accessible from EOS12 and EOS19
   
   d.	Create a centralized service offering, utilizing the VRF “SVC” on the necessary PE nodes
   
   e.	When this task is complete, EOS12 and EOS19 should all be able to ping 20.20.20.20
   
   f.	EOS11, EOS13, EOS15 and EOS18 must not be able to ping 20.20.20.20
   
   g.	Customer-1 (VRF A) and Customer-4 (VRF B) CE devices must not see each other’s routes, and must not be able to ping each other
   
   h.	ACLs must not be used to accomplish any part of this task