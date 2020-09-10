Enable L3VPN Multi-Pathing
=========================================================================
  
   #. Ensure that traffic from EOS15 to EOS12 uses multiple paths across the Service Provider network, distributing the load between EOS1 and EOS6.

      - It is ok to adjust the isis metric on the link between EOS6 and EOS8 in order to force multi-pathing to occur.

   #. EOS8 should have the following output from a ‘show ip route vrf A 12.12.12.12’ command:

      .. note::

         The specific labels may vary in your output.
  
      .. image:: ../../images/RATD_RING_Section7_Task_C.png
         :align: center 