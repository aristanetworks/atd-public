Deploy L2VPN Service for Customer-2
=====================================================

   .. image:: ../../images/RATD-Section8+9.png
      :align: center

=========================================================================
Prepare for Customer-2 Layer 2 VPN E-LAN Services
=========================================================================
   
   #. On all PE nodes that are connected to Customer-2 CE nodes, create VLAN 20.
   
   #. Define the ‘VLAN 20’ MAC-VRF.
   
      - Route-Target for import and export should be 2:20.
   
      - Route-Distinguisher should be X.X.X.X:20 (X = Node-ID).

      - Ensure that all known MAC addresses in VLAN 20 are originated/advertised via BGP to other PE Nodes.
   
   #. Configure the appropriate interfaces on the PE Nodes as access (untagged) interfaces in VLAN 20.
   
   #. Enable EOS14 and EOS9 to be dual-homed to their respective PE nodes via an LACP port-channel.
   
      - Both links should be active for egress, as well as ingress traffic.
   
      - MLAG must not be used to accomplish this task.

=========================================================================
Configure the Customer-2 CE Nodes
=========================================================================
 
   #. Configure EOS9, EOS10 and EOS14 to run OSPF process 200 in area 0.
 
   #. Advertise all connected interfaces into OSPF using a network statement.
 
   #. Ensure all traffic to/from multi-homed L2VPN locations should be load balanced across all PE-CE links into that location.
 
   #. Verify that EOS3 and EOS6 should have the following output from a ‘show l2rib input bgp vlan 20’ command:	
 
      ..	note::

         MAC addresses and Labels may differ in your output, this is ok. The key output is 2-way load balancing to MAC addresses that exist at remote dual-homed sites
 
      - EOS3:
 
         .. image:: ../../images/RATD_Section9_Task_D_EOS3.png
            :align: center   
      
      - EOS6:
      
         .. image:: ../../images/RATD_Section9_Task_D_EOS6.png
            :align: center

   #. Confirm that EOS9, EOS10 and EOS14 have formed OSPF adjacencies with each other. These devices should all be able to ping each other’s Loopback0 interfaces when sourcing the ping from their Loopback0 interface.