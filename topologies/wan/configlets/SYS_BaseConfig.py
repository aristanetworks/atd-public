import urllib2, json, jsonrpclib, ssl
from cvplibrary import CVPGlobalVariables, GlobalVariableNames

# Get this devices MAC address
mac = CVPGlobalVariables.getValue( GlobalVariableNames.CVP_MAC )
ztp = CVPGlobalVariables.getValue( GlobalVariableNames.ZTP_STATE )
hostip = CVPGlobalVariables.getValue( GlobalVariableNames.CVP_IP )

if ztp == 'true':
  user = CVPGlobalVariables.getValue( GlobalVariableNames.ZTP_USERNAME )
  passwd = CVPGlobalVariables.getValue( GlobalVariableNames.ZTP_PASSWORD )
else:
  user = CVPGlobalVariables.getValue( GlobalVariableNames.CVP_USERNAME )
  passwd = CVPGlobalVariables.getValue( GlobalVariableNames.CVP_PASSWORD )
  
# setup context to disable SSL verification
# Request to send to IPAM for Ma1 address
url = "http://192.168.0.4/ipam/arista/mgmtbymac.php?mac=%s" % mac
response = urllib2.urlopen(url)
hostjson = json.loads(response.read())



# Process JSON from IPAM for some reason cvx doesn't appear to be in json
if mac == '2c:c2:60:5c:a3:5e':
  hostname = "cvx01"
  ip = "192.168.0.44"
  mask = 24
else:  
  host = hostjson['host']
  hostname = host['hostname']
  ip = host['ip']
  mask = host['mask']

# Generate and print config
print 'hostname %s' % hostname
print '!'

print 'interface Management 1'
print '   ip address %s/%s' % ( ip, mask )
print '   no lldp transmit'
print '   no lldp receive'
print '!'
print 'ip domain-name arista.test'
print '!'
print 'ip route 0.0.0.0/0 192.168.0.254'
print '!'
print 'ip routing'
print '!'
print 'management api http-commands'
print '   no shutdown'
print '   protocol http'
print '!'