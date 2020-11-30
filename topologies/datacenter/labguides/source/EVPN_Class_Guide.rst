.. image:: images/arista_logo.png
   :align: center

EVPN Lab Guide
====================

Topology Quick View:
-------------------------

.. image:: images/EVPN_Class_Quick_Topology_Image.png
   :align: center

Topology Detailed View:
-----------------------------

.. image:: images/EVPN_Class_Detailed_Topology_Image.png
   :align: center

Lab 1: IP Underlay Control-Plane Buildout
===============================================

    .. note:: To begin this lab, go to the ssh login menu, select the *labs* option or option *97*, then go to *EVPN Class Guide*,
        then execute option *1* or *lab1* to deploy the topology.

    #. Reachability between loopbacks is required, reachability to Point-to-Point underlay prefixes is optional

    #. Must use a routing protocol to accomplish this task

    #. The chosen protocol’s router-id must be a globally unique and pingable address on the device

    #. There is a desire to only run a single routing protocol within the Data Center

    #. If using an address-family aware protocol, all peerings within an AFI/SAFI must be explicitly permitted

    #. To prevent temporary black-holes, no switch should advertise reachability to a prefix until it is programmed into hardware

    .. note:: Important: This feature will not work in a virtual environment, as there is no hardware to program the prefixes into. This step can be skipped,
            but the command to accomplish this task is *update wait-install* under the bgp process.

    #. Though not required today, the ability to perform per-prefix traffic engineering in the underlay, based on a administrator-defined value, is desired

    #. Spine and Leaf switches must use ECMP within the underlay

    #. Regardless of routing protocol chosen, if using a dynamic peerings, all discovered neighbors must be authenticated, and be explicitly trusted sources

    #. Addition or Removal of Leaf switches in the future should not require any routing configuration changes on the Spines

Lab 2: EVPN Control-Plane Provisioning
==============================================

    .. note:: If you are starting out in this lab, go to the ssh login menu, select the *labs* option or option *97*, then go to *EVPN Class Guide*,
        then execute option *2* or *lab2* to deploy the topology.

    #. Enable peering in the EVPN address-family between Spine and Leaf switches

    #. A globally unique loopback must be used as the source of these peerings

    #. Fast detection of peer failure must be enabled to provide fast convergence

    #. Devices must be capable of establishing peerings in the EVPN address-family with devices up to three routing hops away

    #. Spines must not modify any fields within the payload of a transient BGP EVPN Update

    #. All peerings within the EVPN address-family must be explicitly permitted

    #. Control-plane signaling via communities must be supported

    #. If using a dynamic peerings, all discovered neighbors must be authenticated and explicitly trusted sources

    #. Addition or Removal of Leaf switches in the future should not require any routing configuration changes on the Spines

    #. There is a large amount of anticipated EVPN control-plane state. Ensure that peerings are not flapped or disabled due to control-plane scale

Lab 3: MLAG
========================

    .. note:: If you are starting out in this lab, go to the ssh login menu, select the *labs* option or option *97*, then go to *EVPN Class Guide*,
        then execute option *3* or *lab3* to deploy the topology.

    #. Devices will be dual-homed to VTEPs, with the expectation that an LACP port-channel will be formed, and forwarding will be active/active

    #. Each pair of VTEPs will be deployed with a physical interconnect between each other

    #. The deployed multi-homing solution must be easily repeatable across multiple VTEP pairs

    #. VTEPs deployed as a pair must present themselves as a single logical VTEP within the EVPN control-plane

    #. If both spine-facing links on a VTEP fail, that VTEP must be able to maintain it’s EVPN peerings and forwarding capabilities

    #. If a VTEP within a pair is rebooted, ensure that the rebooted VTEP does not transition any host-facing links into a forwarding state until the control-plane has been fully converged

    #. Regardless of which VTEP in the pair receives a VXLAN packet, if a routing operation is required after decap, that receiving VTEP should locally perform that routing operation.

    #. Once MLAG has been deployed, establish an LACP port-channel to HostA and HostC
    
    .. note:: The host-side configuration is already completed. If MLAG is configured correctly, the port-channel will come up

Lab 4: Layer2 VPN Service Provisioning
==============================================

    .. note:: If you are starting out in this lab, go to the ssh login menu, select the *labs* option or option *97*, then go to *EVPN Class Guide*,
        then execute option *4* or *lab4* to deploy the topology.

    #. All L2VPN services will be provided via VXLAN data-plane encapsulation

    #. Enable VTEP functionality on all Leaf switches

    #. Create VLANs necessary to provide bridging operations for locally attached hosts

    #. VXLAN:VNI mappings should be pre-provisioned to help ease future provisioning activities

        #. All VNIs will be 10,000 + VLAN ID

        #. VLANs 10 through 30 will be pre-provisioned on day 1

    #. Configure Route-Distinguishers in a way that enables fast convergence and provides a quick method to validate the source of an EVPN route

    #. L2VPN services must be provisioned in a way that enables the mapping of multiple bridge domains to a single MAC-VRF, reducing config size and the administrative overhead of future L2VPN service provisioning
        
        #. VLANs 10 through 30 should be mapped to a single MAC-VRF

    #. When provisioning a tenant’s MAC-VRF, import and export Route-Targets should be configured using the format “Tenant ID:Tenant ID”
        
        #. VRF A Tenant ID is “1”

    #. Reachability information for all locally learned MAC addresses must be automatically originated into the EVPN control-plane

    #. Upon completion of this lab, HostA should be able to ping HostD

Lab 5: Layer3 VPN Service Provisioning
=============================================

    .. note:: If you are starting out in this lab, go to the ssh login menu, select the *labs* option or option *97*, then go to *EVPN Class Guide*,
        then execute option *5* or *lab5* to deploy the topology.

    #. All L3VPN services will be provided via VXLAN data-plane encapsulation

    #. Each tenant will receive their own unique VRF
        
        #. Create a VRF for Tenant “A”

    #. Configure Route-Distinguishers in a way that enables fast convergence and provides a quick method to validate the source of an EVPN route

    #. When provisioning a tenant’s IP-VRF, import and export Route-Targets should be configured using the format “Tenant ID:Tenant ID”
        
        #. VRF A Tenant ID is “1”

    #. VTEPs must not require that every VLAN and SVI be locally configured for reachability between endpoints within the tenant VRF

    #. When traffic is crossing a subnet boundary, and the destination host is behind a remote VTEP, the ingress VTEP must never bridge towards the destination host

    #. First Hop Gateway IP and MAC address must exist on all VTEPs where an L3VPN services are provisioned
    
        #. Only define the SVIs that are required for locally connected hosts
    
        #. For each subnet, a consistent Gateway IP and MAC address must be used across all VTEPs where the subnet exists

    #. It is anticipated that the environment scale will grow over time to ~45,000 hosts. Ensure that Remote ARP forwarding entries do not limit the scale of the environment

    #. VTEPs must originate reachability to locally attached prefixes within a tenant VRF

    #. There should never be any tenant prefixes within the IPv4 Underlay Control-Plane


Lab 6: Day-2 Ops
======================

    .. note:: If you are starting out in this lab, go to the ssh login menu, select the *labs* option or option *97*, then go to *EVPN Class Guide*,
        then execute option *6* or *lab6* to deploy the topology.

    #. A new VLAN / L2VPN service has been requested

        #. VLAN 25 will be used for this task

        #. A new endpoint in this VLAN will be connected to interface Ethernet6 on LEAF1

        #. Create a new L2VPN service for VLAN 25 on all leafs, and stage the interface configuration

        #. Validate that the expected EVPN control-plane state 

        #. **No changes can be made to the BGP or VXLAN interface configurations**

    #. Create a new L3VPN service for a new tenant (Tenant B). This tenant requires L2VPN service for vlans 31-40. L3VPN services are only required for vlans 35 and 40

        #. The requested L2VPN and L3VPN services must be available on all Leaf switches

        #. For MAC-VRF and IP-VRF, follow the same Route Distinguisher and Route-Target guidelines as Tenant ‘A’

        #. VRF B Tenant ID is 2

        #. VLAN 35 subnet: 35.35.35.0/24

        #. VLAN 40 subnet: 40.40.40.0/24

        #. Once complete, validate that the EVPN control-plane contains the expected state


    #. (Optional) The operations team would like the ability to ping any Tenant ‘A’ workload directly from any Leaf switch in the environment. This will require the response to source from an IP other than the anycast gateway.

        #. Use Loopback201 as the source IP with an IP address of 201.0.0.X/32 (X=Switch ID)

    #. (Optional) The MLAG IP addresses need to be updated on all of the switches during a change window. Reconfigure MLAG IP addresses with the new IP scheme below:
        
        #. Leaf1 and Leaf 3 IP - 192.168.255.254/31
        
        #. Leaf2 and Leaf 4 IP - 192.168.255.255/31
        
        #. Verify that MLAG status is up and the MLAG interfaces are forwarding correctly




Lab 7: Troubleshooting
===========================

    .. note:: You *must* use the ssh login menu to deploy each of these scenarios. Select the *labs* option or option *97*, then go to *EVPN Class Guide*,
        then execute the appropriate option for each scenario.

    #. Scenario A

        #. HostA cannot communicate with HostD

    #. Scenario B
    
        #. HostB cannot communicate with HostC

    #. Scenario C
    
        #. HostA cannot communicate with HostD