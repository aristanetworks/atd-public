VxLAN
=====

.. image:: images/vxlan_1.png
   :align: center

.. note:: Did you know the ``vxlan`` script is composed of Python code that
          uses the CloudVision Portal REST API to automate the provisioning of
          CVP configlets. The configlets that are configured via the REST API
          are ``Spine1-BGP-Lab``, ``Spine2-BGP-Lab``, ``Leaf1-VXLAN-Lab``,
          ``Leaf2-VXLAN-Lab``, ``Leaf3-VXLAN-Lab``, ``Leaf4-VXLAN-Lan``. In
          addition each leaf also gets the ``VLANs`` configlet.

.. note:: The manually-entered commands below that are part of this lab are
          equivalent to ``Leaf3-VXLAN-Lab-Full``.


1. Log into CloudVision and find Leaf3 on the **Devices** page.
* The username to access CloudVision is ``arista`` and the password is ``{REPLACE_ARISTA}``
   
   * Search for ``leaf3`` in the **Device** column of the inventory table.

        .. image:: images/cvp-vxlan/leaf3-inventory-table.png
           :align: center
           :width: 50 %

   * Click on **leaf3**.

2. Review the current vxlan information in CVP
* Click on VXLAN in the left selection columnn under ``Switching``

    * ``Note:`` ``leaf3`` currently has no VXLAN configuration

       .. image:: images/cvp-vxlan/leaf3-vxlan-pre.png
          :align: center
          :width: 50%

3. Create the VXLAN configlet
* Click on Provisioining, click on configlets in the left selection column

* Click the + sign in the Configlets list toolbar

* create a configlet called Leaf3-VXLAN-Lab-Full-user
    .. code-block:: text

        !! Configure physical interface et4 and port-channel 4 for host2 in access vlan4
        interface port-channel 4
            description MLAG - HOST2
            switchport access vlan 12
            mlag 4
        !
        interface Ethernet4
            description HOST2
            channel-group 4 mode active
            lacp timer fast

        !! Configure a loopback interface to be used with interface vxlan1 for vxlan encapsulation
        interface Loopback1
          ip address 172.16.0.56/32
        !
        interface vxlan 1
          vxlan source-interface loopback 1
          !! Map vlan 12 to vni 1212
          vxlan vlan 12 vni 1212
          !! Send BUM traffic to vtep(s)
          vxlan flood vtep 172.16.0.34

* add the CLI text from above to the new configlet

    .. image:: images/cvp-vxlan/leaf3-vxlan-configlet.png
        :align: center
        :width: 50%

* Validate configlet syntax on ``leaf3``

    .. image:: images/cvp-vxlan/leaf3-vxlan-configlet-validate.png
        :align: center
        :width: 50% 

4. Assign VXLAN configlet to ``leaf3``
* Click on Provisioning, click on Network Provisioning in left selection column

* Right click on Leaf3, click on manage configlets, search for Leaf3-VXLAN 

       .. image:: images/cvp-vxlan/leaf3-vxlan-configlet-manage.png
           :align: center
           :width: 50% 

* click the checkbox next to Leaf3-VXLAN-Lab-Full-user

    .. image:: images/cvp-vxlan/leaf3-vxlan-configlet-assign.png
        :align: center
        :width: 50% 

* click validate, review the new lines

    .. image:: images/cvp-vxlan/leaf3-vxlan-configlet-assign-validate.png
        :align: center
        :width: 35% 

* click save

    .. image:: images/cvp-vxlan/leaf3-vxlan-configlet-assign-validate-compare.png
        :align: center
        :width: 50% 

* Click save on the Network Provisioning main view
    ``Note:`` a ``Task`` will be generated

    .. image:: images/cvp-vxlan/leaf3-vxlan-configlet-main-save.png
        :align: center
        :width: 50% 

5. Create a ``Change Control`` with the generated Task
* click ``Tasks`` from the left selection column

    * click the checkbox next to the generated task

        .. image:: images/cvp-vxlan/leaf3-vxlan-cc-task.png
            :align: center
            :width: 50% 

    * click * Create Change Control with 1 Task

        .. image:: images/cvp-vxlan/leaf3-vxlan-cc-create-cc.png
            :align: center
            :width: 50% 

    * click ``Review and Approve`` on the Change Control that was created

        .. image:: images/cvp-vxlan/leaf3-vxlan-cc-review-approve.png
            :align: center
            :width: 50% 

    * click ``Execute Change Control`` in upper right of the UI

        .. image:: images/cvp-vxlan/leaf3-vxlan-cc-execute.png
            :align: center
            :width: 50% 

    * click ``Execute`` in the resulting confirmation dialog box

        .. image:: images/cvp-vxlan/leaf3-vxlan-cc-execute-confirm.png
            :align: center
            :width: 50% 


6. Verify VLXAN operation with CVP Telemetry
* from ``Device Inventory``, click on ``leaf3``

* click on VXLAN in the left selection column under Switchign
    ``Note:`` you will now see the VLANs, VNI mappings related to VXLAN

        .. image:: images/cvp-vxlan/leaf3-vxlan-verification.png
            :align: center
            :width: 50% 

* ping ``host1`` from ``host2``
    
    .. code-block:: text

        host1#ping 172.16.112.201
        PING 172.16.112.201 (172.16.112.201) 72(100) bytes of data.
        80 bytes from 172.16.112.201: icmp_seq=1 ttl=64 time=0.248 ms
        80 bytes from 172.16.112.201: icmp_seq=2 ttl=64 time=0.165 ms
        80 bytes from 172.16.112.201: icmp_seq=3 ttl=64 time=0.181 ms
        80 bytes from 172.16.112.201: icmp_seq=4 ttl=64 time=0.150 ms
        80 bytes from 172.16.112.201: icmp_seq=5 ttl=64 time=0.146 ms

        --- 172.16.112.201 ping statistics ---
        5 packets transmitted, 5 received, 0% packet loss, time 1ms
        rtt min/avg/max/mdev = 0.146/0.178/0.248/0.037 ms, ipg/ewma 0.421/0.211 ms
        host1#

* again, click on VXLAN in the left selection column under Switchign
  ``Note:`` In addition to VLAN, VNI Mappings, you will see an entry in the ``VXLAN MAC Address Table`` section

        .. image:: images/cvp-vxlan/leaf3-vxlan-verification-mac.png
            :align: center
            :width: 50% 

* click on the MAC Address Table for Leaf3 in left selection column
  ``Note:`` You will see the local MAC Address of Host2 on port-channel 4 and the remote MAC Address of Host1 showing port vx1

        .. image:: images/cvp-vxlan/leaf3-vxlan-verification-mac-table.png
            :align: center
            :width: 50% 

**LAB COMPLETE!**
