Offer Centralized Services to L3VPN Customers
=========================================================================

.. image:: ../../images/ratd_mesh_images/ratd_mesh_cent_svcs_l3vpn.png
   :align: center

|

#. If you did not fully complete the previous Customer-4 L3VPN Setup lab, log into the **LabAccess** jumpserver to prepare 
   the lab environment.

   #. Type ``centsvc`` or Lab Option 8 at the prompt. The script will configure the topology with the necessary base IPv4 
      addressing, IS-IS IGP, enable SR extensions for MPLS and BGP EVPN as well as the Customer-1 and Customer-4 L3VPNs.

#. The Centralized Service is attached to Service Provider node **EOS3**. These will be our **PE** node. Since this 
   Centralized Service will be accessed via a Layer 3 VPN Service, create an isolated VRF for its traffic and use EVPN 
   to advertise the customer networks to other interested PEs.

   #. Create a VRF Instance called ``SVC`` on **EOS3**.

      .. note::

         While this service will be accessed by Customers attached to other PEs, we will leverage EVPN to allow for 
         inter-VRF communication and only require the ``SVC`` VRF where the node attaches to the Service Provider network.

      .. code-block:: text

         vrf instance SVC
         !
         ip routing vrf SVC

   #. Place the interface attached to the **CE** node for the Centralized Service into VRF ``SVC`` on **EOS3** to ensure its 
      traffic remains isolated.

      .. code-block:: text

         interface Ethernet6
            vrf SVC
            ip address 10.3.20.3/24

   #. Now leverage BGP EVPN to advertise reachability of any routes learned in VRF ``SVC`` from the Centralized Service by 
      setting an **RD** and an **RT** within BGP on **EOS3**. It should have a unique **RD** following the format of 
      **<Loopback0 IP>** ``:5`` and the **RT** on all routers in the VPN should be ``5:5``.

      .. note::

         Unlike our previous L3VPN setups, for the Centralized Service model, we will only need to ``export`` the routes 
         learned in the ``SVC`` VRF with this **RT**. In a later step, we will see how inter-VRF route-leaking can be 
         controlled using a separate **RT** for import.

      .. code-block:: text

         router bgp 100
            !
            vrf SVC
               rd 3.3.3.3:5
               route-target export evpn 5:5

   #. Finally, define the BGP peer facing the Centralized Service node for route exchange into the VRF on **EOS3**. The CE 
      node (**EOS20**) will use BGP ASN 500.

      .. code-block:: text

         router bgp 100
            !
            vrf SVC
               neighbor 10.3.20.20 remote-as 500
               neighbor 10.3.20.20 maximum-routes 12000 
               !
               address-family ipv4
                  neighbor 10.3.20.20 activate

#. Now that the PE node is configured, configure CE node **EOS20** for Layer 3 attachment to the Service Provider network.

   #. Configure the BGP peerings to the PE devices on **EOS20**  ensuring that the router's Loopback0 address is advertised 
      to the attached PE.

      .. code-block:: text

         router bgp 500
            router-id 20.20.20.20
            neighbor 10.3.20.3 remote-as 100
            neighbor 10.3.20.3 maximum-routes 12000 
            network 20.20.20.20/32

   #. Verify the BGP peering is active but that no routes have been learned from the PE.

      .. code-block:: text

         show ip bgp summary
         show ip bgp detail
         show ip route

#. With the Centralized Service attached to the Service Provider network, configure restricted access to the service IP 
   of ``20.20.20.20`` without using ACLs, allowing only **EOS12** and **EOS19** to access the Service.

   #. First, define a new **RT** of ``500:500`` that will be used for importing routes from **EOS12** and **EOS19** into the ``SVC`` 
      VRF on **EOS3**

      .. note::

         The PE Nodes attached to Customer-1 and Customer-2 will handle the ``export`` of the routes for **EOS12** and **EOS19** 
         with the proper **RT**, so on **EOS3** we only need to worry about importing EVPN Type-5 routes with ``500:500`` into the 
         Centralized Services VRF.

      .. code-block:: text

         router bgp 100
            !
            vrf SVC
               route-target import evpn 500:500

   #. Now, 







**LAB COMPLETE!**
#. Allow CE devices EOS12 and EOS19 to access the Centralized Service at 20.20.20.20.

   - EOS11, EOS13, EOS15 and EOS18 must not be able to ping 20.20.20.20.
