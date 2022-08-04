# ATD-AVD-Dual-DC

## Arista Dual DC w/Ansible

(Beta stage, not for production use)

### About

The Arista Dual DC ATD allow users to simulate a very common network scenario, deploying and test a dual data centers topology utilizing Ansible and Arista Cloudvision.

### Topology

![ATD - Dual DataCenter Topology](images/atd-topo.png "ATD Dual DataCenter")

## Topology Device List

### Data Center 1:

| Device    | Mgmt IP Address |
| -------   | --------------- |
| s1-spine1 | 192.168.0.10  |
| s1-spine2 | 192.168.0.11  |
| s1-leaf1  | 192.168.0.12  |
| s1-leaf2  | 192.168.0.13  |
| s1-leaf3  | 192.168.0.14  |
| s1-leaf4  | 192.168.0.15  |
| s1-host1  | 192.168.0.16  |
| s1-host2  | 192.168.0.17  |
| s1-brdr1  | 192.168.0.100 |
| s1-brdr2  | 192.168.0.101 |
| s1-core1  | 192.168.0.102 |
| s1-core2  | 192.168.0.103 |

### Data Center 2:

| Device    | Mgmt IP Address |
| ------    | --------------- |
| s2-spine1 | 192.168.0.20  |
| s2-spine2 | 192.168.0.21  |
| s2-leaf1  | 192.168.0.22  |
| s2-leaf2  | 192.168.0.23  |
| s2-leaf3  | 192.168.0.24  |
| s2-leaf4  | 192.168.0.25  |
| s2-host1  | 192.168.0.26  |
| s2-host2  | 192.168.0.27  |
| s2-brdr1  | 192.168.0.200 |
| s2-brdr2  | 192.168.0.201 |
| s2-core1  | 192.168.0.202 |
| s2-core2  | 192.168.0.203 |

## Getting Started

To Setup ATD Topology run the following commands
 - cd labfiles/AristaValidatedDesigns
 - make atd-setup
 - make provision
 - Deploy pending tasks from cvp
 - Experiment with AVD ...

 ## Step-by-step Procedures

 For more detailed instructions, a complete step-by-step guide is available [HERE.](./DEMO.md)

 ## Resources

 - [Arista AVD Public Documentation](https://www.avd.sh)
 - [Arista Ansible AVD Collection](https://github.com/aristanetworks/ansible-avd)
 - [Arista Cloudvision Collection](https://github.com/aristanetworks/ansible-cvp)
