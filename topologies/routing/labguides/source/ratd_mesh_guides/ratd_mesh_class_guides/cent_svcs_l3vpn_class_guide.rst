Offer Centralized Services to L3VPN Customers
=========================================================================

.. image:: ../../images/ratd_mesh_images/ratd_mesh_cent_svcs_l3vpn.png
   :align: center

|

#. Configure EOS20 for BGP ASN 500.

   - EOS20 should originate the following network via BGP (any method of network origination is acceptable):

      - 20.20.20.20/32

#. Create a Centralized Services VPN, utilizing the VRF “SVC” on the necessary PE nodes.

#. Establish eBGP IPv4 Unicast peerings between EOS20 and Service Provider PE device.  This peering should be within the Centralized Services VPN (VRF).

#. Allow CE devices EOS12 and EOS19 to access the Centralized Service at 20.20.20.20.

   - EOS11, EOS13, EOS15 and EOS18 must not be able to ping 20.20.20.20.

   - Customer-1 (VRF A) and Customer-4 (VRF B) CE devices must not see each other’s routes, and must not be able to ping each other.

   - ACLs must not be used to accomplish any part of this task.