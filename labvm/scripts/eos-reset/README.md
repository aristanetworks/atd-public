## EOS-Reset

These set of scripts can be used from the ADC labvm/jumphost.  To run these scripts you will need to call the `reset-eos.sh` file.  When running as the `arista` user, you will need to enter the `sudo` password.  When prompted by the Ansible-Playbook for a `SSH password:` just hit `Enter` for an empty/blank password:

#### Example
Here is an example.  As a note, it is perfectly fine to see `fatal` messages in the `[Reboot the EOS Devices]` task.  It's fatal because the EOS device reboots and closes the ssh connection from the jumphost.  After the switch reboots, it will be accessible again.

```
arista@ip-10-33-7-9:~/scripts$ ./reset-eos.sh
STARTING
Getting EOS Underlay IPs
hosts file created
Getting base CVP Configlets for EOS devices

<----- OUTPUT OMITTED ------>


Configlets gathered
Starting Ansible Playbook
SSH password:

PLAY [all] ***********************************************************************************************************************************************************************************************************************************

TASK [Copy base Configs to EOS Devices] ******************************************************************************************************************************************************************************************************
ok: [leaf1]
ok: [spine1]
ok: [spine2]
ok: [leaf4]
ok: [cvx01]
ok: [leaf3]
ok: [leaf2]

TASK [Reboot the EOS Devices] ****************************************************************************************************************************************************************************************************************
fatal: [spine1]: UNREACHABLE! => {"changed": false, "msg": "Failed to connect to the host via ssh: Shared connection to 10.33.149.100 closed.\r\n", "unreachable": true}
fatal: [leaf1]: UNREACHABLE! => {"changed": false, "msg": "Failed to connect to the host via ssh: Shared connection to 10.33.145.151 closed.\r\n", "unreachable": true}
fatal: [leaf4]: UNREACHABLE! => {"changed": false, "msg": "Failed to connect to the host via ssh: Shared connection to 10.33.152.245 closed.\r\n", "unreachable": true}
fatal: [cvx01]: UNREACHABLE! => {"changed": false, "msg": "Failed to connect to the host via ssh: Shared connection to 10.33.144.14 closed.\r\n", "unreachable": true}
fatal: [spine2]: UNREACHABLE! => {"changed": false, "msg": "Failed to connect to the host via ssh: Shared connection to 10.33.156.240 closed.\r\n", "unreachable": true}
fatal: [leaf3]: UNREACHABLE! => {"changed": false, "msg": "Failed to connect to the host via ssh: Shared connection to 10.33.152.146 closed.\r\n", "unreachable": true}
fatal: [leaf2]: UNREACHABLE! => {"changed": false, "msg": "Failed to connect to the host via ssh: Shared connection to 10.33.156.94 closed.\r\n", "unreachable": true}

PLAY RECAP ***********************************************************************************************************************************************************************************************************************************
cvx01                      : ok=1    changed=0    unreachable=1    failed=0
leaf1                      : ok=1    changed=0    unreachable=1    failed=0
leaf2                      : ok=1    changed=0    unreachable=1    failed=0
leaf3                      : ok=1    changed=0    unreachable=1    failed=0
leaf4                      : ok=1    changed=0    unreachable=1    failed=0
spine1                     : ok=1    changed=0    unreachable=1    failed=0
spine2                     : ok=1    changed=0    unreachable=1    failed=0

Done!
```