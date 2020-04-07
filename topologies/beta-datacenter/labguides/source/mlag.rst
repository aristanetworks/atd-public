MLAG
====

.. image:: images/mlag_1.png
   :align: center

.. note:: Did you know the “mlag” script is composed of Python code that
          uses the CloudVision Portal REST API to automate the provisioning of
          CVP Configlets. The configlets that are configured via the REST API
          are ``Spine1-MLAG-Lab``, ``Spine2-MLAG-Lab``, ``Leaf1-MLAG-Lab``,
          ``Leaf2-MLAG-Lab``, ``Leaf3-MLAG-Lab``. In addition each switch also
          gets the ``VLANs`` configlet.

.. note:: The manually-entered commands below that are part of this lab are
          equivalent to ``Leaf4-MLAG-Lab``.

1. Log into the **LabAccess** jumpserver:

   1. Type ``mlag`` at the prompt. The script will configure the datacenter with the exception of **Leaf4**.
   2. On **Leaf3**, verify MLAG operation (it should not be operating correctly)

        .. code-block:: text

            show mlag
            show mlag detail
            show mlag interfaces

2. Configure MLAG on the **Leaf4** switch using the following criteria

   1. Configure Port-channel on **Leaf4** to used for MLAG communication between **Leaf3** & **Leaf4**.

        .. code-block:: text

            configure
            interface port-channel 10
              switchport mode trunk

            interface ethernet 1
              switchport mode trunk
              channel-group 10 mode active

      .. note::
       A *channel-group* is a group of interfaces on a single Arista switch. A *channel-group* is associated with a *port-channel* interface immediately upon its creation. The *channel-group* command implicitly creates the matching *port-channel* with the same ID, which is *10* in this case. The *switchport mode trunk* command allows all VLANs on *port-channel 10*.

   2. Verify switching operation

        .. code-block:: text

            show interfaces status
            show lldp neighbors
            show interfaces trunk

      .. note::
       Each switch is assigned a globally unique sysID by concatenating the 16-bit system priority to a 48-bit MAC address of one of the switch's physical ports. This sysID is used by peer devices when forming an aggregation to verify that all links are from the same switch - for environments where the MLAG peer link contains multiple physical links - which it does NOT in this example. A *trunk group* is the set of physical interfaces that comprise the trunk and the collection of VLANs whose traffic is carried on the trunk. The traffic of a VLAN that belongs to one or more trunk groups is carried only on ports that are members of trunk groups to which the VLAN belongs, i.e., VLANs configured in a *trunk group* are ‘pruned’ off all ports that are not associated with the trunk group. The spanning-tree protocol (STP) is disabled for the peer-link VLAN 4094 to prevent any potential STP disruption on the interpeer communications link. Since VLAN 4094 has been restricted to only be on the peer-link (Po10) by *trunk group MLAGPEER* & *switchport trunk group MLAGPEER* (see step #2.3) the chance of a loop is eliminated. To prevent loops do NOT add this *trunk group MLAGPEER* to any other interface links.

   3. Configure the MLAG VLAN (both Layer 2 and Layer 3).

        .. code-block:: text

            configure
            vlan 4094
              trunk group MLAGPEER

            interface port-channel 10
              switchport trunk group MLAGPEER
              exit

            no spanning-tree vlan-id 4094

            interface vlan 4094
              description MLAG PEER LINK
              ip address 172.16.34.2/30

            ping 172.16.34.1

      .. note::
       The *ip address 172.16.34.2/30* (see step #2.3) assigned to one side of the peer-link can be any unicast address that does not conflict with any SVIs on the same switch. The *local-interface vlan 4094* command (see step #2.4) specifies the SVI upon which the switch sends MLAG control traffic. The IP address is specified within the definition of the VLAN associated with this local interface, which you already performed earlier above. While the peer-link's (designated with the command *peer-link port-channel 10* (see below)) primary purpose is to exchange MLAG control information between the 2 peer switches, it also carries dataplane traffic from devices that are attached to only 1 MLAG peer & have no alternative path. This peer-link can also carry traffic in topology failure scenarios (i.e. one of these peer-link switches loses all its uplinks to the spine switches). The *domain-id MLAG34* command determines the MLAG domain that consists of these 2 peer switches & the links that connect these 2 switches. The *domain-id* is case-sensitive and must match the same *domain-id* on the other peer switch.

   4. Define the MLAG Domain.

        .. code-block:: text

            configure
            mlag
              domain-id MLAG34
              local-interface vlan 4094
              peer-address 172.16.34.1
              peer-link port-channel 10

   5. Configure Port-channels and interfaces on **Leaf4** connecting to **Spine1** & **Spine2**.

        .. code-block:: text

            configure
            interface port-channel 34
              switchport mode trunk
              mlag 34

            interface ethernet 2-3
              channel-group 34 mode active
              switchport mode trunk

      .. note::
       The *mlag 34* (see #2.5) assigns an MLAG ID to *interface port-channel 34*. MLAG peer switches form an MLAG when each switch configures the same MLAG ID to a port-channel interface. This is **different** than the MLAG *domain-id* (see #2.4). The global-scope *mlag* command above (see #2.4) just enters the global MLAG configuration scope of the Arista switch.

   6. Configure Port-channels on **Leaf4** connecting to **Host2**

        .. code-block:: text

            configure
            interface port-channel 4
              switchport access vlan 12
              mlag 4

            interface ethernet 4
              channel-group 4 mode active

            interface ethernet5
              shutdown

3. Validate MLAG on the **Leaf4** switch using the following:

   1. Verify MLAG operation

        .. code-block:: text

            show mlag
            show mlag detail
            show mlag interfaces

   2. Verify switching operation

        .. code-block:: text

            show interfaces status
            show lldp neighbors
            show interfaces trunk

   3. Validate connectivity from **Host1** to **Host2** by logging into **Host1** through the menu (option 7) or using screen.

        .. code-block:: text

              enable
              ping 172.16.112.202

|

**LAB COMPLETE!**
