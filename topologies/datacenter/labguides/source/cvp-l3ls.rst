Layer 3 Leaf-Spine
==================

.. note:: For more details on the configuration we will apply to Leaf4, check out the UCN MLAG Lab.

**To access the command line of particular switch, click on that switch in the topology diagram at the top of the lab guide.**

1. Log into CloudVision and find Leaf4 on the **Devices** page.

   1. The username to access CloudVision is ``arista`` and the password is ``{REPLACE_ARISTA}``
   
   2. Search for ``leaf4`` in the **Device** column of the inventory table.

    .. image:: images/cvp-l3ls/leaf4-inventory-table.png
       :align: center
       :width: 50 %

   3. Click on **leaf4**.

2. Click on the **BGP** section on the left side navigation bar.

   1. Here we can see details for the BGP state of leaf4.

    .. image:: images/cvp-l3ls/leaf4-bgp-overview-pre.png
       :align: center
       :width: 50 %

   2. Notice that BGP does not appear to be configured on leaf4.

   3. Switch to **spine1** to see the status of spine1's BGP configuration.

    .. image:: images/cvp-l3ls/spine1-bgp-overview-pre.png
       :align: center
       :width: 50 %

   3. See that there is 1 unestablished peer and we can see the details for that attempted neighborship in the table.

   4. View these details for **spine2** as well.

3. Click **Metrics** at the top of the page

   1. In this section of CloudVision, users can create custom Dashboards to refer to particular telemetry data they find noteworthy.

   2. Click **create a new dashboard**.

   3. In the view builder on the left, select the values for each dropdown as listed below:
    
    ..   .. table::
       :widths: auto
       :align: center

       ==============  =========================
       Dashboard View
       -----------------------------------------                         
         View Mode     Table
        Metric Type    Devices                
          Metrics      BGP                     
                        - Established Peers    
                        - Unestablished Peers  
                        - Learned Paths        
                        - AS Number            
                        - Router-ID            
          Devices       - leaf1                 
                        - leaf2                 
                        - leaf3                 
                        - leaf4                 
                        - spine1                
                        - spine2                
       ==============  =========================

    .. image:: images/cvp-l3ls/bgp-dashboard-setup.png
       :align: center
       :width: 50 %

   4. Click **Save Dashboard** in the bottom left corner.
   
   5. If prompted to name the dashboard, give a name and click **Save**.

   6. Now there is a dashboard that displays BGP information for all switches in our leaf-spine network in one place.

4. Configure BGP on leaf4.

   1. Click **Provisioning** at the top of the page.

   2. Find **leaf4**, right click on it, and click **Manage -> Configlet**.

    .. image:: images/cvp-l3ls/leaf4-manage-configlet.png
       :align: center
       :width: 50 %

   3. Search for ``Leaf4-BGP-Lab-Full`` in the search bar, select the configlet, and click **Validate**.

    .. image:: images/cvp-l3ls/leaf4-add-bgp-configlet.png
       :align: center
       :width: 50 %

   4. Validate the Designed Configuration created by CloudVision from the Proposed Configlets against Leaf4's running configuration and click **Save**.

    .. image:: images/cvp-l3ls/leaf4-validate-bgp-configlet.png
       :align: center
       :width: 50 % 

   5.  There should now be a temporary action for leaf4 indicated by the green outline around leaf4. Click **Save**.

    .. image:: images/cvp-l3ls/leaf4-pending-task.png
       :align: center
       :width: 50 %  

   6.  A task should have been created.  Click **Tasks** on the left side to navigate to the **Tasks** page.

   7.  Check the assignable task for leaf4 and click **Create Change Control with 1 Task**.

    .. image:: images/cvp-l3ls/bgp-create-cc.png
       :align: center
       :width: 50 %

   8.  At this point, you should be on the Change Control page.  Click **Review and Approve** towards the upper right corner to view the effects of each task in the change control. 

    .. image:: images/cvp-l3ls/bgp-cc-page.png
       :align: center
       :width: 50 %

   9.  Review the changes you are about to push and click **Approve** in the bottom right corner of the window.

    .. image:: images/cvp-l3ls/bgp-review-and-approve.png
       :align: center
       :width: 50 %

   10. The **Review and Approve** button has now changed to an **Execute** button.  Click **Execute** to push the configuration update for leaf4.

    .. image:: images/cvp-l3ls/bgp-execute-cc.png
       :align: center
       :width: 50 %

5. Verify that BGP is properly configured
   
   1.  Head back over to **Metrics** and select the dashboard we created earlier.

    .. image:: images/cvp-l3ls/bgp-dashboard-done.png
       :align: center
       :width: 50 %

   2.  Make sure all of the switches have the proper BGP configuration and number of peers.

    .. image:: images/cvp-l3ls/leaf4-bgp-overview-post.png
       :align: center
       :width: 50 %

   3.  Navigate to the BGP Overview page for **leaf4** as well as both **spine1** and **spine2**. 
   
    .. image:: images/cvp-l3ls/spine1-bgp-overview-post.png
       :align: center
       :width: 50 %

6. Validate connectivity from **Host1** to **Host2**. From **Host1** execute:

        .. code-block:: text

            ping 172.16.116.100
            traceroute 172.16.116.100

**LAB COMPLETE!**
