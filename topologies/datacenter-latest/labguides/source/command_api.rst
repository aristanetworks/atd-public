Command API
===========

The first lab will demonstrate the on-switch Command API explorer
feature. The Command API provides an interface to experiment with
commands and view their request and response structure without having to
write a script or program to test it with.

Connect to **labvm** by clicking on labvm in the **Lab Frontend**.

.. image:: images/commandapi_1.png
   :align: center

Launch **Google Chrome** from DevBox (not your laptop) via the Guacamole interface. Chrome should automatically connect to the demo
switch’s Command API. If it doesn’t, log onto the switch via
HTTPS: `https://192.168.0.14 <https://192.168.0.14>`_

.. image:: images/commandapi_2.png
   :align: center

When prompted, enter in the username ``arista`` and ``{REPLACE_ARISTA}`` as the password.
Accept the self-signed SSL certificate, please do so.

You will be greeted with the following window:

.. image:: images/commandapi_3.png
   :align: center

Get familiar with the interface. Try entering in ``show interfaces`` and
clicking **Submit POST** request. Note that it requires the full command to
work properly; shorthand commands, such as ``sh int`` do not work. Any API
action is the same way.

.. note:: Technically, you can use the AutoComplete command to use shorthand, but it’s a good practice to use long form. When writing
          code it’s always important to think about the next person to look at it!                                                                  

When you successfully issue a command, notice what the response looks
like:

.. image:: images/commandapi_4.png
   :align: center

The format above is in JSON (JavaScript Object Notation). Every line has
a *key*, and a *value*. This is why JSON is nice to use; it’s easy to
reference and use key/value pairs. We will play with this more in the
next lab.

Now try to issue a configuration command. Try:

.. code-block:: html

   vlan 1000
   name test

Hit **Submit POST Request**.

What does the response viewer say? Note there’s an error, in this
case ``"message": "CLI command 1 of 2 'vlan 1000' failed: invalid command"`` 

If you were to log into the switch right now and issue that command without using an API, what would cause this?

Now try it with the following:

.. code-block:: html

   enable
   configure
   vlan 1000
   name test

Just like if you were to login to a switch and issue those commands
normally, the same applies here. The response indicates a success now.
Log into your switch and observe that the VLAN is present:

.. image:: images/commandapi_5.png
   :align: center

.. note:: To switch between your desktop and the switch, press **Control+Alt+Shift**, click **arista** at the top right of the menu, click **Home** and 
          then expand **veos** and double click on **leaf1**. To switch back, reverse the process.

Play around some more if you’d like! Check out the **Overview** and **Command Documentation**
tabs. Also, this is running on a virtual edition of our switch, so you can also do this at home or in your work lab!
