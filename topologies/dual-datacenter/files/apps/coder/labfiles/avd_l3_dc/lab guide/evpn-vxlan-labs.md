# EVPN VXLAN Labs

The goal of these labs are to show how AVD eases Day 2 and beyond network operations.  You will complete two 

<br>
<br>

## Lab 1 - Add VLANs to EVPN VXLAN Topology

This lab will show you how simple it is to automate the configuration changes associated with adding additional VLANs to your EVPN VXLAN topology.  In a non-automated EVPN VXLAN topology, anytime a new VLAN needs to be added and extended, it has to be created on every switch, added to VXLAN, and added to the BGP configuration on the relevant devices.  During this lab, you will modify the `dc1_fabric_services.yml` and `dc2_fabric_services.yml` vars files to add the new VLANs listed below.  



Modify the ***fabric_services*** vars files to add the following VLANs:

```yaml

VLAN ID: 30
    Name: thirty
    Description: thirty
    Tags: ATD
    MTU: 9014
    vIP: 10.30.30.1/24
    EVPN:  True

VLAN ID: 40
    Name: forty
    Description: forty
    Tags: ATD
    MTU: 9014
    vIP: 10.40.40.1/24
    EVPN:  True

VLAN ID: 50
    Name: fifty
    Description: fifty
    Tags: ATD
    MTU: 9014
    vIP: 10.50.50.1/24
    EVPN:  True

```

After modifying and saving the vars files, complete the following steps:

1) Issue the `make build_dc1` and `make build_dc2` to generate the new structured and device configurations.

2) Review the configurations in their respective directories and verify the changes are correct.

3) Review the changes to the documentation that is auto-created.

4) Issue the `make deploy_dc1_cvp` and `make deploy_dc2_cvp`, review the created change controls in CVP, and approve.

5) Login to leaf switches 1 and 2 and verify the new configurations are present.

<br>
<br>


## Lab 2 - Add Leaf Pairs 3 and 4

This lab will show you the simplicity in adding additional leaf pairs to your existing Layer 3 leaf/spines topology.  In a non-automated topology, when deploying new leafs, you would need to duplicate or create the base configs for the new leafs, and then modify the configurations of the existing devices to add them into the EVPN VXLAN overlay.  For this lab, you will be adding leafs 3 and 4 in each datacenter into the network topology by following the below steps.

1) The first step is to add the new leafs into their respective inventory files:

For dc1, you will modify:  `sites/dc1/inventory.yml`

Add the following switches into the correct location in the file:

```yaml
s1-Leaf3
s1-Leaf4
```

For dc2, you will modify:  `sites/dc2/inventory.yml`

Add the following switches into the correct location in the file:

```yaml
s2-Leaf3
s2-Leaf4
```

2) To enable AVD to generate all the required configuration changes, you will only need to modify the `*_fabric.yml` files for each datacenter.  Follow the  YAML file structure for the existing leaf pairs, 1 and 2, and enter the required changes using the parameters below:

    1) For dc1, you will modify:  `sites/dc1/group_vars/dc1_fabric.yml`

Use the following parameters for Leafs 3 and 4, which are leaf pair 2.

```yaml
group: LeafPair2
bgp_as: 65002

s1-Leaf3
    id: 18
    mgmt_ip: 192.168.0.14
    uplink_switch_interfaces: Ethernet4, Ethernet4

s1-Leaf4
    id: 20
    mgmt_ip: 192.168.0.15
    uplink_switch_interfaces: Ethernet5, Ethernet5
```

    2) For dc2, you will modify:  `sites/dc2/group_vars/dc2_fabric.yml`

Use the following parameters for Leafs 3 and 4, which are leaf pair 2.

```yaml
group: LeafPair2
bgp_as: 65102

s2-Leaf3
    id: 118
    mgmt_ip: 192.168.0.24
    uplink_switch_interfaces: Ethernet4, Ethernet4

s2-Leaf4
    id: 120
    mgmt_ip: 192.168.0.25
    uplink_switch_interfaces: Ethernet5, Ethernet5
```

After modifying and saving the vars files, complete the following steps:

1) Issue the `make build-dc1` and `make build-dc2` to generate the new structured and device configurations.

2) Review the configurations in their respective directories and verify the changes are correct.  

3) Review the changes to the documentation that is auto-created.

4) Issue the `make deploy-dc1` and `make deploy-dc2`, review the created change controls in CVP, and approve.

5) Login to leaf switches 3 and 4 and verify the new configurations are present.
