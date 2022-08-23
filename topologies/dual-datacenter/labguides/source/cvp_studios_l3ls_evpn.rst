.. # define a hard line break for HTML
.. |br| raw:: html

   <br />

.. raw:: html

 <style>.red{color:#aa0060; font-weight:bold; font-size:16px}</style>
.. role:: red


CloudVision Studios  -  L3LS/EVPN LAB GUIDE
===========================================



The "Datacenter1" topology for this lab consists of two **spines,** four **leafs**, and two **"hosts"** for reachability testing. The borderleafs, cores, and Datacenter 2 are not a part of this lab guide. 
The hosts will be pre-configured as L2 LACP trunk port-channels up to their respective leafs. 
VLAN 60 and 70 will be pre-configured with SVIs on each host for post change reachability testing. 
All underlay addressing will be performed by CVPS.

The hosts are already configured via lab configlets, we will not be involving them in the Studios process. 
|br| First, provision the via lab console and run  option 6, ``CVP lab for Studios L3LS/EVPN (studiosl3ls)`` 
|br| Allow the task to complete, and proceed to step 1. 

.. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/3TOPO.PNG
	:align: center
	:width: 50%

Open CVP via the topology page and login. 

1. Workspace Creation


   a. Navigate to **Provisioning>Studios>Create Workspace**. Name it **"LAB"**
   #. Once created, go to the **"Inventory Studio"**


      .. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/4WorkspaceIntro.gif
         :align: center
         :width: 50%


#. Inventory studio
    
   a. Navigate to **Provisioning>Studios>Inventory and Topology**.
   #. Enter the studio and click the *“add updates”* tab.
   #. Select both ``s1-Spines`` and  ``s1-leaf1-4``, Ignore anything else. 
   #. Click **"Add Updates"**.
   #. Notice that there are devices now in the *“onboarded devices”* section. 
   #. Enter the device and see how Studios has detected the topology connections.





      .. note:: 
         This is where we will tell studios which devices to include, and the studio will know how the physical topology is built via lldp. It will allow the other studios to auto detect links to assign properly for a functional network.
  


   .. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/5Inventory.gif
         :align: center
         :width: 50%

#. Workspace Review
 
   .. note:: 
         You can  make a separate workspace for every studio if you wish, however for this lab we are going to do all this work in the same workspace, because we need  to demonstrate how this process builds on itself in the  staging area. 
  
   |br| Click on *“Review Workspace”* on the upper right. This will take us to the *"Workspace Summary"* page to store the inputs for this studio to the staging area for later use. 
   |br| Once we click review, it will run through the checks and tell us if we are good to proceed. You can see in the workspace summary what studios have been modified.



   .. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/6InventoryBuild.PNG
               :align: center
               :width: 50%



   .. note:: 
         In the current CVPS build the build process will only kick off automatically the first time. As we modify other studios, we will manually start this process by clicking "Start Build"
     


 
 

#. Device Tagging

   Tagging is used to easily group devices and assign them to a studio. 
   |br| This can be done from within a workspace even though it's technically not a studio.
   |br| There are user tags and tags the system creates using the *"auto tagger"* as we move through the studio configurations. 
   |br| Tags are formed in a **label:value format.** For this lab, we will be using ``“DC:DC1”`` for all assets in ``DC1``,

   a. Go to the Provisioning tab and click *"Tags"* on the lower left 
   
 
      .. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/7tagslocation.PNG
         :align: center
         :width: 50%


   b. tag devices with ``“DC:DC1”`` 


   .. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/8tagsprocess.gif
         :align: center
         :width: 50%

      .. note:: You can use almost any naming convention that makes sense for ythe use case. Examples are for this lab.



   c. Click on **"Review Workspace"** in the upper right and observe that the workspace now shows we have a tag change. 
   d. Trigger *“start build”* and allow the build process to complete. 

   |br| Proceed with the lab, we are going to focus on **L3LS** first, then do **EVPN** after.


#. L3LS Studio

   a. Navigate to the **Provisioning>Studios>L3 Leaf-Spine Fabric** studio. 
   #. Set the tag query to assign the devices.
   #. include all devices with the ``DC:DC1`` tag pair. You’ll see the number of devices it finds and their IDs.
   #. In the "Data Centers" section, use a value of **"1"**  
      *(this can be a name or an integer, but for the lab use the aforementioned value)*
   #. Once complete, click the arrow to proceed into the configuration.  


      .. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/9L3LSPT1.gif
         :align: center
         :width: 50%

   |br|
   **Important Tip:** 
   |br| **Anytime you see “create” in a field the autotagger is automatically creating a tag for the devices included in the studio. We’ll come back to this later.** 

   Every Spine and Leaf requires a unique number. 


   f. Assign devices to DC:1. 
   #. Assign roles and device numbers for each switch


      .. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/10L3LSPT2.gif
          :align: center
          :width: 50%
  
   
   


   |br| Once complete, click "**Add Pod**", give it a name of *“1”* then make use of the arrow in the pod field to move on. 

   .. note:: A leaf domain can be a pair of switches or a standalone. So in this lab, we need to make two. 
      Leafs ``s1-leaf1`` and ``s1-leaf2`` will be in ``Leaf Domain 1``, and ``s1-leaf3`` and ``s1-leaf4`` will be in ``Leaf Domain 2``. 
   
   
   
   h. Add Pod 1
   #. Enter Pod 1 configuration
   #. Manually add swiches to **Assigned Devices** up top
   #. Add the spines first, and you’ll see them automatically get added. 
   #. Make 2  **leaf domains.** 
   #. Assign leafs to their proper domains. 

   .. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/11L3LSPT3.gif
      :align: center
      :width: 50%



   .. warning:: Leaf Domains must be an integer or the build process will fail.



   |br| The next step is to review the workspace. But before we do that, have a good look  at the lower section. 
   |br| These are all the variables that the topology will be built on. For this lab we’ll leave it all at defaults. 
   |br| Noteworthy are those blue knobs below. 
   |br| They set BGP dynamic listeners on the Spines,configure the VXLAN Overlay and get the topology ready for EVPN. 
   |br| If all you wanted was strictly L3LS as a foundation you could turn off VXLAN/EVPN if you so chose.      

      
         
   .. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/12L3LSPT4.PNG
            :align: center
            :width: 50%

   Start the build. Remember, we need to manually kick the build off, and if everything went according to plan, we will get three green checks. 

   .. note:: Notice the tag changes have increased, and L3 Leaf-Spine Fabric is in the list of modified studios.  

   .. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/13L3LSPT5.gif
     :align: center
     :width: 50%

   Success! Now that we have these changes stored to the workspace, let’s work on EVPN, which will pull data from this configuration. 

#. EVPN Studio

   |br| Once again, we need to add the device query. But seeing as how this is EVPN, the focus is on the leafs. 

   a. Navigate to the **Provisioning>Studios>EVPN Services** studio. 
   #. Use  ``DC:DC1 AND Role:Leaf`` as the query
   #. Create tenant, which we’ll call **“A”**.     

   .. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/6InventoryBuild.PNG
               :align: center
               :width: 50%

   d. Enter tenant for further configuration. 

   .. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/14EVPNPT1.gif
      :align: center
      :width: 50%

   e. Create VRF **“A”**, and enter the configuration.
   
   .. note:: 
      The only required entry here is the **VNI**. The **VNI** can be whatever you want, just ensure it does not conflict with the VNI the VLANS will get auto assigned with (though you can override the VNI on the VLAN page) 
      As best practice we will set the **VNI** as **50000**.

   f. Set VNI to 5000.
   #. Exit back to tenant to configure vlans.



   |br| The next step is to create the vlans in the VRF, and assign them to the devices that will carry them. 

   h. In the Tenant, add ``60`` in the vlan ID  field then enter configuration.
   #. Name the VLAN  “PROD”, Choose the "A" VRF,  and then set SVI of **10.60.60.1/24** 
   #. Scroll down to Devices and use ``DC:DC1 AND Role:Leaf`` as the search, then enter configuration. 
   #. Change "Apply" on all devices to "Yes"
   #. Repeat the above steps with ``vlan70``, name PROD2 and set SVI to  **10.70.70.1/24** 

      .. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/15EVPNPT2.gif
       :align: center
       :width: 50%
   
   
   
   .. warning:: The CIDR is required. 

   .. note::
      |br| Notice how when you add the leafs to the vlan the router_bgp.router_id and router_bgp.as variables auto-filled. 
      |br| The studio is pulling this information directly from the information stored from the L3LS studio.






   
   As the final step of this studio, create the vlan aware bundle. 
   |br| (If you are cross vendor, you might not be able to use VLAN Aware Bundles)

   l. In the tenant, scroll down to Vlan Aware Bundles and create it. 
   #. Call it **"BUNDLE”** then enter the configuration. 
   #. Use 60,70 as the vlan range for this example.  

   


   .. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/16EVPNPT3.gif
      :align: center
      :width: 50%


   .. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/16.1EVPNPT3.png
      :align: center
      :width: 50%

   |br| We’re done with the EVPN studio
   |br|  Let’s see if the inputs are correct. Click review workspace and then start the build.  

   .. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/17EVPNPT4.gif
      :align: center
      :width: 50%

   |br| Success! We now have a working L3LS/EVPN topology, but not for the hosts yet. We need to configure the port-channels on the leafs to the hosts below them. 
   |br|
   |br| For that, let’s use the **Interface Configuration Studio** and then we’ll test connectivity across the fabric. 


#. Interface Studio

  
   Let’s take a look at the topology. The hosts are already pre configured for PO1 on ports ``E1-2`` in LACP. 
   |br| The leafs are connected to the hosts on ``E4`` and ``E5``. 

   .. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/18-topoforPO.PNG
      :align: center
      :width: 50%

   The hosts are also configured in vlan 60 and 70 with respective SVIs for testing. 
   Let’s navigate to the Interface Studio and start the configuration. 
   
   
   a. Navigate to the **'Provisioning>Studios>Interface Configuration”** studio. 
   #. Add the search query ``DC:DC1 AND Role:Leaf`` to assign devices to the studio
   #. Create a profile, named **“MLAG-PO”**, and enter configuration.
   #. Set as **trunk port**, set native VLAN of **“1”**, allow ``vlan60`` and ``vlan70``, set PO to **"1"**, check **“yes”** for mlag. 


   .. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/19-intstudio1.gif
      :align: center
      :width: 50%


   e. apply the profile to port ``E4`` on each leaf pair.


      .. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/20-intstudio1.gif
       :align: center
       :width: 50%

8. Final Revew and Submission to Change Control
    a. Click “Start Build” and you should get a successful action. 


   .. warning:: As discussed, we are going to commit this workspace as a final build to studios. Once we submit, this workspace will close out and it cannot be modified. However, because the inputs are committed to Studios (the repository) we can open up a new workspace and make/add/remove new changes. 


   b. Click “Submit Workspace” to close out and create the Change Control. 
 
   .. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/21-CC1.gif
      :align: center
      :width: 50%

   After the Workspace has been submitted and the Change Control created, you’ll see a *“View Change Control”* option. 

   c. Click  *“View Change Control”* to be taken to Change Control. 
   d. *“Review and Approve”* to prep the changes to the network. 
   e. Run the  changes in parallel, and choose "execute immediately" to apply to devices. 
   f. Click *“Approve and Execute”*. 


   |br| All tasks should complete successfully, and we can move onto the verification part of the lab.


   .. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/22-CC1.gif
      :align: center
      :width: 50%

   |br|
   |br|

#. Lab Verification

   a. Log into the Spines and run **sh bgp summary**
   #. Verify underlay and overlay BGP adjacencies are **Established**.
   #. Repeat for Leafs. Outputs should be similar.

   |br|

   SPINES - BGP Summary

   .. code-block:: bash 
      
      Neighbor               AS Session State AFI/SAFI                AFI/SAFI State   NLRI Rcd   NLRI Acc
      172.16.0.3          65001 Established   L2VPN EVPN              Negotiated              4          4
      172.16.0.4          65001 Established   L2VPN EVPN              Negotiated              4          4
      172.16.0.5          65002 Established   L2VPN EVPN              Negotiated              4          4
      172.16.0.5          65002 Established   L2VPN EVPN              Negotiated              4          4
      172.16.0.6          65002 Established   L2VPN EVPN              Negotiated              4          4
      172.16.200.1        65001 Established   IPv4 Unicast            Negotiated              7          7
      172.16.200.5        65001 Established   IPv4 Unicast            Negotiated              7          7
      172.16.200.9        65002 Established   IPv4 Unicast            Negotiated              7          7
      172.16.200.13       65002 Established   IPv4 Unicast            Negotiated              7          7

   LEAFS - BGP Summary

   .. code-block:: bash 
 
      Neighbor               AS Session State AFI/SAFI                AFI/SAFI State   NLRI Rcd   NLRI Acc
      172.16.0.1            65000 Established   L2VPN EVPN              Negotiated              8          8
      172.16.0.2            65000 Established   L2VPN EVPN              Negotiated              8          8
      172.16.200.0          65000 Established   IPv4 Unicast            Negotiated             10         10
      172.16.200.2          65000 Established   IPv4 Unicast            Negotiated             10         10
      192.168.255.255       65001 Established   IPv4 Unicast            Negotiated             13         13




   d. Verify MLAG on the Leafs. On Leafs 1-4 run the **“show mlag”** command 
   #. Verify all Leafs show as **“Active”** and **“Up-Up.”**

      .. code-block:: bash

         MLAG Status:                     
         state                              :              Active
         negotiation status                 :           Connected
         peer-link status                   :                  Up
         local-int status                   :                  Up


   f. On leafs 1 and 3 verify the  Port-Channel status. 
   #. Run the command **“sh port-channel dense”**

   .. code-block:: bash 
   
      Port-Channel       Protocol    Ports             
      Po1(U)            LACP(a)     Et1(PG+) Et2(PG+) PEt1(P) PEt2(P)



   .. note:: MLAG has an enhancement where the port-channel command will show the status of the port channel across both switches in the pair. See the section below. This output shows the status and configuration of the MLAG PortChannel of the local switch as well as the peer, with the **(P)** being the opposite switch. 




   |br| Now that we’ve confirmed all the base connectivity, let’s test the fabric and look at some outputs. 
	h. Ping the gateway at **10.60.60.1**. from ``s1-host1``.
	#. Ping the SVI local to the switch at at **10.60.60.160**. from ``s1-host1``.
	#. Ping across the fabric in the same vlan, from ``s1-host1`` **10.60.60.160** to ``s1-host2`` **10.60.60.161.**
	#. Ping across the fabric intervlan from ``s1-host1`` **10.60.60.160** to ``s1-host2`` **10.70.70.171.**
	#. On ``s1-leaf1``, review the EVPN routing table using **“show bgp evpn“**.
	#. On ``s1-host1`` and on ``s1-host2`` do **“show int vlan 60”**  and make note of their **mac.**
	#. On ``s1-leaf1``, do ``“show mac address-table vlan 60”``.
	#. notice ``s1-host1’s`` mac comes across PO1 and ``s1-host2’s`` comes across Vx1.


|br| 

**LAB COMPLETE!**

   
