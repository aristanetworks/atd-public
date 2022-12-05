eAPI
====

This lab will walk you through using eAPI through Python. As mentioned
in the previous lab and the presentation, eAPI works through JSON
requests and responses. Fortunately, Python has a module that can handle
that easily!

If you haven’t used Python before, don’t worry! We will break down the
first script to explain how it works, and what it’s doing.

The scripts below leverage ``show`` commands, but you can easily modify them
to issue configuration commands as well - just use what you learned in
the previous lab to do that.

.. note:: While Arista switches have a fully functional Python
          installation, please make sure to use the lab VM for the scripting part of this lab.

Your very first script
----------------------

For the first script, we are going to issue ``show version`` to the switch,
and then print the output.

.. warning:: Please do not start writing this script until you get to the
             next section

The script is the same as in the presentation you just saw:

.. code-block:: python

    #!/usr/bin/env python3

    from jsonrpclib import Server
    import ssl

    ssl._create_default_https_context = ssl._create_unverified_context

    switch = Server ("https://arista:{REPLACE_PWD}@192.168.0.12/command-api")

    response = switch.runCmds( 1, ["show version"] )

    print(response)

Let’s break down the script into individual pieces:

**#!/usr/bin/env python3** - this is called a shebang (no, we didn’t make this
up!). A shebang instructs the operating system what to use to run the
script. In this case, python!

**from jsonrpclib import Server** - this imports the Python
submodule ``Server`` from the module ``jsonrpclib``. A Python module extends the
capability of Python by adding additional functionality. There are
Python modules for pretty much everything!

**import ssl**- this imports the Python ``ssl`` module.

**ssl._create_default_https_context = ssl._create_unverified_context** - This command is used to ignore
self-signed certificates within this lab.

**switch = Server ( "https://arista:{REPLACE_PWD}@192.168.0.12/command-api")**
this instantiates a variable - ``switch`` - and uses the ``Server`` submodule
imported previously to create a connection to the switch. Note that it
uses standard username/password formatting to make the connection.

**response = switch.runCmds( 1, ["show version"] )** - instantiates a
variable called ``response`` - that uses the previously
created ``switch.runCmds`` variable to run commands. This is where it starts
getting interesting. 

Once we create the ``switch`` connection, ``runCmds`` is the method provided by
theswitch’s JSON-RPC interface which allows us to run commands against
it. As a part of ``runCmds``, we also expect an API version (1) and the
command itself, in this case ``show version``.

If you rewind and go back to the Command API Explorer, you would see
that in the **Request Viewer** pane:

.. image:: images/eapi/eapi_1.png
   :align: center

Note the ``method``, ``cmds``, and ``version`` keys!

.. note:: The other values, such as format, timestamps, and id are
          defaults and do not need to be specified in your request.

**print(response)** - finally, we print the ``response`` variable to screen.

Write it
~~~~~~~~

Now that’s out of the way, it’s time to actually write the code! Connect to
the **Programmability IDE** service. This IDE is running VS Code. If prompted for a password, enter in your
lab password: ``{REPLACE_PWD}``

.. image:: images/eapi/nested_eapi_ide_1.png
   :align: center


To start writing our first script, click on ``New file`` to open a new file. Then start typing in the code from above.
Alternatively, if you’d just like to paste in the code, you can copy and paste it right into VS Code by pressing:

**Ctrl+v** on Windows
-- or --
**Cmd+v** on Macs.


Once done, save the file to your **project/labfiles** directory.

``/home/coder/project/labfiles/show_version.py``

Run it
~~~~~~

Now, let’s run it! Within the IDE, you can use any of the following to open a **Terminal** window:

**Ctrl+Shift+`**

Open it via the IDE Menus.

.. image:: images/eapi/nested_eapi_ide_2.png
   :align: center

A terminal window will open. Run your script by entering:

.. code-block:: bash

    python3 show_version.py

If this doesn’t work, make sure you replaced ``show_version.py`` with
the filename of the script you saved above!

.. note:: For the more Linux savvy folks, you might wonder why we’re
          calling Python directly instead of relying on the aforementioned
          shebang (``#!/usr/bin/env python3``) - if you want to make the file executable
          go for it!

.. image:: images/eapi/nested_eapi_ide_3.png
   :align: center

Woohoo - check out that JSON!


Advanced
--------

So that was cool and all, but if you want to take it one step further,
check out the following script - this time we’re taking the output and
doing something with it:

.. code-block:: python

    #!/usr/bin/env python3

    from jsonrpclib import Server
    import ssl

    ssl._create_default_https_context = ssl._create_unverified_context

    switch = Server ("https://arista:{REPLACE_PWD}@192.168.0.12/command-api")

    response = switch.runCmds( 1, ["show version"] )

    print("The switch model name is " + response[0]["modelName"] + " and it is running " + response[0]["version"])

There are plenty of other possibilities here. Think about your day to
day operations and things that you have to do frequently that take a lot
of time, but are tedious and error prone. Any Python script that can be
run against one switch can be run against many more. Adding a VLAN to
every switch in your datacenter might just involve providing a list of
switch hostnames or IP addresses, a VLAN ID, and a name and your script
will do it all for you!

Another script idea is tracing a MAC across your network until you find
the physical port it’s connected to. The possibilities are only limited
by your imagination.

Bonus
-----

Print the response of ``show version`` using `PrettyPrint <https://docs.python.org/3/library/pprint.html>`__\ .
