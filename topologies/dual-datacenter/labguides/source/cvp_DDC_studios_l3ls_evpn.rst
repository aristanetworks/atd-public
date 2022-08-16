.. # define a hard line break for HTML
.. |br| raw:: html

   <br />

.. raw:: html

 <style>.red{color:#aa0060; font-weight:bold; font-size:16px}</style>
.. role:: red


CloudVision Studios  -  L3LS/EVPN LAB GUIDE
===========================================



Our "Datacenter1" topology for this lab consists of two spines, four leafs, and two "hosts" for reachability testing. The borderleafs, cores, and Datacenter 2 are not a part of this lab guide. 
Our hosts will be pre-configured as L2 LACP trunk port-channels up to their respective leafs. 
VLAN 60 and 70 will be pre-configured with SVIs on each host for post change reachability testing. 
All underlay addressing will be performed by CVPS.

The hosts are already configured via lab configlets, we will not be involving them in the Studios process. 
|br| First, provision the via lab console and run  option 6, ``CVP lab for Studios L3LS/EVPN (studiosl3ls)`` 
|br| Allow the task to complete, and proceed to step 1. 

.. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/3TOPO.PNG
	:align: center
	:width: 50%


 
Let’s open CVP via the topology page, and get started!

1. Workspace Creation


   a. Navigate to **Provisioning>Studios>Create Workspace**. Name it **"LAB"**
   b. Once created, let's go to the **"Inventory Studio"**


.. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/4WorkspaceIntro.gif
   :align: center
   :width: 50%


2. Inventory studio
    
   a. Navigate to **Provisioning>Studios>Inventory and Topology**.
   b. Enter the studio and click the *“add updates”* tab.
   c. Select ``s1-Spines`` and  ``s1-leaf1-4``, Ignore anything else. 
   d. Click **"Add Updates"**.
   e. Notice that there are devices now in the *“onboarded devices”* section. 
   f. Enter the device and see how Studios has detected the topology connections.





.. note:: This is where we will tell studios which devices to include, and the studio will know how the physical topology is built via lldp. It will allow the other studios to auto detect links to assign properly for a functional network.
  


.. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/5Inventory.gif
   :align: center
   :width: 50%

3. Workspace review

    
   a. Click on *“Review Workspace”* on the upper right. This will take us to the *"Workspace Summary"* page to save our inputs for this studio to the staging area for later use. 
  |br| Once we hit review, it will run through the checks and tell us if we are good to proceed. You can see in the workspace summary what studios have been modified.
  |br| **In the current CVPS build the build process will only kick off automatically the first time. As we modify other studios, we will manually start this process by clicking "Start Build".** 
 
 
  .. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/6InventoryBuild.PNG
   :align: center
   :width: 50%
 
 
 .. note:: You can absolutely make a separate workspace for every studio if you wish, however for this lab we are going to do all this work in the same workspace, because we need  to demonstrate how this process builds on itself in the  staging area. 




 

4. Device Tagging

Tagging is used to easily group devices and assign them to a studio. 
|br| This can be done from within a workspace even though it's technically not a studio.
|br| There are user tags and tags the system creates using the *"auto tagger"* as we move through our studio configurations. 
|br| Tags are formed in a **label:value format.** For this lab, we will be using ``“DC:DC1”`` for all assets in ``DC1``,

a. Go to the Provisioning tab and click *"Tags"* on the lower left 
   
 
 .. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/7tagslocation.PNG
   :align: center
   :width: 50%


b. tag devices with ``“DC:DC1”`` 


.. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/8tagsprocess.gif
   :align: center
   :width: 50%

.. note:: You can use almost any naming convention that makes sense for your use case. Examples are for this lab.



c. Click on **"Review Workspace"** in the upper right and observe that the workspace now shows we have two tag changes. 
d. Trigger the *“start build”* and allow the build process to complete. 

|br| Let's move on with the lab, we are going to focus on **L3LS** first, then do **EVPN** after.


5. L3LS Studio

   a. Navigate to the **Provisioning>Studios>L3 Leaf-Spine Fabric** studio. 
   b. Set our tag query to assign our devices.
   c. include all devices with the ``DC:DC1`` tag pair. You’ll see the number of devices it finds and their IDs.
   d. In the "Data Centers" section, let's use a value of **"1"**  *(this can be a name or an integer, but for the lab let's use the aforementioned value)*
   e. Once complete, click the arrow to proceed into the configuration.  


.. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/9L3LSPT1.gif
   :align: center
   :width: 50%

   |br|
**Important Tip:** 
|br| **Anytime you see “create” in a field the autotagger is automatically creating a tag for the devices included in the studio. We’ll come back to this later.** 



|br| Now, we need to assign the individual devices from our query, assign the **fabric device roles**, and create our pod. 
|br| The Fabric Device section is critical. Here we will set our **roles** and **ID** numbers. Every Spine and Leaf requires a unique number. 

|br| Let’s do this now. 

f. assign roles and device numbers for each switch
|br|

 


.. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/10L3LSPT2.gif
   :align: center
   :width: 50%
  
   
   


|br| Once complete, let's "**Add Pod**", give it a name of *“1”* then make use of the arrow in the pod field to move on. 

g. Add Pod 1
h. Enter Pod 1 configuration
i. Manually add swiches to "Assigned Devices up top"
j. Add the spines first, and you’ll see them automatically get added! 
k. Now add the leafs. 
l. Make the  **leaf domains.** 

.. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/11L3LSPT3.gif
   :align: center
   :width: 50%

|br| A leaf domain can be a pair of switches or a standalone. So in this lab, we need to make two. 
|br| ``s1-leaf1`` and ``s1-leaf2`` will be in ``Leaf Domain 1``, and ``s1-leaf3`` and ``s1-leaf4`` will be in ``Leaf Domain 2``. 

   .. warning:: Leaf Domains must be an integer or the build process will fail.



And that’s it! 

|br| Our next step is to review the workspace. But before we do that, let's have a good look  at the lower section. 
|br| These are all the variables that the topology will be built on. For this lab we’ll leave it all at defaults. 
|br| Also noteworthy are those blue knobs below. 

|br| They set BGP dynamic listeners on the Spines,configure the VXLAN Overlay and get the topology ready for EVPN. 
|br| If all you wanted was strictly L3LS as a foundation you could turn off VXLAN/EVPN if you so chose.      

.. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/12L3LSPT4.PNG
   :align: center
   :width: 50%

Let's start our build! Now remember, we need to manually kick the build off, and if everything went according to plan, we will get three green checks. 

  .. note:: Notice the tag changes have increased, and L3 Leaf-Spine Fabric is in the list of modified studios.  

.. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/13L3LSPT5.gif
   :align: center
   :width: 50%

Success! Now that we have these changes saved to our workspace, let’s work on EVPN, which will pull data from this configuration. 

6. EVPN Studio


- Navigate to the **Provisioning>Studios>EVPN Services** studio. 

Once again, we need to add our device query. But seeing as how this is EVPN, our focus is on the leafs. 

a. Use  ``DC:DC1 AND Role:Leaf`` as our query
b. Create tenant, which we’ll call **“A”**.
c. Enter tenant for further configuration 

.. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/14EVPNPT1.gif
   :align: center
   :width: 50%

|br| d. set up VRF, **“A”**, and enter the configuration.
|br| 
|br| The only required entry here is the **VNI**. Your **VNI** can be whatever you want, just ensure it does not conflict with the VNI the VLANS will get auto assigned with (though you can override the VNI on the VLAN page) 
|br| As best practice we will set our **VNI** as **50000**.

d. Set VNI to 5000
e. Exit back to Tenant to configure vlans



Our next step is to create the vlans in the VRF, and assign them to the devices that will carry them. 

|br| f. In the Tenant, add ``60`` in the vlan field then enter configuration.
|br| g. Choose the "A" tenant, name the VLAN  “PROD” and then set SVI of **10.60.60.1/24** 
|br| h. Scroll down to Devices and use ``DC:DC1 AND Role:Leaf`` as our search, then enter configuration. 
|br| i. Change "Apply" on all devices to "Yes"
|br| j. Repeat the above steps with ``vlan70``, name PROD2 and set SVI of **10.70.70.1/24** 

.. warning:: The CIDR is required. 

.. note::
   |br| Notice how when you add the leafs to the vlan the router_bgp.router_id and router_bgp.as variables auto-filled. 
   |br| The studio is pulling this information directly from our information stored from our L3LS studio! 

.. note::




.. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/15EVPNPT2.gif
    :align: center
    :width: 50%

   


   


.. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/16EVPNPT3.gif
   :align: center
   :width: 50%



As the final step of this studio, let's  create our vlan aware bundle. 
|br| (if you are cross vendor, you might not be able to use VLAN Aware Bundles)

|br| k. In the tenant, scroll down to Vlan Aware Bundles and create it. 
|br| l. Call it **"BUNDLE”** then enter the configuration. 
|br| m. Use 60,70 as our vlan range for this example.  


.. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/16.1EVPNPT3.png
   :align: center
   :width: 50%

|br| We’re done with the EVPN studio! Let’s see if our inputs are correct. Click review workspace and then start the build.  

.. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/17EVPNPT4.gif
   :align: center
   :width: 50%

|br| Success! We now have a working L3LS/EVPN topology, but not for the hosts yet. We need to configure the port-channels on the leafs to the hosts below them. 
|br|
|br| For that, let’s use the **Interface Configuration Studio** and then we’ll test connectivity across the fabric. 


7. Interface Studio

  
Let’s take a look at our topology. The hosts are already pre configured for PO1 on ports ``E1-2`` in LACP. 
|br| Our yet to be configured Leafs are connected to the hosts on ``E4`` and ``E5``. 

.. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/18-topoforPO.PNG
   :align: center
   :width: 50%

The hosts are also configured in vlan 60 and 70 with respective SVIs for testing. 
Let’s navigate to our Interface Studio and start our configuration. 
  
  
a. Navigate to the **'Provisioning>Studios>Interface Configuration”** studio. 
b. Add the search query ``DC:DC1 AND Role:Leaf`` to assign devices to the studio
c. Create a profile, named **“MLAG-PO”**, and enter configuration.
d. Set as **trunk port**, set native VLAN of **“1”**, allow ``vlan60`` and ``vlan70``, set PO to **"1"**, check **“yes”** for mlag. 


.. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/19-intstudio1.gif
   :align: center
   :width: 50%


e. apply the profile to port ``E4`` on each leaf pair.


   .. thumbnail:: images/cvp_DDC_studios_l3ls_evpn/20-intstudio1.gif
    :align: center
    :width: 50%

8. Final Revew and Submission to Change Control
    a. Hit “Start Build” and you should get a successful action. 


   .. warning:: As discussed, we are going to commit this workspace as a final build to studios. Once we submit, this workspace will close out and it cannot be modified. However, because our inputs are committed to Studios (the repository) we can open up a new workspace and make/add/remove new changes. 


b. Hit “Submit Workspace” to close out and create our Change Control. 
 
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

8. Lab Verification

   |br| a. Log into the  Spines and run **sh bgp summary**, verify underlay and overlay BGP adjacencies are **Established**.
   |br| b. Repeat for Leafs. Outputs should be similar.





SPINES - BGP Summary
----------------------
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
----------------------

.. code-block:: bash 
 
 Neighbor               AS Session State AFI/SAFI                AFI/SAFI State   NLRI Rcd   NLRI Acc
 172.16.0.1            65000 Established   L2VPN EVPN              Negotiated              8          8
 172.16.0.2            65000 Established   L2VPN EVPN              Negotiated              8          8
 172.16.200.0          65000 Established   IPv4 Unicast            Negotiated             10         10
 172.16.200.2          65000 Established   IPv4 Unicast            Negotiated             10         10
 192.168.255.255       65001 Established   IPv4 Unicast            Negotiated             13         13


c. Verify MLAG on our Leafs. On Leafs 1-4 run the **“show mlag”** command 
d. Verify all Leafs show as **“Active”** and **“Up-Up.”**

.. code-block:: bash 
   
 MLAG Status:                     
 state                              :              Active
 negotiation status                 :           Connected
 peer-link status                   :                  Up
 local-int status                   :                  Up

e. On leafs 1 and 3 verify the  Port-Channel status. 
f. Run the command **“sh port-channel dense”**

 .. note:: MLAG has an enhancement where the port-channel command will show the status of the port channel across both switches in the pair. See the section below. This output shows the status and configuration of the MLAG PortChannel of the local switch as well as the peer, with the **(P)** being the opposite switch. 

.. code-block:: bash 
   
   Port-Channel       Protocol    Ports             
   Po1(U)            LACP(a)     Et1(PG+) Et2(PG+) PEt1(P) PEt2(P)


Now that we’ve confirmed all our base connectivity, let’s test our fabric and look at some outputs. 

|br| g. Ping the gateway at **10.60.60.1**. from ``s1-host1``.
|br| h. Ping the SVI local to the switch at at **10.60.60.160**. from ``s1-host1``.
|br| i. Ping across the fabric in the same vlan, from ``s1-host1`` **10.60.60.160** to ``s1-host2`` **10.60.60.161.**
|br| j. Ping across the fabric intervlan from ``s1-host1`` **10.60.60.160** to ``s1-host2`` **10.70.70.171.**
|br| k. On ``s1-leaf1``, review the EVPN routing table using **“show bgp evpn“**.
|br| l. On ``s1-host1`` and on ``s1-host2`` do **“show int vlan 60”**  and make note of their **mac.**
|br| m. On ``s1-leaf1``, do ``“show mac address-table vlan 60”``.
|br| n. notice ``s1-host1’s`` mac comes across PO1 and ``s1-host2’s`` comes across Vx1.



**LAB COMPLETE!**
--------------------------------

