Connecting to your lab machine
==============================

1. Before we begin, let's reset the environment to clear out previous lab changes.
If the environment was brought up fresh and you are starting from this point, you can skip step #1.

SSH to the public address assigned to the LabAccess jumphost server (this is the Topology Address shown in the "Welcome to Arista's Test Drive!" picture above). The username is ``arista`` and the password is ``{REPLACE_PWD}``:

    .. code-block:: text

       ssh arista@{unique_address}.topo.testdrive.arista.com

|
You will be greeted with the following menu:


.. image:: images/program_connecting/nested_connecting_2.png
   :align: center

|

Select option **1** (**Reset All Devices to Base ATD**), wait til the command has completed, then log out.

|

2. Now we need to make sure that you can access your handy lab machine! You should have received your login 
information (a URL) from your friendly Arista SE already. If you have not, please reach out and ask for one.

Once you receive your token, click on the link. You will greeted with a
screen that looks like this:

.. image:: images/program_connecting/nested_connecting_landing_1.png
   :align: center
|
For these labs, we will be leveraging the **Console Access**, **Programmability IDE** and **WebUI** services. Connect to each of the service by clicking on the corresponding links on the left side.
Each service will open in a new tab in your browser.

.. image:: images/program_connecting/nested_connecting_overview_1.png
   :align: center
|
To access each of the services, the credentials are listed on the **Arista Test Drive Lab** overview page in the **Usernames and Passwords** section.

These services will be used to provide a ssh access to the lab, coding IDE, and a WebUI for the upcoming programmability labs.
