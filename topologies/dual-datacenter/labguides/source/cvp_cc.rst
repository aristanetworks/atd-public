CVP Change Control, Telemetry & Rollback
==========================================

Learn how to use CloudVision’s Change Control. A Change Control (CC) can be associated with one or mores Tasks. CloudVision will take pre and post snapshots when a CC is executed to give us a state to revert back should there be any issues after the change.

Next, the lab will review Telemetry state-streaming information of the change of adding routes and how the routes propagate across the environment.

Lastly, the lab will initiate a Network Rollback to revert the changes that were implemented. The Network Rollback feature can greatly minimize downtime and gives the user the ability to restore the environment to a previous network state quickly.


.. note:: Did you know → the “cvp” script is composed of python code that uses the CloudVision Portal Rest API to automate the provisioning of CVP Configlets.

TASK 1: Apply a Configlet Builder to create a group of Tasks
************************************************************

* Log into the LabAccess jumpserver:
    .. warning:: If starting from this lab module, type ``cvp`` or ``7`` at the prompt. The script will configure all devices in the lab so you can complete this lab. The configlet builder will fail to generate device configlets if this script hasn't been run.


Now we want to add several Loopbacks to each device using a Configlet Builder at the ``s1/s1-Leaf`` level.


.. image:: images/cvp_cc/cvp_cc_1.gif
   :align: center

|

1. Navigate to the 'Network Provisioning' page under the 'Provisioning' tab.

2. Expand the ``S1`` container, right click on the ``S1-Leaf`` container and select 'Manage' -> 'Configlet'

3. Select the ‘Add_Loopbacks’ from the list of configlets.

4. Select 'Generate' to build a configlet for each device. View the generated configuration by expanding the Proposed Configuration on the right by selecting the '+' 

5. Select 'Update' to return to 'Network Provisioning' and select 'Save' at the bottom of the screen. Tasks will be generated and a notifcation will show next to the 'Tasks' option in the Navigation column. Now that we have Tasks created we can use Change Control feature.

|

.. image:: images/cvp_cc/cvp_cc_2.gif
   :align: center

|

6. Navigate to 'Change Control' from the Provisioning Tab.

7. Create a new Change Control by clicking the '+ Create Change Control' in the top right.

8. This screen will show pending tasks that will be associated with a Change Control(CC). Select all pending Tasks and click '+ Create Change Control with 4 Tasks'.

9. First, we need to give the Change Control a name. Click the pencil on the top right to edit the CC name. Name it 'Add_Loopbacks_CC' and hit Enter.

10. Next we will need to change the root stage to 'Serial' execution. 

11. Then we will create 3 new child stages. Click the '+' on the right side of the screen three times in order to create 3 new stages.

12. Rename the top and bottom stages to 'Before Snapshot' and 'After Snapshot' respectively by clicking the Pencil icon. Name the middle stage 'Configuration Changes'.

13. Next we can select a Snapshot template that we want to run before and after the change. Select the 'Before Snapshot' stage and click 'Add Actions' under the right side menu.

14. Under 'Select action', select 'Snapshot -> Validate_Routing'  and select 'S1-Leaf1', 'S1-Leaf2', 'S1-Leaf3', and 'S1-Leaf4' under 'Select devices to run on', then click 'Add to change control'.

15. Now click and drag each of the four leaf switch tasks to the 'Configuration Changes' task.
   
16. Repeat step 15, but select 'After Snapshot'. We should now have 2 stages that will take a before and after snapshot of the devices being changed.

.. note:: A few notes about Change Control:

    a. Each Task can be assigned to different stages if wanted. Health checks can be performed in stages before the next stage executes.
    b. The order of Task execution can be specified if there are dependencies. This is done by clicking the tasks and selecting the option in the drop-down menu.

|

17. For this lab, we now want to execute the CC. First a review and approval will need to take place. Select 'Review and Approve'.  Here we can view all of the changes for the tasks, snapshots to be taken, and any other information relative to the change control in order to approve it.

18. Once changes have been reviewed, we can click 'Approve' in the bottom right.

19. Once the change has been approved, we should now have a button that says 'Execute Change Control' in the top right corner. Click this to execute the changes.

20. We will now be prompted with with a confirmation. Click 'Execute' to confirm the CC execution.

21. While the CC executes, we can see the progress of each task as it is executed.

|

.. image:: images/cvp_cc/cvp_cc_3.gif
   :align: center

|

22. Once the Change Control is successfully completed, we can view and compare the snapshots under 'Devices' -> 'Comparison'

23. To compare the before and after from our CC, select the 'Two times' option to compare two points in time for the same device. Select 'S1-Leaf1' from the dropdown menu and click the Quick link for '30 minutes ago'.   Then hit 'Compare'.

24. CVP will bring up a variety of views that allows you to compare the state of the device from 30 minutes ago to the current time.  Select 'Snapshots' from the left Navigation column.

25. In the 'Comparing Data...' heading, select the first time to bring up a list of optional times to compare the Snapshot from.  The top option represents the 'Before Change' Snapshot taken when the Change Control was executed.  Select that to see a comparison of the command outputs from before and after the change.

|

TASK 2: View Telemetry
**********************


.. image:: images/cvp_cc/cvp_cc_4.gif
   :align: center

|

1. Using Telemetry, we can view the routes that were added as part of this change propagate across the environment. One way to view telemetry information is per device in the 'Devices' tab.  Navigate to the 'Devices' tab and select 'leaf1' to view detailed information.

2. On the left Navigation column, select 'IPv4 Routing Table' to see a live view of the device's routing table.  Using the timeline at the bottom of the screen, you can navigate to any point in time to see what the route table was at that exact moment.  You can also see a running list of changes to the routing table on the right.

3. By clicking on the 'compare against 30m ago' link, you can navigate back to the Comparison view of the routing table to see all the routes added in green as part of the Change Control pushed earlier.

4. To view Telemetry information for multiple devices in a common dashboard, select the 'Metrics' tab.

5. To build a dashboard, select 'Explorer' in the left column to bring up a list of available telemetry metrics to add.

6. Under the 'Metrics' dropdown, select 'IPv4 Total Route Count' and select 'S1-Leaf1', 'S1-Leaf2', 'S1-Leaf3' and 'S1-Leaf4' to add them to the dashboard view.

7. This will bring up a live rolling view of the selected metric.  In the timeline at the bottom, select 'Show Last: 1h' to view metric data for the last hour.  You will see a graphical representation of the increase in routes for each device.

8. Select the 'Add View' button to save this metric view and add another if desired.  Using the same process, add a view for 'IPv4 BGP Learned Routes' and 'IP Interfaces' to see other results of the Change Control.  Then hit the 'Save Dashboard' button in the bottom left.

9. Name the dashboard 'Leaf Routing Metrics' and hit 'Save'.  The dashboard is now saved and can be pulled up by other users of CVP at any time to view the consolidated metrics selected.

|

TASK 3: Rollback
****************


.. image:: images/cvp_cc/cvp_cc_5.gif
   :align: center

|

1. Initiate a Network Rollback to revert the changes that were implemented. Go to the 'Provisioning -> Change Control' page and find the change control we just executed: 'Add_Loopbacks_CC'.

2. In the top right, click 'Rollback Change'.

3. Here we will select the tasks we wish to roll back. Select all of the tasks for the leafs and click 'Create Rollback Change Control'.

4. We will now have a rollback change control created. The same change control process can be followed as before. Select 'Review and Approve' to see a reflection of the changes that will be executed.  Note that the config lines are now red as they will be removed when the Rollback Change is pushed. Select 'Approve' to move to the next step.

5. Hit 'Execute Change Control' to push the change to rollback the configuration of the devices to the previous state.

6. Navigate back to 'Metrics' then the 'Leaf Routing Metrics' dashboard.  Select 'Show Last: 5m" in the timeline to see your telemetry reflect in real-time the removal of the IPv4 routes and interfaces.

LAB COMPLETE

|