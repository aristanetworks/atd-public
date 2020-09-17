Deploy L3VPN Service for Customer-1
=====================================================

.. image:: ../../images/ratd_mesh_images/ratd_mesh_c1_l3vpn.png
   :align: center

|

===================================================================================
Prepare for Customer-1 Layer 3 VPN Services
===================================================================================
   
#. On all PE nodes that are connected to Customer-1 CE nodes, define VRF “A”.

   - Ensure IPv4 Unicast Forwarding is enabled.

   - Route-Target for import and export should be 1:1.

   - Route-Distinguisher should be X.X.X.X:1 (X = Node-ID).

#. Place the appropriate interfaces on the PE nodes into VRF “A”.

=========================================================================
Configure Customer-1 CE devices
=========================================================================
   
#. Configure EOS11, EOS12 and EOS13 to run OSPF process 100 in area 0.

#. Advertise all connected interfaces into OSPF using a network statement.

   - Once this task is complete; EOS11, EOS12, and EOS13 should be able to ping each other’s loopbacks and directly connected interfaces

=========================================================================
Establish PE-CE peering with Customer-1
=========================================================================
   
#. Configure EOS11 and EOS12 for BGP AS 123.
  
   - EOS11 and EOS12 should originate the following networks via BGP (any method of network origination is acceptable):
  
      - 11.11.11.11/32
  
      - 12.12.12.12/32
  
      - 13.13.13.13/32

#. Configure EOS15 for BGP AS 15.

   - EOS15 should originate the following networks via BGP (any method of network origination is acceptable):

      - 15.15.15.15/32

#. Establish eBGP IPv4 Unicast peering between Customer-1 CE and Service Provider PE devices. These peerings should be within the Customer-1 VPN (VRF).

#. Ensure EOS12 should has the following output from a ‘show ip route ospf’ command:
  
   .. image:: ../../images/ratd_common_images/ratd_c1_l3vpn_ospf.png
      :align: center   

#. Ensure EOS15 should has the following output from a ‘show ip route bgp’ command:

   .. image:: ../../images/ratd_common_images/ratd_c1_l3vpn_bgp.png
      :align: center   

#. Verify reachability between all Customer-1 CE devices by pinging each other’s Loopback0 interface while sourcing the pings from their own Loopback0 interface.

=========================================================================
Enable L3VPN Multi-Pathing
=========================================================================

#. Ensure that traffic from EOS15 to EOS12 uses multiple paths across the Service Provider network, distributing the load between EOS1 and EOS6.

   - It is ok to adjust the isis metric on the link between EOS6 and EOS8 in order to force multi-pathing to occur.

#. EOS8 should have the following output from a ‘show ip route vrf A 12.12.12.12’ command:

   .. note::

      The specific labels may vary in your output.

   .. image:: ../../images/ratd_mesh_images/ratd_mesh_l3vpn_mp.png
      :align: center 