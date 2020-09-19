Leverage SR-TE to Steer VPN Traffic
==================================================================

.. image:: ../../images/ratd_mesh_images/ratd_mesh_srte.png
   :align: center
  
|

#. Log into the **LabAccess** jumpserver to prepare the lab environment.

   #. From the Main Menu, type ``labs`` or Option 97 for ``Additional Labs``.

   #. Type ``mesh-topology-supplemental-labs`` to access the Supplemental Labs.

   #. Type ``srte`` at the Labs Selection Menu. The script will configure the topology 
      with the necessary prerequisites.

#. In the first scenario, we will use Segment Routing Traffic Engineering, or **SR-TE** to manipulate L3VPN traffic for 
   Customer-1. Configure the Service Provider network so that traffic from **EOS15** to **EOS12** follows the path pictured 
   above.

   #. First, create a Prefix-List and Route-Map **EOS1** and **EOS6** to set the BGP **Color** community on the route for 
      **EOS12**.

      .. note::

         The BGP Color community is used to identify routes on the ingress PE that should be steered by the SR-TE policy, 
         which we will see in a later step. Since the route for **EOS12**, ``12.12.12.12/32`` is received by both PEs, we can 
         set the policy on both.

      .. code-block:: text

         ip prefix-list
         !
          


**LAB COMPLETE!**
