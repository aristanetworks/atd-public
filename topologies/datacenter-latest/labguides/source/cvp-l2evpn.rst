.. # define a hard line break for HTML
.. |br| raw:: html

   <br />

L2 EVPN
=======

1. Log into CloudVision and find **leaf3** on the **Devices** page

* The username to access CloudVision is ``arista`` and the password is ``{REPLACE_ARISTA}``
   
* Search for ``leaf3`` in the **Device** column of the **inventory** table.

.. image:: images/cvp-l2vpn/leaf3-inventory-table.png
    :align: center
    :width: 50 %
|br|

* Click on **leaf3**
|br|

2. Review the current **running-config** routing agent information in CVP

* Click on **Running Config** in the left selection column under **Device Overview**

.. image:: images/cvp-l2vpn/leaf3-l2vpn-running-config.png
    :align: center
    :width: 50%
|br|

* Verify that ``service routing protocols model multi-agent`` line is in the current **running-config**
|br|

3. Review the current VXLAN information in CVP

* Click on **VXLAN** in the left selection column under **Switching**

.. image:: images/cvp-l2vpn/leaf3-l2vpn-vxlan-pre.png
    :align: center
    :width: 50%
|br|

* **Note:** leaf3 currently has no VXLAN configuration

* Click on **Topology** in the navigation bar at the top of the page 
* Click the **Link Overlay** dropdown in the left selection column

.. image:: images/cvp-l2vpn/leaf3-l2vpn-vxlan-before.png
    :align: center
    :width: 50%
|br|

* Click the **VXLANs** selection, also click and view the **VLANs** selection
* **Note:** You should see VLAN 1 on ``leaf3`` & ``leaf1``
* **Note:** You should not see VLAN 12 or VNI 1200 as a dashed line from ``leaf3`` to other leaf switches
|br|

4. Create the EVPN L2VPN configlet

* Click on **Provisioning**, click on **Configlets** in the left selection column
* Click the **+** sign in the Configlets list toolbar

.. image:: images/cvp-l2vpn/leaf3-l2vpn-configlet-list.png
    :align: center
    :width: 50%
|br|

* Create a configlet called ``Leaf3-l2vpn-Lab-Full-user``

.. code-block:: text

    !! Configure physical interface et4 for LACP and Port-Channel4 in access vlan 12
    interface Port-Channel4
      switchport mode access
      switchport access vlan 12
    !
    interface Ethernet1
      shutdown
    !
    !! Configure interface et2 as a p2p leaf to spine L3 link
    interface Ethernet2
      no switchport
      ip address 172.16.200.10/30
    !
    !! Configure interface et3 as a p2p leaf to spine L3 link
    interface Ethernet3
      no switchport
      ip address 172.16.200.26/30
    !
    !! Configure physical interface et4 for LACP (active) in Port-Channel4
    interface Ethernet4
      channel-group 4 mode active
      lacp timer fast
    !
    interface Ethernet5
      shutdown
    !
    !! Configure loopback0 interface for use with routing protocol (BGP)
    interface Loopback0
      ip address 172.16.0.5/32
    !
    !! Configure loopback1 interface for use as the VTEP IP interface
    interface Loopback1
      ip address 3.3.3.3/32
      ip address 99.99.99.99/32 secondary
    !

    !! Configure routing protocol BGP Underlay
    router bgp 65103
      router-id 172.16.0.5
      maximum-paths 2 ecmp 2
      neighbor SPINE peer group
      neighbor SPINE bfd
      neighbor SPINE remote-as 65001
      neighbor SPINE maximum-routes 12000
      neighbor 172.16.200.9 peer group SPINE
      neighbor 172.16.200.25 peer group SPINE
    !! Configure routing protocol BGP overlay
      neighbor SPINE-EVPN-TRANSIT peer group
      neighbor SPINE-EVPN-TRANSIT next-hop-unchanged
      neighbor SPINE-EVPN-TRANSIT update-source Loopback0
      neighbor SPINE-EVPN-TRANSIT ebgp-multihop
      neighbor SPINE-EVPN-TRANSIT send-community extended
      neighbor SPINE-EVPN-TRANSIT remote-as 65001
      neighbor SPINE-EVPN-TRANSIT maximum-routes 0
      neighbor 172.16.0.1 peer group SPINE-EVPN-TRANSIT
      neighbor 172.16.0.2 peer group SPINE-EVPN-TRANSIT
      redistribute connected
    !
    !! Enable address family evpn for the SPINE-EVPN-TRANSIT peer group
    address-family evpn
      neighbor SPINE-EVPN-TRANSIT activate
    !
    !! Disable address family ipv4 on SPINE-EVPN-TRANSIT peer group
    address-family ipv4
      no neighbor SPINE-EVPN-TRANSIT activate
    !

* Add the CLI text from above to the new configlet

.. image:: images/cvp-l2vpn/leaf3-l2vpn-configlet.png
    :align: center
    :width: 50%
|br|

* Validate configlet syntax on ``leaf3``

.. image:: images/cvp-l2vpn/leaf3-l2vpn-configlet-validate.png
    :align: center
    :width: 50% 
|br|

.. image:: images/cvp-l2vpn/leaf3-l2vpn-configlet-validate2.png
    :align: center
    :width: 50% 
|br|

5. Assign the EVPN configlet to ``leaf3``

* Click on **Provisioning**, then click on **Network Provisioning** in the left selection column
* Right click on **leaf3**, Click on **Manage->Configlets** and then search for ``Leaf3-l2vpn``

.. image:: images/cvp-l2vpn/leaf3-l2vpn-configlet-manage.png
    :align: center
    :width: 50% 
|br|

* Click the checkbox next to ``Leaf3-l2vpn-Lab-Full-user``

.. image:: images/cvp-l2vpn/leaf3-l2vpn-configlet-assign.png
    :align: center
    :width: 50% 
|br|

* Click **Validate**, review the new lines added to the **Designed Configuration**

.. image:: images/cvp-l2vpn/leaf3-l2vpn-configlet-assign-validate.png
    :align: center
    :width: 35% 
|br|

* click **Save**

.. image:: images/cvp-l2vpn/leaf3-l2vpn-configlet-assign-validate-compare.png
    :align: center
    :width: 50% 
|br|

* Click **Save** on the **Network Provisioning** main view

* **Note:** a Task will be generated

.. image:: images/cvp-l2vpn/leaf3-l2vpn-configlet-main-save.png
    :align: center
    :width: 50% 
|br|

6. Create a **Change Control** with the generated Task

* Click **Tasks** from the left selection column

* Click the checkbox next to the generated task from the pool of **Assignable Tasks**

.. image:: images/cvp-l2vpn/leaf3-l2vpn-cc-task.png
    :align: center
    :width: 50% 
|br|

* Click **+ Create Change Control with 1 Task**

.. image:: images/cvp-l2vpn/leaf3-l2vpn-cc-create-cc.png
    :align: center
    :width: 50% 
|br|

* Click **Review and Approve** on the newly created **Change Control**

.. image:: images/cvp-l2vpn/leaf3-l2vpn-cc-review-approve.png
    :align: center
    :width: 50% 
|br|

* Click **Execute Change Control** in upper right of the UI

.. image:: images/cvp-l2vpn/leaf3-l2vpn-cc-execute.png
    :align: center
    :width: 50% 
|br|

* Click **Execute** in the resulting confirmation dialog box

.. image:: images/cvp-l2vpn/leaf3-l2vpn-cc-execute-confirm.png
    :align: center
    :width: 50% 
|br|

7. Verify the EVPN BGP protocol overlay

* **Note:** This verification step can also be done on the CLI of ``leaf3`` 
* Click **Provisioning**, then click **Snapshot Configuration**

.. image:: images/cvp-l2vpn/leaf3-l2vpn-snapshot-config.png
    :align: center
    :width: 50% 
|br|

* Click **or create a new configuration** in the center of the **Snapshot Configuration** screen

.. image:: images/cvp-l2vpn/leaf3-l2vpn-snapshot-config-new.png
    :align: center
    :width: 50% 
|br|


* Under **Snapshot Configuration** enter ``ip-bgp-evpn-summary`` under Name 
* In the **Commands** dialog enter the following commands

.. code-block:: text

  show bgp evpn summary
  show ip bgp summary
  show ip route bgp

* Under devices, select ``leaf3``

.. image:: images/cvp-l2vpn/leaf3-l2vpn-snapshot-config-content.png
    :align: center
    :width: 50% 
|br|

* Click **Save**

* Click **Devices**, then click **leaf3**
* Click **Snapshots** in the left selection column
* Click **ip-bgp-evpn-summary** 
* **Note:** Under ``show bgp evpn summary`` you should see that there are two **overlay** BGP peers, peered with the loopback0 interface IP address
* **Note:** Under ``show ip bgp summary`` you should see that there are two **underlay** BGP peers, peered with the p2p interfaces (Et2 & Et3) IP addresses
* **Note:** Under ``show ip route bgp`` you should see that there are a number of ECMP routes to networks via the p2p interfaces (ET2 & ET3) of the peers  

.. image:: images/cvp-l2vpn/leaf3-l2vpn-snapshot-ip-bgp-evpn-summary.png
    :align: center
    :width: 50% 
|br|

8. Add the L2VPN VXLAN configuration to the previously created configlet ``Leaf3-l2vpn-Lab-Full-user``

* Click **Provisioning**, then click **Configlets**
* Search for ``l2vpn`` then click **Leaf3-l2vpn-Lab-Full-user**
* Click the **edit** button and add the following configuration lines in **bold** below, to the configlet created in step (4.)
* **Note:** For simplicity add the new lines in the same position and order as they appear in **bold** below 
* **Note:** This step will add an L2VPN to ``leaf3`` to extend VLAN 12 using VXLAN from ``leaf3`` to ``leaf1``

.. image:: images/cvp-l2vpn/leaf3-l2vpn-edit-configlet.png
    :align: center
    :width: 50% 
|br|


.. raw:: html
 
 <pre>
    !! Configure physical interface et4 for LACP and Port-Channel4 in access vlan 12
    interface Port-Channel4
      switchport mode access
      switchport access vlan 12
    !
    interface Ethernet1
      shutdown
    !
    !! Configure interface et2 as a p2p leaf to spine L3 link
    interface Ethernet2
      no switchport
      ip address 172.16.200.10/30
    !
    !! Configure interface et3 as a p2p leaf to spine L3 link
    interface Ethernet3
      no switchport
      ip address 172.16.200.26/30
    !
    !! Configure physical interface et4 for LACP (active) in Port-Channel4
    interface Ethernet4
      channel-group 4 mode active
      lacp timer fast
    !
    interface Ethernet5
      shutdown
    !
    !! Configure loopback0 interface for use with routing protocol (BGP)
    interface Loopback0
      ip address 172.16.0.5/32
    !
    !! Configure loopback1 interface for use as the VTEP IP interface
    interface Loopback1
      ip address 3.3.3.3/32
      ip address 99.99.99.99/32 secondary
    !
    <b>interface Vxlan1
    vxlan source-interface Loopback1
    vxlan udp-port 4789
    vxlan vlan 12 vni 1200</b>
    !
    !! Configure routing protocol BGP Underlay
    router bgp 65103
      router-id 172.16.0.5
      maximum-paths 2 ecmp 2
      neighbor SPINE peer group
      neighbor SPINE bfd
      neighbor SPINE remote-as 65001
      neighbor SPINE maximum-routes 12000
      neighbor 172.16.200.9 peer group SPINE
      neighbor 172.16.200.25 peer group SPINE
    !! Configure routing protocol BGP overlay
      neighbor SPINE-EVPN-TRANSIT peer group
      neighbor SPINE-EVPN-TRANSIT next-hop-unchanged
      neighbor SPINE-EVPN-TRANSIT update-source Loopback0
      neighbor SPINE-EVPN-TRANSIT ebgp-multihop
      neighbor SPINE-EVPN-TRANSIT send-community extended
      neighbor SPINE-EVPN-TRANSIT remote-as 65001
      neighbor SPINE-EVPN-TRANSIT maximum-routes 0
      neighbor 172.16.0.1 peer group SPINE-EVPN-TRANSIT
      neighbor 172.16.0.2 peer group SPINE-EVPN-TRANSIT
      redistribute connected
    !
    <b>vlan 12
    rd 3.3.3.3:12
    route-target both 1:12
    redistribute learned</b>
    !
    !! Enable address family evpn for the SPINE-EVPN-TRANSIT peer group
    address-family evpn
      neighbor SPINE-EVPN-TRANSIT activate
    !
    !! Disable address family ipv4 on SPINE-EVPN-TRANSIT peer group
    address-family ipv4
      no neighbor SPINE-EVPN-TRANSIT activate
    !
    </pre>

* Repeat the process described in step (6.) to push the additional configuration to ``leaf3``
|br|

9. Verify l2vpn VXLAN operation with CVP Telemetry

* Using the method described in step (7.), create a new snapshot called ``vxlan-info``

  **Note:** This verification can also be done on the CLI of ``leaf1`` and ``leaf3``

* Select ``leaf1`` and ``leaf3`` under the **Devices** dropdown of the new Snapshot configuration

* Add the following commands to the **Commands** field of the new snapshot

.. code-block:: text

  show bgp evpn route-type imet
  show bgp evpn route-type mac-ip
  show vxlan address-table

* Wait 5-10 minutes you will see the snapshot data populated 

  **Note:** wait for the snapshot to run and until after you ping from ``host1`` to ``host2`` before viewing this snapshot

.. image:: images/cvp-l2vpn/leaf3-l2vpn-snapshot-vxlan-info.png
    :align: center
    :width: 50%
|br|

* From **Device** page **Inventory** click on **leaf3**
* Click on **VXLAN** in the left selection column under **Switching**

.. image:: images/cvp-l2vpn/leaf3-l2vpn-vxlan-verification.png
 :align: center
 :width: 50% 
|br|

* **Note:** you should now see the VLANs to VNI mappings related the to VXLAN configuration on ``leaf3``

* Ping ``host1`` from ``host2``
    
.. code-block:: text

    host1# ping 172.16.112.201
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

* Again, click on **VXLAN** in the left selection column under **Switching**

.. image:: images/cvp-l2vpn/leaf3-l2vpn-vxlan-verification-mac.png
    :align: center
    :width: 50% 
|br|

* **Note:** In addition to the VLAN to VNI Mappings, you will see an entry in the ``VXLAN MAC Address Table`` section

* Click on the **MAC Address Table** for ``leaf3`` in left selection column

.. image:: images/cvp-l2vpn/leaf3-l2vpn-vxlan-verification-mac-table.png
    :align: center
    :width: 50% 
|br|

* **Note:** You will see the local MAC Address of Host2 on Port-Channel 4 and the remote MAC Address of Host1 via port ``Vxlan1``

* Review the snapshot ``vxlan-info`` created earlier in step (9.)
* **Note:** ``show bgp evpn route-type imet`` will show the VXLAN flood lists dynamically built and distributed by BGP EVPN
* **Note:** ``show bgp evpn route-type mac-ip`` will show the VXLAN mac to IP bindings being sent via BGP EVPN 
* **Note:** ``show vxlan address-table`` will show the VLAN, MAC Address and VXLAN interface and remote VTEP IP

.. image:: images/cvp-l2vpn/leaf3-l2vpn-vxlan-info-snapshot.png
    :align: center
    :width: 50% 
|br|

* Click on **Topology View** 
* Click the **Link Overlay** dropdown in the left selection column

.. image:: images/cvp-l2vpn/leaf3-l2vpn-vxlan-before.png
    :align: center
    :width: 50%
|br|

* Click the **VXLANs** selection, also click and view the **VLANs** selection
* **Note:** You should see VLAN 12 on ``leaf3`` & ``leaf1``
* **Note:** You should see that ``leaf3`` has both VLAN 12 and VNI 1200 with a dashed line to ``leaf1``
* **Note:** You should **now** see VLAN 12 and VNI 1200 as a dashed line from leaf3 to leaf1, indicating VLAN 12 is extended via VNI 1200

.. image:: images/cvp-l2vpn/leaf3-l2vpn-vxlan-vlan-after.png
    :align: center
    :width: 50%
|br|

.. image:: images/cvp-l2vpn/leaf3-l2vpn-vxlan-vni-after.png
    :align: center
    :width: 50%
|br|

**LAB COMPLETE!**
