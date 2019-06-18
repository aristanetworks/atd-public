CVP Configlet
=============

Let’s create a new CloudVision configlet. CloudVision configlets are
snippets of configuration that are used to create a switch
configuration.

All of the switches have a base Configlet Builder that was generated
from the IP Address Management (IPAM) system. Additional Configlets have
been defined for AAA and VLANs.

1. Log into the Arista Demo Cloud portal with your assigned URL. If you don’t have one, please see your ATD staff.


.. image:: images/cvp_configlet1.png


2. Click on the link "Click Here To Access Topology" and navigate to the below page. Click the CVP link on the left side of the screen and accept any SSL warning signs that may pop up.


.. image:: images/cvp_configlet2.png


3. You will come to a login screen for CloudVision Portal. Enter the username “arista” and the password “arista”


4. For this lab, create a new configlet by selecting **Configlets** from the CloudVision entry portal, and clicking the  **+** in the top right and select Configlet.


.. image:: images/cvp_configlet3.png
   :align: center

  
5. In the configuration section enter the command information as shown:


    .. code-block:: text

       alias routeage bash echo show ip route | cliribd
            

6. Name the Configlet **Alias**


.. image:: images/cvp_configlet4.png
   :align: center    

7. The Configlet can be validated against a device to ensure there isn’t a conflict and the configuration is validated. To validate, click the checkbox in the top right section.


.. image:: images/cvp_configlet5.png
   :align: center

.. image:: images/cvp_configlet6.png
   :align: center   

8. Once the configuration is validated, Click the **Save** button to save the Configlet

9. To apply the Configlet, navigate to **Network Provisioning** and right click on the **Tenant** container and select **Manage** -> **Configlet**

.. image:: images/cvp_configlet7.png
   :align: center   

10. Select the **Alias** Configlet and click **Update**. This activity is to simply add a new configlet to the existing configlets applied on the **Tenant** container. **Do not Remove** existing configlets from the Proposed Configuration section.


    *\**Expert Tip - Use search bar to find Configlets faster*

.. image:: images/cvp_configlet8.png
   :align: center    

11. On the **Network Provisioning** page, Click the **Save** button to save the changes to the topology.

12. The screen will refresh and a **T** for task will appear above each switches; generating tasks that need to run to push the configuration change.

.. image:: images/cvp_configlet9.png
   :align: center    

13. Click the **Task** notification on the top right.

14. Check each **Pending** task and click the **Execute** button.

.. image:: images/cvp_configlet10.png
   :align: center

15. When the tasks are in-progress or completed, navigate into the task by clicking on the **Task ID**. The Log tab includes information for all interactions between CVP and the switch. 

.. image:: images/cvp_configlet11.png
   :align: center

16. Select View Config tab to review the *Designed Configuration* vs. *Running Configuration*. The Designed Configuration is a combination of all configlets to build a full device configuration. The Running Configuration is the running-config prior to executing the task. Configuration differences are highlighted to show New Lines, Mismatch Lines, and To Reconcile.

.. image:: images/cvp_configlet12.png
   :align: center

**LAB COMPLETE**
