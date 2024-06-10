CloudVision Custom Events
==========================
Using the EOS Syslog function, and CVP Custom Events, 
CVP users can trigger custom events of any severity. Since EOS streams its state to CVP by way of the TerminAttr agent, this includes all of the system log messages.

A custom event based on a specific syslog entry can be created with little more than a regular expression (aka regex) to detect 
and match an occurring log message. Or this log could be triggered by an EOS Event-Handler as part of the action.
In this lab we will use the EOS CLI to send log messages that CVP will detect and create an Event accordingly.

|

Creating a Custom Event
**************

#. Start by selecting **Events** from the navigation menu. Then select **Event Generation**.

#. After selecting **Event Generation** choose and select **Custom Syslog Event** from the event types. 

#. Select **Add Rule**. 

#. Under   **Syslog Details** set the fields to the values listed:

#. In the **Log Message** field add the following Regular Expression:
    
   .. code-block:: text

      CR\d{6}

#. The **Event Title** field should be set to **Change Control Event Logged**.

#. The **Description** field should be set to **Change Control Event Logged. See CR number for details**.

#. The **Mute Period** field should be **10 sec**.

   .. thumbnail:: images/aa-cvp_custom_events/cvp_custom_event_1.png
      :align: center

   |

#. Select **Save Changes** to finish creating the Custom Syslog Event.

   .. thumbnail:: images/aa-cvp_custom_events/cvp_custom_event_2.gif
      :align: center

   .. tip:: 
      This Regular expression will match when the log
      message contains a string beginning with "CR" followed
      by exactly 6 numeric digits. In this example CR means **Change Record**.
      This will give the NOC the change record to review when an event is logged.

   |



Generating the Syslog Message 
**************


#. Log in to the CLI of leaf switch **s1-leaf1**.

#. Type the following EOS CLI command:

   .. code-block:: text

      s1-leaf1# send log level alerts message CR123456 starting now!

   .. thumbnail:: images/aa-cvp_custom_events/cvp_custom_event_3.gif
      :align: center
      :title: Generating a custom log event

   |

Reviewing the Events in Cloudvision
**************

#. Select **Events** from the navigation menu.

#. You should see an event similar to the one below:

   .. thumbnail:: images/aa-cvp_custom_events/cvp_custom_event_4.gif
      :align: center
      :title: Viewing our custom log event on the CVP Events page

   .. tip:: 
      * Experiment by sending messages with different severity levels, and modify the **CR123456** example using only 5 digits, or 7 digits. Does the event still trigger when using 5 or 7 digits?

      * Experiment with different regular expressions, perhaps try to build a match for other logs happening on **s1-leaf1** 

   |

**LAB COMPLETE**

|
   