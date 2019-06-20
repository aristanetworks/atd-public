If a device is no longer reachable/accessible after making changes to the device.
For example, accidentally removing the mamagement IP address, removing the 'arista'
user, modifying the original configlet, etc.

The device(s) and CVP configlets can be restored back to their original state.
To bring devices back, enter the following command from bash:

To restore only the eos1 vEos device:
eos-reset.py -d eos1 

To restore eos1, eos5 and eos15 devices enter:
eos-reset.py -d eos1 eos5 eos15

To restore all devices:
eos-reset.py -d all
