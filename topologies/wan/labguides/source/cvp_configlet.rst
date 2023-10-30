CVP Configlet
=============

Let’s create a new CloudVision configlet. CloudVision configlets are
snippets of configuration that are used to create a switch
configuration.

All of the switches have a base Configlet. Additional Configlets have
been defined for AAA and VLANs.

1. Log into the Arista Test Drive portal with your assigned URL. If you
   don’t have one, please see your ATD staff.

.. thumbnail:: images/cvp_configlet/nested_cvp_overview_1.png
   :align: center

         Click image to enlarge

|

2. Click on the link "Click Here To Access Topology" and navigate to the below page. Click the CVP link on the left side of the screen.

|

.. thumbnail:: images/cvp_configlet/nested_cvp_landing_1.png
   :align: center

          Click image to enlarge

|

1. You will come to a login screen for CloudVision Portal. Enter the username ``arista`` and the password ``{REPLACE_PWD}``

|

.. thumbnail:: images/cvp_configlet/cvp_configlet_1.gif
   :align: center

            Click image to enlarge


|

1. For this lab, select 'Provisioning -> Configlets' from CloudVision.

2. Click the '+' in the top right and select 'Configlets' to create a new configlet.

3. In the configuration section enter the command information as shown:


    .. code-block:: text

       alias snz show interface counter | nz


4. Name the Configlet 'Alias'.

5. The Configlet can be validated against a device to ensure there isn’t a conflict and the configuration is validated. To validate, click the checkbox in the top right section.

6. Once the configuration is validated, Click the 'Save' button to save the Configlet

|

.. thumbnail:: images/cvp_configlet/cvp_configlet_2.gif
   :align: center

          Click image to enlarge

|

1.  To apply the Configlet, navigate to 'Network Provisioning' and right click on the 'Tenant' container and select 'Manage -> Configlet'.

2.  Select the 'Alias' Configlet and click 'Update'. This activity is to simply add a new configlet to the existing configlets applied on the 'Tenant' container. **Do not Remove** existing configlets from the Proposed Configuration section.


    *\**Expert Tip - Use search bar to find Configlets faster*


3.  On the 'Network Provisioning' page, Click the 'Save' button to save the changes to the topology.

4.  The screen will refresh and a 'T' for task will appear at the right column of each device, representing that tasks have been generated that need to run to push the configuration change.

|

.. thumbnail:: images/cvp_configlet/cvp_configlet_3.gif
   :align: center

          Click image to enlarge

|

1.  Click 'Tasks' in the left navigation column.

2.  Check each Task in the 'Assignable Tasks' section, then click the 'Create Change Control with 9 Tasks' button.

    *\**See the 'CVP Change Control, Telemetry & Rollback' lab guide for more information on Change Controls*


3.  Select 'Review and Approve' in the top right, then 'Approve' in the bottom right to approve the Change Control.

4.  Select 'Execute Change Control' in the top right and then 'Execute' to execute the Change Control tasks.

5.  When the tasks are completed, navigate into the task by clicking on the task object.

6.  Select 'Show Details' icon on the righ side of the screen to review the *Designed Configuration* vs. *Running Configuration*. The Designed Configuration is a combination of all configlets to build a full device configuration. The Running Configuration is the running-config prior to executing the task. Configuration differences are highlighted to show New Lines, Mismatch Lines, and To Reconcile.

|

.. note:: We can see the unchanged configuration by clicking on the down arrows next to the designed configuration.

|
   
   **LAB COMPLETE**
