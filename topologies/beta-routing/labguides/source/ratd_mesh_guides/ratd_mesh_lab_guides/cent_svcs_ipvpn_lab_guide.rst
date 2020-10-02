Offer Centralized Services to L3VPN Customers
=========================================================================

.. image:: ../../images/ratd_mesh_images/ratd_mesh_cent_svcs_l3vpn.png
   :align: center

|

#. Log into the **LabAccess** jumpserver to prepare the lab environment.

   #. From the Main Menu, type ``labs`` or Option 97 for ``Additional Labs``.

   #. Type ``mesh-topology-ldp-ipvpn-base-labs`` to access the LDP and IPVPN Labs.

   #. Type ``centsvcs`` at the Labs Selection Menu. The script will configure the topology with the necessary prerequisites.

#. The Centralized Service is attached to Service Provider node **EOS3**. These will be our **PE** node. Since this 
   Centralized Service will be accessed via a Layer 3 VPN Service, create an isolated VRF for its traffic and use EVPN 
   to advertise the customer networks to other interested PEs.

   #. Create a VRF Instance called ``SVC`` on **EOS3**.

      .. note::

         While this service will be accessed by Customers attached to other PEs, we will leverage IP-VPN to allow for 
         inter-VRF communication and only require the ``SVC`` VRF where the node attaches to the Service Provider network.

      .. code-block:: text

         vrf instance SVC
         !
         ip routing vrf SVC
         !
         ipv6 unicast-routing vrf SVC

   #. Place the interface attached to the **CE** node for the Centralized Service into VRF ``SVC`` on **EOS3** to ensure its 
      traffic remains isolated.

      .. code-block:: text

         interface Ethernet6
            vrf SVC
            ip address 10.3.20.3/24
            ipv6 address fd00:3:20::3/64

   #. Now leverage IP-VPN to advertise reachability of any routes learned in VRF ``SVC`` from the Centralized Service by 
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
               route-target export vpn-ipv4 5:5
               route-target export vpn-ipv6 5:5

   #. Finally, define the BGP peer facing the Centralized Service node for route exchange into the VRF on **EOS3**. The CE 
      node (**EOS20**) will use BGP ASN 500.

      .. code-block:: text

         router bgp 100
            !
            vrf SVC
               neighbor 10.3.20.20 remote-as 500
               neighbor 10.3.20.20 maximum-routes 12000 
               neighbor fd00:3:20::20 remote-as 500
               neighbor fd00:3:20::20 maximum-routes 12000 
               !
               address-family ipv4
                  neighbor 10.3.20.20 activate
               !
               address-family ipv6
                  neighbor fd00:3:20::20 activate

#. Now that the PE node is configured, configure CE node **EOS20** for Layer 3 attachment to the Service Provider network.

   #. Configure the BGP peerings to the PE devices on **EOS20**  ensuring that the router's Loopback0 address is advertised 
      to the attached PE.

      .. code-block:: text

         router bgp 500
            router-id 20.20.20.20
            neighbor 10.3.20.3 remote-as 100
            neighbor 10.3.20.3 maximum-routes 12000 
            neighbor fd00:3:20::3 remote-as 100
            neighbor fd00:3:20::3 maximum-routes 12000
            !
            address-family ipv4
               network 20.20.20.20/32
            !
            address-family ipv6
               neighbor fd00:3:20::3 activate
               network 20:20:20::20/128

   #. Verify the BGP peering is active but that no routes have been learned from the PE.

      .. code-block:: text

         show ip bgp summary
         show ip bgp detail
         show ip route
         show ipv6 bgp summary
         show ipv6 bgp detail
         show ipv6 route

#. With the Centralized Service attached to the Service Provider network, configure restricted access to the service IP 
   of ``20.20.20.20`` without using ACLs, allowing only **EOS11** and **EOS19** to access the Service.

   #. First, define a new **RT** of ``500:500`` that will be used for importing routes from **EOS11** and **EOS19** into the 
      ``SVC`` VRF on **EOS3**

      .. note::

         The PE Nodes attached to Customer-1 and Customer-2 will handle the ``export`` of the routes for **EOS11** and 
         **EOS19** with the proper **RT**, so on **EOS3** we only need to worry about importing VPNv4 and v6 routes with 
         ``500:500`` into the Centralized Services VRF.

      .. code-block:: text

         router bgp 100
            !
            vrf SVC
               route-target import vpn-ipv4 500:500
               route-target import vpn-ipv6 500:500

   #. Now, export the route for ``11.11.11.11/32`` and ``11:11:11::11/128`` from the Customer-1 VRF on PE nodes **EOS1** 
      using the **RT** of ``500:500``. To ensure only the route for **EOS11** is exported on the PEs, use a Route-Map and 
      Prefix-List to control application of the **RT**.

      .. note::

         Applying the route-map to the IP-VPN ``export`` statement will allow ``500:500`` to be tagged onto the VPN route 
         in addition to the Customer-1 default **RT** of ``1:1``.

      .. code-block:: text

         ip prefix-list SVC-ACCESS seq 10 permit 11.11.11.11/32
         !
         ipv6 prefix-list SVC-ACCESS
            seq 10 permit 11:11:11::11/128
         !
         route-map EXPORT-TO-SVC permit 10
            match ip address prefix-list SVC-ACCESS
            set extcommunity rt 500:500 additive
         !
         route-map EXPORT-TO-SVC permit 20
            match ipv6 address prefix-list SVC-ACCESS
            set extcommunity rt 500:500 additive
         !
         route-map EXPORT-TO-SVC permit 30
         !
         router bgp 100
            !
            vrf CUSTOMER-1
               route-target export vpn-ipv4 route-map EXPORT-TO-SVC
               route-target export vpn-ipv6 route-map EXPORT-TO-SVC

   #. Similarly, on **EOS7**, configure a Route-Map and Prefix-List to export the route for **EOS19**, ``19.19.19.19/32``, 
      with the **RT** of ``500:500``.

      .. code-block:: text

         ip prefix-list SVC-ACCESS seq 20 permit 19.19.19.19/32
         !
         ipv6 prefix-list SVC-ACCESS
            seq 10 permit 19:19:19::19/128
         !
         route-map EXPORT-TO-SVC permit 10
            match ip address prefix-list SVC-ACCESS
            set extcommunity rt 500:500 additive
         !
         route-map EXPORT-TO-SVC permit 20
            match ipv6 address prefix-list SVC-ACCESS
            set extcommunity rt 500:500 additive
         !
         route-map EXPORT-TO-SVC permit 30
         !
         router bgp 100
            !
            vrf CUSTOMER-4
               route-target export vpn-ipv4 route-map EXPORT-TO-SVC
               route-target export vpn-ipv6 route-map EXPORT-TO-SVC

   #. Now, allow PE **EOS1** to import the route for the Centralized Service with the **RT** of ``5:5`` into the VRF for 
      Customer-1.

      .. note::

         This will allow the PE to advertise the route for the Centralized Service, ``20.20.20.20/32`` and 
         ``20:20:20::20/128``, to the attached CE node.

      .. code-block:: text

         router bgp 100
            !
            vrf CUSTOMER-1
               route-target import vpn-ipv4 5:5
               route-target import vpn-ipv6 5:5

   #. Finally, repeat the above step on **EOS7** to import the Centralized Service route into the VRF for Customer-4.

      .. code-block:: text

         router bgp 100
            !
            vrf CUSTOMER-4
               route-target import vpn-ipv4 5:5
               route-target import vpn-ipv6 5:5

#. With the necessary inter-VRF route leaking configuration in place, validate the **EOS11** and **EOS19** can reach the 
   Centralized Service while other CE nodes for the Customers cannot.

   #. View the routing tables of **EOS11** and **EOS19** to ensure the route for the Centralized Service, ``20.20.20.20/32`` 
      and ``20:20:20::20/128`` is present.

      .. code-block:: text

         show ip route 20.20.20.20
         show ipv6 route 20:20:20::20

   #. Verify connectivity from **EOS11** and **EOS19** to the Centralized Service at ``20.20.20.20`` from each router's 
      Loopback0 IP.

      .. note::

         As mentioned earlier, MPLS forwarding for IPv6 overlay traffic does not working in vEOS-lab. The control-plane can 
         still be validated for IPv6.

      **EOS11**

      .. code-block:: text

         ping 20.20.20.20 source 11.11.11.11

      **EOS19**

      .. code-block:: text

         ping 20.20.20.20 source 19.19.19.19

   #. Display the routing table of **EOS20** to ensure only the routes for the allowed Customer nodes are present.

      .. note::

         Only routes for the Loopback0 interfaces of **EOS11** and **EOS19** should be learned from the Service Provider 
         network.   

      .. code-block:: text

         show ip route bgp
         show ipv6 route bgp

   #. Confirm that other Customer-1 and Customer-2 nodes cannot access the Centralized Service.

      .. note::

         **EOS12** and **EOS13** will have the route for the Centralized Service due to redistribution of BGP into OSPF, but 
         since the Centralized Service does not have a return route, no connections can be completed. Other customer nodes 
         will not have the route at all.

      .. code-block:: text

         show ip route bgp
         show ipv6 route bgp
         ping 20.20.20.20 source **<Loopback0 IP>**

#. On the Service Provider network, verify that the Centralized Service routes and approved Customer node routes are being 
   exchanged with the proper IP-VPN and MPLS information.

   #. On **EOS3**, verify the incoming routes for forwarding path for **EOS11** and **EOS19** from the ``SVC`` VRF.

      .. note::

         The VPN routes have two RTs attached to them; one from the standard L3VPN export and one from the Route-Map to 
         ensure it is imported properly into the ``SVC`` VRF. Since the Route-Map has the ``additive`` keyword, it will allow 
         both to be present and not overwrite.

      .. code-block:: text

         show bgp vpn-ipv4 detail | section 500:500
         show bgp vpn-ipv6 detail | section 500:500
         show ip route vrf SVC
         show ipv6 route vrf SVC

   #. On **EOS1**, verify the incoming routes for forwarding path for **EOS20**  from the ``CUSTOMER-1`` VRF.

      .. code-block:: text

         show bgp vpn-ipv4 detail | section 5:5
         show bgp vpn-ipv6 detail | section 5:5
         show ip route vrf CUSTOMER-1
         show ipv6 route vrf CUSTOMER-1


**LAB COMPLETE!**