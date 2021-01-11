from cvplibrary import CVPGlobalVariables, GlobalVariableNames, Form



# Get this devices Serial 


serial = CVPGlobalVariables.getValue( GlobalVariableNames.CVP_SERIAL )
mask = '24'
ServiceRouting = True

#Create the IP address from the serial number

IPaddress = '192.168.0.66'

if serial == '9BD9FE8B8A0EB6F43910F5F583A9CF40':
 IPaddress = '192.168.0.21'
 hostname = 'leaf1'


elif serial == '8823F318C30617010F15E56A40D3AE14':
 IPaddress = '192.168.0.22'
 hostname = 'leaf2'


elif serial == '5356CC64EE6812A82D43E42F3BC0F3C5':
 IPaddress = '192.168.0.23'
 hostname = 'leaf4'


elif serial == '04DADEBA6B3D1548218141BC827D02A5':
 IPaddress = '192.168.0.24'
 hostname = 'leaf3'

elif serial == '329874C0FD77D12A30D571B6B79E9195':
 IPaddress = '192.168.0.11'
 hostname = 'spine1'

elif serial == '4B49885915FFE471AB899ACDEE5B803D':
 IPaddress = '192.168.0.12'
 hostname = 'spine2'


elif serial == 'FF5D15D80D0D3E6B8D1D060DE545627D':
 IPaddress = '192.168.0.51'
 ServiceRouting = False
 hostname = 'host1'


elif serial == '94910C4142FA2F7B76DFEC1D3C761E28':
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