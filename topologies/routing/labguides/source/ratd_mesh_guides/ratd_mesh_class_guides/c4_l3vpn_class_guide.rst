Deploy L3VPN Service for Customer-4
=====================================================

   .. image:: ../../images/ratd_mesh_images/ratd_mesh_c4_l3vpn.png
      :align: center

=========================================================================
Prepare for Customer-4 Layer3 VPN Services
=========================================================================

   #. On all PE nodes that are connected to Customer-4 CE nodes, define VRF "B".

      - Ensure IPv4 Unicast Forwarding is enabled.
   
      - Route-Target for import and export should be 2:2.
   
      - Route-Distinguisher should be X.X.X.X:2 (X = Node-ID).
   
   #. Place the appropriate interfaces on the PE nodes into VRF “B”.

=========================================================================
Establish PE-CE peering with Customer-4
=========================================================================
 
   #. Configure EOS18 and EOS19 should as BGP AS 200.
   
      - EOS18 should originate the following network via BGP (any method of network origination is acceptable):
   
         - 18.18.18.18/32
   
      - EOS19 should originate the following network via BGP (any method of network origination is acceptable):
   
         - 19.19.19.19/32
   
   #. Establish eBGP IPv4 Unicast peerings between Customer-4 CE and Service Provider PE devices.  These peerings should be within the Customer-4 VPN (VRF).
   
   #. Verify reachability between Customer-4 CE devices by pinging each other’s Loopback0 interface when sourcing the pings from their own Loopback0 interface.