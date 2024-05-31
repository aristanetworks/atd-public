CVP Advanced Change Control
==========================================

Learn how to use CloudVision’s Change Control. A Change Control (CC) can be associated with one or mores Tasks. CloudVision will take pre and post snapshots when a CC is executed to give us a state to revert back should there be any issues after the change.

Next, the lab will review Telemetry state-streaming information of the change of adding routes and how the routes propagate across the environment.

Lastly, the lab will initiate a Network Rollback to revert the changes that were implemented. The Network Rollback feature can greatly minimize downtime and gives the user the ability to restore the environment to a previous network state quickly.


.. note:: Did you know → the “cvp” script is composed of python code that uses the CloudVision Portal Rest API to automate the provisioning of CVP Configlets.

TASK 1: Apply a Configlet Builder to create a group of Tasks
************************************************************
.. note:: The Configlet Builder feature enables you to programatically create device configurations (Configlets) for devices that have relatively dynamic configuration requirements. This helps to prevent you from having to manually code Configlets. 

|

* Log into the LabAccess jumpserver:
    .. warning:: If starting from this lab module, type ``cvp`` or ``5`` at the prompt. The script will configure all devices in the lab so you can complete this lab. The configlet builder will fail to generate device configlets if this script hasn't been run.


Now we want to add several Loopbacks to each device using a Configlet Builder at the ``s1/s1-Leaf`` level.

1. Navigate to the **Network Provisioning** page under the **Provisioning** tab.

2. Expand the ``S1`` container, right click on the ``S1-Leaf`` container and select **Manage** -> **Configlet**

3. Select the **Add_Loopbacks** configlet from the list of configlets.

4. Select **Generate** to build a configlet for each device. View the generated configuration by expanding the Proposed Configuration on the right by selecting the **+** 

5. Select **Update** to return to 'Network Provisioning' and select **Save** at the bottom of the screen. Tasks will be generated and a notifcation will show next to the 'Tasks' option in the Navigation column. Now that we have Tasks created we can use Change Control feature.

|

.. thumbnail:: images/cvp_cc/cvp_cc_1.gif
   :align: center
   :title: assigning the Add_Loopbacks configlet to the S1-Leaf container
   
|

6. Navigate to **Change Control** from the Provisioning Tab.

7. Create a new Change Control by clicking the **+ Create Change Control** button in the top right.

8. This screen will show pending tasks that will be associated with a Change Control(CC). Select all pending Tasks and click **+ Create Change Control with 4 Tasks**.

9. First, we need to give the Change Control a name. Click the pencil on the top right to edit the CC name. Name it **Add_Loopbacks_CC** and hit Enter.

10. Next we will need to change the root stage to Serial execution. To do this, click on the Root stage, then on the right side, change the drop down to **Series**. You can also change between Parallel and Series within the Change Control screen as well. 

|

.. thumbnail:: images/cvp_cc/cvp_cc_2.gif
   :title: changing our change control root stage to series so they'll run in order

|

11.  Then we will create 3 new child stages. Click the **...** on the right side of the root stage to create 3 stage containers.

12. Rename the top and bottom stages to **Before Snapshot** and **After Snapshot** respectively by clicking the Pencil icon. Name the middle stage **Configuration Changes**.

13. Next we can select a Snapshot template that we want to run before and after the change. Select the **Before Snapshot** stage and click **Add Actions** under the right side menu.

14. Under **Select action**, select **Snapshot** -> **Validate_Routing**  and select 'S1-Leaf1', 'S1-Leaf2', 'S1-Leaf3', and 'S1-Leaf4' under 'Select devices to run on', then click **Add to change control**.

15. Now click and drag each of the four leaf switch tasks to the 'Configuration Changes' task.
   
16. Repeat step 15, but select 'After Snapshot'.

|

.. thumbnail:: images/cvp_cc/cvp_cc_3.gif
   :title: This is how our change control looks just before we review, approve and execute it.

|

17.  We should now have 2 stages that will take a before and after snapshot of the devices being changed and your Change Conrol screen should look like this:

|

.. thumbnail:: images/cvp_cc/cvp_cc_4.png
   :title: This is how our change control looks just before we review, approve and execute it.

|


.. note:: A few notes about Change Control:

    a. Each Task can be assigned to different stages if wanted. Health checks can be performed in stages before the next stage executes.
    b. The order of Task execution can be specified if there are dependencies. This is done by clicking the tasks and selecting the option in the drop-down menu.
    c. The root stage and child stages can each be set to series or parallel. We set the root stage to series earlier in the lab so that it will run the stages in order. The child stages can be set to run in parallel to speed up task executio

|

18.  We now want to execute the CC. First a review and approval will need to take place. Select **Review and Approve**.  Here we can view all of the changes for the tasks, snapshots to be taken, and any other information relative to the change control in order to approve it.

19.  Once changes have been reviewed, we can click **Approve** in the bottom right.

20.  Once the change has been approved, we should now have a button that says **Execute Change Control** in the top right corner. Click this to execute the changes.

21.  We will now be prompted with with a confirmation. Click **Execute** to confirm the CC execution.

22.  While the CC executes, we can see the progress of each task as it is executed.

|

.. thumbnail:: images/cvp_cc/cvp_cc_5.gif
   :align: center
   :title: Comparing our ipv4 routes before and after our change control, then showing our snapshot that was created during our change control

|

23. Once the Change Control is successfully completed, we can view and compare the snapshots under **Devices** -> **Comparison**

24. To compare the before and after from our CC, select the **Time Comparison** option to compare two points in time for the same device. Select **S1-Leaf1** from the dropdown menu and click the Quick link for **30 minutes ago**.   Then hit **Compare**.

25. CVP will bring up a variety of views that allows you to compare the state of the device from 30 minutes ago to the current time.  Select **Snapshots** from the left Navigation column.

26. In the 'Compared with...' heading, select the first time to bring up a list of optional times to compare the Snapshot from.  The earlier option represents the 'Before Change' Snapshot taken when the Change Control was executed.  Select that to see a comparison of the command outputs from before and after the change.

|

.. thumbnail:: images/cvp_cc/cvp_cc_6.gif
   :align: center
   :title: Comparing our ipv4 routes before and after our change control, then showing our snapshot that was created during our change control

|

**In the next part of this lab, we'll view and compare Telemetry data based on the changes we made, and then create a sample Dashboard showing the number of IPv4 routes**

|

`Click here to continue to part 2 of this lab ---> <cvp_cc_2.html>`_
**************************************************************************

|

|

