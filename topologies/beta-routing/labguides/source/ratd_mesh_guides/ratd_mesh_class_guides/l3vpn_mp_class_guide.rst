Enable L3VPN Multi-Pathing
=========================================================================

   .. image:: ../../images/RATD-Section4+5+6+7-Image.png
      :align: center

   #. Ensure that traffic from EOS15 to EOS12 uses multiple paths across the Service Provider network, distributing the load between EOS1 and EOS6.
  
      - It is ok to adjust the isis metric on the link between EOS6 and EOS8 in order to force multi-pathing to occur.
  
   #. EOS8 should have the following output from a ‘show ip route vrf A 12.12.12.12’ command (label may vary, this is ok):
  
      .. image:: ../../images/RATD_Section7_Task_C.png
         :align: center   