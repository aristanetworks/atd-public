.. # define a hard line break for HTML
.. |br| raw:: html

   <br />

Event API Lab
=============

In this lab we will be creating custom log events on one of our virtual switches, then using the Event API link on our lab landing screen to view them. This demonstrates how simple it is to create a new Event rule in CVP to forward alerts to a webhook or other receiver.

|

1. Start by logging into CVP (if you aren't already) and clicking on **Events** on the top navigation bar


2. Now click on **Notifications** on the upper right, to customize Event Notification settings. 

.. thumbnail:: images/ag-event_api/ag-event_api1.png

|

3. Click on **Receivers** on the left
4. Now click on **+ Add Receiver** and name it **My Receiver**
5. Click on **+ Add Configuration**, then choose **Webhook (HTTP)**

.. thumbnail:: images/ag-event_api/ag-event_api2.png

|

6. in the **Target URL** field, paste the following:

.. code-block:: text

   http://192.168.0.1:5000/alert

7. Leave the other options unchecked and click **Save** on the bottom left side of the screen

|
Now that we have a receiver to send our events to, we have to configure a rule to tell CVP what to send to this receiver.

1.  To do this, click on **Rules** on the left side of the screen.
2.  Leave the Add Conditions section at the default values. By default, all devices, interface tags, and event types will be selected.
3.  In the Receiver section, click the drop down and select **My Receiver**

.. thumbnail:: images/ag-event_api/ag-event_api3.png

|

11. click **Save** on the bottom left once more.
12. That's it! Now we can create a test alert to make sure it works. To do this, click on **Status** on the left.
13. In the **Test Notification Sender** section, select any severity, and event type, and any device, then click **Send Test Notification**

.. thumbnail:: images/ag-event_api/ag-event_api4.png

|

14. Now go back to your lab landing page and click on **Event Alert API**

|

.. thumbnail:: images/ag-event_api/ag-event_api5.png

|

15. You may need to refresh the page a few times but you should see your test alert come through momentarily.

.. thumbnail:: images/ag-event_api/ag-event_api6.png



