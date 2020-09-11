Establish MPLS transport label distribution via Segment-Routing
=========================================================================

   .. image:: ../../images/ratd_ring_images/ratd_ring_isis_sr.png
      :align: center

    #. Enable Segment-Routing extensions to IS-IS, leveraging MPLS data plane encapsulation.
      
        - The Segment Routing Global Block (SRGB) label range should be 900,000 – 965,535 on all Service Provider nodes.
   
    #. Configure each node should with a globally unique Node SID equal to 900,000 + NodeID.
 
        - For example, EOS1 should have a Node SID of 900,001.
   
    #. Review IS-IS adjacency SIDs on EOS7 and EOS8.
 
        :Question:
            Is there overlap? If so, will this present an issue? Why or Why not?
   
    #. Validate that all Service Provider nodes have a globally unique Node SID.
   
    #. To protect against black holes, and reduce convergence time:
 
        - Enable the equivalent of IGP Sync and Session-Protection within the Segment-Routing domain.
   
    #. Once this task has been completed, all Service Provider nodes should have an LSP established for reachability between loopbacks.

       .. code-block:: text

         ping mpls segment-routing ip x.x.x.x/32 source y.y.y.y

       .. code-block:: text

         traceroute mpls segment-routing ip x.x.x.x/32 source y.y.y.y