If a device is no longer reachable/accessible after making changes to the device.
For example, accidentally removing the mamagement IP address, removing the 'arista'
user, modifying the original configlet, etc.

The device(s) and CVP configlets can be restored back to their original state.
To bring devices back, enter the following command from bash:

To restore only the spine1 vEos device:
eos-reset.py -d spine1 

To restore spine1, leaf1 and cvx01 devices enter:
eos-reset.py -d spine1 leaf1 cvx01

To restore all devices:
eos-reset.py -d all
