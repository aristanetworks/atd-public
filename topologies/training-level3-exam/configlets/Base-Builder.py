from cvplibrary import CVPGlobalVariables, GlobalVariableNames, Form



# Get this devices Serial


serial = CVPGlobalVariables.getValue( GlobalVariableNames.CVP_SERIAL )
mask = '24'
ServiceRouting = True

#Create the IP address from the serial number


if serial == '4A7F6E96300132903A73A74CCF18B697':
 IPaddress = '192.168.0.21'
 hostname = 'leaf1'


elif serial == '3831DEFC364900BF9EEFC45FEE7794E7':
 IPaddress = '192.168.0.22'
 hostname = 'leaf2'


elif serial == 'ED469CFA13C4017B2D19BF7EBCAD50B1':
 IPaddress = '192.168.0.23'
 hostname = 'leaf3'


elif serial == '434653268ABA082A2FF6B52F1367CE80':
 IPaddress = '192.168.0.24'
 hostname = 'leaf4'

elif serial == '8085B9640BC6D8FDC1FD23D242EBF433':
 IPaddress = '192.168.0.11'
 hostname = 'spine1'

elif serial == 'D28D62E5729AB8BF44A0BC017DEB188A':
 IPaddress = '192.168.0.12'
 hostname = 'spine2'

elif serial == 'F77703A62ADE220E689A41057AA56288':
 IPaddress = '192.168.0.13'
 hostname = 'spine3'

elif serial == 'D763323F00C03738A8C824D2F1DA05E8':
 IPaddress = '192.168.0.25'
 hostname = 'borderleaf1'

elif serial == '7C16136B7483F2E2FB002E8E0646F1F0':
 IPaddress = '192.168.0.26'
 hostname = 'borderleaf2'

elif serial == '86342B780ED73BCB30E1DFE48E26AC38':
 IPaddress = '192.168.0.51'
 ServiceRouting = False
 hostname = 'host1'


elif serial == 'CE0B31805130945E3CE40B060E9E636D':
 IPaddress = '192.168.0.52'
 ServiceRouting = False
 hostname = 'host2'


# Generate and print config - Ignore the service routing command if not needed
print 'hostname %s' % hostname
print '!'
print 'interface Management 1'
print '  ip address %s/%s' % ( IPaddress, mask )
print '  no lldp transmit'
print '  no lldp receive'
print '!'
if ServiceRouting:
 print 'service routing protocols model multi-agent'
 print '!'
print 'dns domain arista.lab'
print '!'
print 'ip route 0.0.0.0/0 192.168.0.1'
print '!'
print 'ip routing'
print '!'
print 'management api http-commands'
print '  no shutdown'
print '  protocol http'
print '!'