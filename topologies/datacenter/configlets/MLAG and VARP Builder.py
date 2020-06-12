import sys, jsonrpclib
sys.path.append('/usr/lib64/python2.7/site-packages/')
import yaml
from cvplibrary import CVPGlobalVariables as cvpGV
from cvplibrary import GlobalVariableNames as GVN

def sendCmd(commands):
  ztp = cvpGV.getValue(GVN.ZTP_STATE)
  hostip = cvpGV.getValue(GVN.CVP_IP)
  if ztp == 'true':
    user = cvpGV.getValue(GVN.ZTP_USERNAME)
    passwd = cvpGV.getValue(GVN.ZTP_PASSWORD)
  else:
    user = cvpGV.getValue(GVN.CVP_USERNAME)
    passwd = cvpGV.getValue(GVN.CVP_PASSWORD)
    
  url = "https://%s:%s@%s/command-api" % (user, passwd, hostip)
  switch = jsonrpclib.Server(url)
  response = switch.runCmds(1, commands)[0]
  return response

hostname = sendCmd(['show hostname'])['hostname']
f = open('hostvars/%s.yml' % hostname )
info = yaml.load(f)

if 'mlag' not in info.keys():
  print ''
else:
  print 'vlan %s' % info['mlag']['peer_vlan']
  print '   name MLAGPeerLink'
  print '   trunk group mlagPeer'
  print '!'
  print 'no spanning-tree vlan %s' % info['mlag']['peer_vlan']
  print '!'
  for i in info['mlag']['peer_interfaces']:
    print 'interface %s' % i
    print '   channel-group %s mode active' % info['mlag']['peer_link'].replace('Port-Channel','')
    print '!'
    
  print 'interface %s' % info['mlag']['peer_link']
  print '   description MLAGPeerLink'
  print '   switchport mode trunk'
  print '   switchport trunk group mlagPeer'
  print '!'
  
  print 'interface Vlan%s' % info['mlag']['peer_vlan']
  print '   description MLAGPeerIP'
  print '   ip address %s/%s' % (info['mlag']['ip'], info['mlag']['cidr'])
  print '!'
  
  print 'mlag configuration'
  print '   domain %s' % info['mlag']['domain']
  print '   local-interface Vlan%s' % info['mlag']['peer_vlan']
  print '   peer-address %s' % info['mlag']['peer_ip']
  print '   peer-link %s' % info['mlag']['peer_link']
  print '!'
  
  for m in info['mlag']['mlags']:
    for i in m['interfaces']:
      print 'interface %s' % i
      print '   channel-group %s mode active' % m['mlag']
      print '!'
      print 'interface Port-Channel%s' % m['mlag']
      print '   mlag %s' % m['mlag']
      if m['trunk']:
        print '   switchport mode trunk'
      elif m['access']:
        print '   switchport mode access'
        print '   switchport access vlan %s' % m['vlan']
      print '!'

if 'mlag_svis' not in info.keys():
  print ''
else:
  varp = False    
  for s in info['mlag_svis']:
    print 'interface Vlan%s' % s['vlan']
    print '   description VLAN%sSVI' % s['vlan']
    print '   ip address %s/%s' % (s['ip'], s['cidr'])
    print '   no autostate'
    if s['varp']:
      varp = True
      print '   ip virtual-router address %s' % s['varp_ip']
    print '!'
  
  if varp:
    print 'ip virtual-router mac-address 00:1C:73:00:00:01'
    print '!'
    
