MLAG
====

.. note:: For more details on the configuration we will apply to Leaf4, check out the UCN MLAG Lab.

**To access the command line of particular switch, click on that switch in the topology diagram at the top of the lab guide.**


1. Log into CloudVision and find Leaf3 on the **Devices** page.

   1. The username to access CloudVision is ``arista`` and the password is ``{REPLACE_ARISTA}``

   2. Search for ``Leaf3`` in the **Device** column of the inventory table.

    .. image:: images/cvp-mlag/mlag-leaf3-inventory-table.png
       :align: center
       :width: 50 %

   3. Click on ``Leaf3``.

2. View the MLAG status for Leaf3.

   1. Click on the **MLAG** section on the left side navigation bar.

   2. Here we can see details for the fundamental components of our MLAG configuration for **Leaf3** along with each MLAG component's status.

    .. image:: images/cvp-mlag/leaf3-mlag-overview-pre.png
       :align: center
       :width: 50 %

   3. Notice that our MLAG status is inactive.  This is because we don't have an MLAG configuration in place on Leaf4, Leaf3's peer.

3. To fix this we'll configure MLAG on Leaf4.

   1. Head over to the Network Provisioning section of CloudVision by clicking **Provisioning** at the top of the page.

   2. Find **Leaf4** and right click on its icon.  Select ``Manage`` -> ``Configlet``.

    .. image:: images/cvp-mlag/leaf4-manage-configlet.png
       :align: center
       :width: 50 %

   3. Search for the Configlet Builder ``Leaf4-MLAG-Lab`` in the search bar, select the configlet, and click **Validate**.

    .. image:: images/cvp-mlag/mlag-leaf4-add-configlet.png
       :align: center
       :width: 50 %

   4. On the **Validate and Compare** page, CloudVision uses all of the configlets applied to the device to create a Designed Configuration.  It then compares this Designed Configuration to the Running Configuration on the device.  If everything looks good, click **Save**.

    .. image:: images/cvp-mlag/mlag-leaf4-validate-and-compare.png
       :align: center
       :width: 50 %

   5. We now have a pending action.  You can optionally view this pending action by clicking **Preview**. Click **Save** once more to create a task.

    .. image:: images/cvp-mlag/mlag-leaf4-pending-task.png
       :align: center
       :width: 50 %

   6. Head over to the **Tasks** section in **Provisioning** by clicking **Tasks** on the left side bar.

   7. Select our recently created task for Leaf4 and click 'Create Change Coontrool'.

    .. image:: images/cvp-mlag/leaf4-mlag-create-cc.png
       :align: center
       :width: 50 %

   8. Here we can review, approve, and execute the configuration update change control.  Click **Review** toward the right side to confirm the changes we are about to push.

    .. image:: images/cvp-mlag/leaf4-mlag-cc.png
       :align: center   
       :width: 50 %

   9. If the changes look good, click **Approve**.

    .. image:: images/cvp-mlag/leaf4-mlag-cc-review.png
       :align: center
       :width: 50 %

   10. The **Review** button has now changed to an **Execute** button.  Click **Execute** to execute the change control.

    .. image:: images/cvp-mlag/leaf4-mlag-cc-execute.png
       :align: center
       :width: 50 %

4. Once our change control has successfully completed, navigate back to our Device overview page to check out **Leaf3**'s MLAG status.

    1. If you aren't there already, on the Devices page, select **Leaf3** -> **Switching** -> **MLAG**

    .. image:: images/cvp-mlag/leaf3-mlag-overview-post.png
       :align: center
       :width: 50 %

    2. Everything should look okay now.

    3. Jump over to **Leaf4**'s MLAG section, we see the everything looks okay too.

5. Log in to Host1 and ping Host2
        .. code-block:: text

              ping 172.16.112.202

6. Click **Devices** at the top of the page to navigate back to the main **Devices** page.
    1. Click **Comparison** on the left side bar.
    2. At the center of the page, select **Leaf3** for one of our devices and **Leaf4** for the other.
    3. Here we can compare different metrics for these two devices side by side to see similarities and differences between the two members of this MLAG pair.


**LAB COMPLETE!**
