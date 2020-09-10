Deploy IS-IS as the Service Provider Underlay IGP
==========================================================

   .. image:: ../../images/RATD-Section1+2-Image.png
      :align: center
  
   #. Configure IS-IS to carry underlay IPv4 prefix reachability information.
  
      - All nodes should be within the same flooding domain.
  
      - All nodes should only maintain a Level-2 database.
  
      - Ensure that there are no unnecessary Pseudonodes within the topology
  
   #. (Optional) Only advertise reachability information for /32 loopback interfaces into the LSDB
  
      - Once this task has been completed, all Service Provider nodes should be able to ping all other node loopback addresses