Bridging Role for EOS
=====================

The arista.eos-bridging role creates an abstraction for common layer 2 bridging configuration.
This means that you do not need to write any ansible tasks. Simply create
an object that matches the requirements below and this role will ingest that
object and perform the necessary configuration.

This role specifically enables configuration of EOS switchports and vlans.
It also exposes purging functions to remove extraneous trunk groups in both
the vlan and switchport configuration.


Installation
------------

```
ansible-galaxy install arista.eos-bridging
```


Requirements
------------

Requires an SSH connection for connectivity to your Arista device. You can use
any of the built-in eos connection variables, or the convenience ``provider``
dictionary.

Role Variables
--------------

There are some variables that control global purging functions.

|                          Variable | Type                  | Notes                                    |
| --------------------------------: | --------------------- | ---------------------------------------- |
|       eos_purge_vlan_trunk_groups | boolean: true, false* | If true, when the role provisions vlan trunk groups, it will remove extraneous trunk groups that are present in the configuration but haven't been specified in your host variables. |
| eos_purge_switchport_trunk_groups | boolean: true, false* | If true, when the role provisions switchport trunk groups, it will remove extraneous trunk groups that are present in the configuration but haven't been specified in your host variables. |
|                   eos_purge_vlans | boolean: true, false* | If true, when the role provisions vlans, it will remove extraneous vlans that are present in the configuration but haven't been specified in your host variables. |


The tasks in this role are driven by the ``switchports`` and ``vlans`` objects
described below:

**switchports** (list) each entry contains the following keys:

|                 Key | Type                      | Notes                                    |
| ------------------: | ------------------------- | ---------------------------------------- |
|                name | string (required)         | The interface name of the switchport     |
|                mode | choices: access*, trunk   | Mode of operation for the interface      |
|         access_vlan | string                    | Only required for http or https connections |
|   trunk_native_vlan | string                    | Vlan associated with the interface. Used if mode=trunk |
| trunk_allowed_vlans | list                      | The native vlan used when mode=trunk.    |
|        trunk_groups | list                      | The set of trunk groups configured on the interface |
|               state | choices: present*, absent | Set the state for the switchport         |

**vlans** (list) each entry contains the following keys:

|          Key | Type                      | Notes                                    |
| -----------: | ------------------------- | ---------------------------------------- |
|       vlanid | int (required)            | The vlan id. Example: 1, 1000, 1024. Without the Vlan |
|         name | string                    | The name for the vlan. No spaces allowed. |
| trunk_groups | list                      | The set of trunk groups configured on the interface |
|       enable | boolean: true*, false     |                                          |
|        state | choices: present*, absent | Set the state for the vlan               |


```
Note: Asterisk (*) denotes the default value if none specified
```

Configuration Variables
-----------------------

|                     Key | Choices      | Description                              |
| ----------------------: | ------------ | ---------------------------------------- |
| eos_save_running_config | true*, false | Specifies whether to write any changes to the running-config resulting from the role execution to memory, copying the configuration to the startup-config. |

```
Note: Asterisk (*) denotes the default value if none specified
```

Connection Variables
--------------------

Ansible EOS roles require the following connection information to establish
communication with the nodes in your inventory. This information can exist in
the Ansible group_vars or host_vars directories, or in the playbook itself.

|         Key | Required | Choices    | Description                              |
| ----------: | -------- | ---------- | ---------------------------------------- |
|        host | yes      |            | Specifies the DNS host name or address for connecting to the remote device over the specified *transport*. The value of *host* is used as the destination address for the transport. |
|        port | no       |            | Specifies the port to use when building the connection to the remote device. This value applies to either acceptable value of *transport*. The port value will default to the appropriate transport common port if none is provided in the task (cli=22, http=80, https=443). |
|    username | no       |            | Configures the usename to use to authenticate the connection to the remote device.  The value of *username* is used to authenticate either the CLI login or the eAPI authentication depending on which *transport* is used. If the value is not specified in the task, the value of environment variable ANSIBLE_NET_USERNAME will be used instead. |
|    password | no       |            | Specifies the password to use to authenticate the connection to the remote device. This is a common argument used for either acceptable value of *transport*. If the value is not specified in the task, the value of environment variable ANSIBLE_NET_PASSWORD will be used instead. |
| ssh_keyfile | no       |            | Specifies the SSH keyfile to use to authenticate the connection to the remote device. This argument is only used when *transport=cli*. If the value is not specified in the task, the value of environment variable ANSIBLE_NET_SSH_KEYFILE will be used instead. |
|   authorize | no       | yes, no*   | Instructs the module to enter priviledged mode on the remote device before sending any commands. If not specified, the device will attempt to excecute all commands in non-priviledged mode. If the value is not specified in the task, the value of environment variable ANSIBLE_NET_AUTHORIZE will be used instead. |
|   auth_pass | no       |            | Specifies the password to use if required to enter privileged mode on the remote device.  If *authorize=no*, then this argument does nothing. If the value is not specified in the task, the value of environment variable ANSIBLE_NET_AUTH_PASS will be used instead. |
|   transport | yes      | cli*, eapi | Configures the transport connection to use when connecting to the remote device. The *transport* argument supports connectivity to the device over cli (ssh) or eapi. |
|     use_ssl | no       | yes*, no   | Configures the transport to use SSL if set to true only when *transport=eapi*.  If *transport=cli*, this value is ignored. |
|    provider | no       |            | Convience method that allows all the above connection arguments to be passed as a dict object. All constraints (required, choices, etc) must be met either by individual arguments or values in this dict. |

```
Note: Asterisk (*) denotes the default value if none specified
```

Ansible Variables
-----------------

|    Key | Choices      | Description                              |
| -----: | ------------ | ---------------------------------------- |
| no_log | true, false* | Prevents module arguments and output from being logged during the playbook execution. By default, no_log is set to true for tasks that gather and save EOS configuration information to reduce output size. Set to true to prevent all output other than task results. |

```
Note: Asterisk (*) denotes the default value if none specified
```

Dependencies
------------

The eos-bridging role is built on modules included in the core Ansible code.
These modules were added in ansible version 2.1

- Ansible 2.1.0

Example Playbook
----------------

The following example will use the arista.eos-bridging role to completely setup
switchports and vlans a leaf switch without writing any tasks. We'll create a
``hosts`` file with our switch, then a corresponding ``host_vars`` file and
then a simple playbook which only references the bridging role. By including
the role we automatically get access to all of the tasks to configure bridging
features. What's nice about this is that if you have a host without bridging
configuration, the tasks will be skipped without any issue.


Sample hosts file:

    [leafs]
    leaf1.example.com

Sample host_vars/leaf1.example.com

    provider:
      host: "{{ inventory_hostname }}"
      username: admin
      password: admin
      use_ssl: no
      authorize: yes
      transport: cli

    vlans:
      - vlanid: 1
        name: default
      - vlanid: 2
        name: production

    eos_purge_vlans: false

    switchports:
      - name: Ethernet1
        mode: access
        access_vlan: 400
      - name: Ethernet2
        mode: trunk
        trunk_native_vlan: 20
        trunk_allowed_vlans:
          - 100
          - 101
          - 200
          - 201
        trunk_groups:
          - peering1
          - peering2

A simple playbook to configure bridging, leaf.yml

    - hosts: leafs
      roles:
         - arista.eos-bridging

Then run with:

    ansible-playbook -i hosts leaf.yml
​    


Developer Information
------------

Development contributions are welcome. Please see *Arista Roles for Ansible - Development Guidelines* ([test/arista-ansible-role-test/README](test/arista-ansible-role-test/README.md)) for additional information, including how to develop and run test cases for role development.




License
-------

Copyright (c) 2015, Arista Networks EOS+
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of Arista nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


Author Information
------------------

Please raise any issues using our GitHub repo or email us at ansible-dev@arista.com
