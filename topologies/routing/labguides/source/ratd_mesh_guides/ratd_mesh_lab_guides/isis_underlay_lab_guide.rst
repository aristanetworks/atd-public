Deploy IS-IS as the Service Provider Underlay IGP
==========================================================

.. image:: ../../images/ratd_mesh_images/ratd_mesh_isis_sr.png
   :align: center
  
.. note::
   The Base Labs of the Routing ATD are structured to build on each other. You should complete 
   all Base Labs before moving onto Supplemental Labs. Alternatively, using the Lab Selection 
   Menus will complete configurations for prior labs as necessary. Supplemental Labs can be 
   completed in any order.

#. Log into the **LabAccess** jumpserver to prepare the lab environment.

   #. From the Main Menu, type ``labs`` or Option 97 for ``Additional Labs``.

   #. Type ``mesh-topology-base-labs`` to access the Base Setup Labs.

   #. Type ``reset`` at the Labs Selection Menu. The script will configure the topology 
      with the necessary prerequisites.

      .. admonition:: Did you know?

         The ``reset`` option (and all other options) makes use of CloudVision Portal APIs 
         to apply "configlets" to each EOS node ensuring they have the proper configuration.
         
#. Prior to configuration, verify the topology's base status.

   #. On **EOS1**, verify interface configurations and neighbors.

      .. note::

         Full commands will be typed for reference in lab steps, but commands in EOS can be 
         shortened or tab-completed at the user's discretion.

      .. code-block:: text

         show ip interface brief
         show run interfaces Ethernet1-5
         show lldp neighbors

   #. Verify there is **no** routing protocol configuration or neighbors present as of yet.

      .. code-block:: text

         show run section isis
         show run section bgp
         show isis neighbors
         show ip bgp summary

#. Configure the IS-IS routing protocol on the **EOS1** router using the following steps.

   #. Enable IS-IS with an instance ID of ``100`` and define a **NET** or Network Entity Title. For the 
      NET, use the format of ``49.1111.0000.000`` **(EOS ID)** ``.00`` where ``1111`` is the IS-IS area 
      ID and ``0000.000`` **(EOS ID)** is the System ID.

      .. note::

         Arista EOS utilizes the Industry-Standard CLI. When entering configuration commands, be 
         sure to first type ``configure`` to enter configuration mode.

      .. code-block:: text

         router isis 100
            net 49.1111.0000.0001.00

   #. Set the IS-IS level to level-2 and activate the IPv4 unicast address-family to ensure the 
      router will hold all backbone IPv4 routes.

      .. code-block:: text

         router isis 100
            is-type level-2
            !
            address-family ipv4 unicast

   #. To shrink the overall size of the LSDB and routing table, we will only advertise Loopback /32 networks 
      to other EOS routers and not individual link addressing. This is accomplished by only advertising 
      passive IS-IS interfaces and networks.

      .. code-block:: text

         router isis 100
            advertise passive-only

   #. Verify protocol configuration thus far.

      .. admonition:: Pro-Tip
      
         You do **not** need to ``exit`` configuration mode to execute show commands in EOS.

      .. code-block:: text

         show run section isis

#. Configure IS-IS interfaces on **EOS1**.

   #. All links connecting to other SP routers (EOS1 through EOS8) will form IS-IS adjacenies. Configure 
      the link between **EOS1** and **EOS2** as an IS-IS interface.

      .. code-block:: text

         interface Ethernet1
            isis enable 100

   #. Additionally, since this is point to point link to a level-2 router, we will define those characteristics 
      to ensure proper peering and bypass unnecessary DIS elections.

      .. code-block:: text

         interface Ethernet1
            isis circuit-type level-2
            isis network point-to-point

   #. Repeat the above configurations for the other interfaces on **EOS1** that are attached to adjacent 
      SP nodes. Refer to the diagram above and LLDP neighbor information for interfaces requiring configuration.

      .. admonition:: Pro-Tip

         You can configure multiple interfaces at once using ranges and separators in EOS. For example, **EOS1** 
         interfaces Et2, 4 and 5 require IS-IS configuration, but the commands are the same for all interfaces. 
         You can type ``interface Ethernet2,4-5`` to enter configurations for all three at once.

   #. Next, the Loopback0 interface needs to be activated as an IS-IS interface.

      .. code-block:: text

         interface Loopback0
            isis enable 100

   #. Lastly, since Loopback0 is not attached to another router, we can set it as a passive interface for IS-IS 
      to ensure proper operation.

      .. code-block:: text

         interface Loopback0
            isis passive
      
      .. note::

         In addtion, this command works in conjunction with the ``advertise passive-only`` command in our IS-IS 
         protocol configuration. It ensures only our passive (i.e. Loopback0) interfaces will be advertised.

#. Since no other routers have been configured, there are no peers as of yet. Configure **EOS2** using the same 
   steps above.

   .. note::

      Each EOS node requires a unique NET. Following the format described above, **EOS2** will have a NET 
      of ``49.1111.0000.0002.00`` under the IS-IS configuration. In addtion, interfaces Et1 through 5 are all 
      attached to SP routers so will require IS-IS configuration.

#. With both **EOS1** and **EOS2** configured, verify IS-IS peering and route advertisement.

   #. Verify IS-IS adjacency and LSDB.

      .. code-block:: text

         show isis neighbors
         show isis interface
         show isis database detail

      .. note::

         IS-IS will automatically convert system IDs to configured hostnames to make show outputs easier to interpret.

   #. Verify routing table only show IS-IS routes for the associated Loopback0 /32 networks.

      .. code-block:: text

         show ip route

   #. Test reachability between Loopback0 interfaces from **EOS1** to **EOS2**.

      .. code-block:: text

         ping 2.2.2.2 source 1.1.1.1

#. Configure the remaining Service Provider nodes (**EOS3 - EOS8**) for IS-IS using the steps above. Verify routing tables 
   only show advertised Loopback0 interfaces for all nodes.


**LAB COMPLETE!**
