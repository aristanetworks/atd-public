Deploy E-LINE Service for Customer-3
=========================================================================

.. image:: ../../images/ratd_mesh_images/ratd_mesh_c3_eline.png
   :align: center

|

#. Log into the **LabAccess** jumpserver to prepare the lab environment.

   #. From the Main Menu, type ``labs`` or Option 97 for ``Additional Labs``.

   #. Type ``mesh-topology-ipvpn-labs`` to access the LDP and IPVPN Labs.

   #. Type ``c3eline`` at the Labs Selection Menu. The script will configure the topology with the necessary prerequisites.

#. Customer-3 is attached to two Service Provider nodes, **EOS1** and **EOS4**. These will be **PE** nodes. Since this 
   customer will require a Layer 1 Wire Service, create a local patch and use an LDP Pseudowire to advertise the customers 
   port to the other interested PE.

   #. On **EOS1** and **EOS4**, configure the port facing CE devices **EOS17** and **EOS16** respectively.
      
      .. note::

         For a port-based service (which differs from a VLAN-based service), the CE-facing interface must be configured 
         as a routed interface with the ``no switchport`` command. We will also disable LLDP so those frames are not 
         consumed on the interface.

      .. code-block:: text

         interface Ethernet6
            no switchport
            no lldp transmit
            no lldp receive

   #. On **EOS1** and **EOS4**, create the logical patch name ``C3-E-LINE`` between the local CE interface and an, 
      that will be created with a name of ``EOS16-EOS17``.

      .. note::

         As the name implies, the ``patch-panel`` configuration allows for stitching together local and remote interfaces 
         using an emulated Layer 1 Service.

      .. code-block:: text

         patch panel
            patch C3-E-LINE
               connector 1 interface Ethernet6
               connector 2 pseudowire ldp EOS16-EOS17

   #. On **EOS1**, leverage LDP to advertise the Layer 1 Service to the peer node of **EOS4**. In addtion, use an MTU value 
      of 9000. Use the pseudowire name of ``EOS16-EOS17`` and an ID of ``1617``. These values must match on both ends of the 
      service.

      .. note::

         These values tie together the previous patch configuration.

      .. code-block:: text

         mpls ldp
            !
            pseudowires
               mtu 9000
               !
               pseudowire EOS16-EOS17
                  neighbor 4.4.4.4
                  pseudowire-id 1617

   #. Repeat the previous step on **EOS4** while adjusting the variables accordingly to match the other side of the service.

      .. code-block:: text

         mpls ldp
            !
            pseudowires
               mtu 9000
               !
               pseudowire EOS16-EOS17
                  neighbor 1.1.1.1
                  pseudowire-id 1617

#. Configure the Customer-3 CE nodes to connect to each other over the emulated LINE service.

   #. Since the Service Provider is providing a Layer 1 service, configure the CE on **EOS16** and **EOS17** interfaces 
      as OSPF peers as if they were attached back to back with a cable.

      .. note::

         The IP addressing on the links has already been configured by the base IPv4 configuration template.

      .. code-block:: text

         interface Ethernet1
            ip ospf network point-to-point
         !
         router ospf 300
            network 0.0.0.0/0 area 0.0.0.0
            max-lsa 12000

#. With all PE and CE nodes configured, verify connectivity between CE nodes **EOS16** and **EOS17**.

   #. Verify that all CE interfaces are able to resolve ARP for their peers and are able to see each other as LLDP neighbors.

      .. note::

         The Service Provider network is emulating the behavior of a Layer 1 connection and as such should be transparent to 
         the Layer 2 and 3 operations between the CE nodes. Note that depending on the holdtime of the CE LLDP table, the 
         PEs may still be present, but they should age out.

      .. code-block:: text

         show ip arp
         show lldp neighbor

   #. Verify OSPF adjacencies have formed between the CEs and routes have been exchanged.

      .. code-block:: text

         show ip ospf neighbor
         show ip route

   #. Test connectivity between CE Loopback0 interfaces from **EOS16** to **EOS17**.

      .. code-block:: text

         ping 17.17.17.17 source 16.16.16.16

#. Next, verify the LDP control-plane and MPLS data-plane for the customer E-LINE service.

   #. On **EOS1**, verify the local patch status.

      .. note::

         Take note of the ``MPLS label`` assigned to the local and remote nodes and that they may differ, since the VPN label 
         for the E-LINE service is locally significant.

      .. code-block:: text

         show interface Ethernet6
         show patch panel detail

   #. Verify the forwarding path for traffic on the pseudowire towards **EOS4** on **EOS1**.

      .. note::

         The In/Out section of the ``show patch panel forwarding`` output will show the VPN label for the PW and the 
         associated LDP tunnel index for the destination PE. This tunnel index can then be found in the output of the 
         ``show tunnel rib brief`` command.

      .. code-block:: text

         show patch panel forwarding
         show mpls ldp tunnel


**LAB COMPLETE!**