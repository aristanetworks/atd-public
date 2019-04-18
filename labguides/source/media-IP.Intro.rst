Media Intro to IP Lab
=====================

.. image:: images/media-IP.Intro.png
   :align: center

.. note:: An IP address serves two principal functions. It identifies the host, or more specifically its network interface, and it provides the location of the host in the network, and thus the capability of establishing a path to that host. Its role has been characterized as follows: "A name indicates what we seek. An address indicates where it is. A route indicates how to get there."

**1.** Log into the **LabAccess** jumpserver:

   1. Type ``media - IP Intro`` at the prompt. The script will configure the topology with the exception of **Leaf4**. The main task is to configure the remaining device so there is connectivity between the two hosts



**2.** Configure the proper ip address on the interfaces along with the appropriate static routes to ensure there is end-to-end connectivity for the two end hosts to reach each other.  All interfaces in this lab are designed as point-to-point  connections

   1. on **leaf4** assign the appropriate ip address and ensure the adjacent devices can be reached

        .. code-block:: text

            configure
            !
            interface Ethernet3
                no switchport
                ip address 10.127.34.4/24
            !
            interface Ethernet 4
                no switchport
                ip address 172.16.46.4/24
            !

      it is worth mentioning by default all interfaces on an Arista switch is set to be a switchport (layer 2), we need to allow it to be a routed interface and thus ``no switchport`` is added.  Once the IP address has been added to the appropriate interface, ensure reachability to the adjacent device by leveraging ``ping`` on **leaf 4**

        .. code-block:: text

            !
             ping 10.127.34.3
            !
             ping 172.16.46.6
            !

      At this point if the adjacent devices can be reached, you have configured the IP address correctly


   2. once the address has been assigned to the appropriate interfaces, we can enable the routing as well as add the appropriate static routes on **leaf4** to allow reachability between the two host end-points.


        .. code-block:: text

            configure
            !
            ip routing
            !
            ip route 172.16.15.0/24 10.127.34.3
            !


      .. note::
         we added the entire prefix for the static route but we could of also put the specific host address.  Normally your internal security policies will dictate which approach to take




**3.** Validate end-to-end connectivity once IP adresses and static routes are in place

   1. log into **host2** and verify there is reachability to **host1**

        .. code-block:: text

            ping 172.16.15.5

      If all the IP address and routing settings have been completed correctly, then you should have reachability

**LAB COMPLETE!**