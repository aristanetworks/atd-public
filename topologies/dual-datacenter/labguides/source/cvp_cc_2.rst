
CVP Telemetry and Introduction to Dashboards  (Advanced Change Control Lab Pt. 2)
=================================================

|

View Telemetry
**************
.. Note:: Please complete the Advanced Change Control Lab first in order to see the additional IPv4 routes shown below. `<--Click here to go back to part 1 of this lab <cvp_cc.html>`_

|

1. Using Telemetry, we can view the routes that were added as part of this change propagate across the environment. One way to view telemetry information is per device in the Devices tab.  Navigate to the **Devices** tab and select **s1-leaf1** to view detailed information.

2. On the left Navigation column, select **IPv4 Routing Table** to see a live view of the device's routing table.  Using the timeline at the bottom of the screen, you can navigate to any point in time to see what the route table was at that exact moment.  You can also see a running list of changes to the routing table on the right.

3. By clicking on the **compare against 30m ago** link, you can navigate back to the Comparison view of the routing table to see all the routes added in green as part of the Change Control pushed earlier.

|

.. thumbnail:: images/cvp_cc/cvp_cc_4.gif
   :align: center
   :title: Creating a Dashboard to display telemetry data for multiple devices

|

4. To view Telemetry information for multiple devices in a common dashboard, select the **Dashboard** tab.

5. To build a dashboard, select **+ New Dashboard** on the top right to bring up a list of available telemetry metrics to add. Drag the **Horizon Graph** to the middle pane, then click it to configure it.

6. Under the **Metric Data Type** dropdown, select **IPv4 Total Route Count**. In the **Local Devices Query** box type **device: S1-Leaf1, S1-Leaf2, S1-Leaf3, S1-Leaf4** to add them to the dashboard view.

.. thumbnail:: images/cvp_cc/cvp_cc_8.png
   :title: Using local devices query to select the devices that will appear on our dashboard

7. This will bring up a live rolling view of the selected metric.  In the timeline at the bottom, select 'Show Last: 1h' to view metric data for the last hour.  You will see a graphical representation of the increase in routes for each device. (you may need to click the time near your dashboard name to get the timeline to show up)

8. Using the same process, add a view for 'IPv4 BGP Learned Routes' and 'IP Interfaces' to see other results of the Change Control.  Then hit the **Save** button in the top right.

9. Name the dashboard **Leaf Routing Metrics** and hit **Save**.  The dashboard is now saved and can be pulled up by other users of CVP at any time to view the consolidated metrics selected.

|

Rollback
********


.. thumbnail:: images/cvp_cc/cvp_cc_5.gif
   :align: center
   :title: Rollback in progress for the Add_Loopbacks CC

|

1. Just as we did in the Configlet lab, we can initiate a Network Rollback to revert the changes that were implemented. Go to the 'Provisioning -> Change Control' page and find the change control we just executed: 'Add_Loopbacks_CC'.

2. In the top right, click 'Rollback Change'.

3. Here we will select the tasks we wish to roll back. Select all of the tasks for the leafs and click 'Create Rollback Change Control'.

4. We will now have a rollback change control created. The same change control process can be followed as before. Select 'Review and Approve' to see a reflection of the changes that will be executed.  Note that the config lines are now red as they will be removed when the Rollback Change is pushed. Select 'Approve' to move to the next step.

5. Hit 'Execute Change Control' to push the change to rollback the configuration of the devices to the previous state.

6. Navigate back to 'Metrics' then the 'Leaf Routing Metrics' dashboard.  Select 'Show Last: 5m" in the timeline to see your telemetry reflect in real-time the removal of the IPv4 routes and interfaces.

LAB COMPLETE
