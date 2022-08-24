CloudVision Studios  -  L3LS/EVPN LAB GUIDE
===========================================



The "Datacenter1" topology for this lab consists of two **spines,** four **leafs**, and two **"hosts"** for reachability testing. The borderleafs, cores, and Datacenter 2 are not a part of this lab guide. 
The hosts will be pre-configured as L2 LACP trunk port-channels up to their respective leafs. 
VLAN 60 and 70 will be pre-configured with SVIs on each host for post change reachability testing. 
All underlay addressing will be performed by CVPS.

The hosts are already configured via lab configlets, we will not be involving them in the Studios process. 
|br| First, provision the via lab console and run  option 6, ``CVP lab for Studios L3LS/EVPN (studiosl3ls)`` 
|br| Allow the task to complete, and proceed to step 1. 

.. thumbnail:: images/cvp_studios_l3ls_evpn/3TOPO.PNG
	:align: center
	:width: 50%

Open CVP via the topology page and login. 

1. Workspace Creation


   a. Navigate to **Provisioning>Studios>Create Workspace**. Name it **"LAB"**
   #. Once created, go to the **"Inventory Studio"**


      .. thumbnail:: images/cvp_studios_l3ls_evpn/4WorkspaceIntro.gif
         :align: center
         :width: 50%

