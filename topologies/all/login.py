#!/usr/bin/python
import os
import sys
import signal
import re
from ruamel.yaml import YAML
from itertools import izip_longest

def atoi(text):
  return int(text) if text.isdigit() else text

def natural_keys(text):
  return [ atoi(c) for c in re.split(r'(\d+)', text) ]
  
def sortVEOS(vd):
  tmp_l = []
  tmp_d = {}
  fin_l = []
  for tveos in vd:
    tmp_l.append(tveos['hostname'])
    tmp_d[tveos['hostname']] = tveos
  tmp_l.sort(key=natural_keys)
  # If cvx in list, move to end
  if 'cvx' in tmp_l[0]:
        tmp_cvx = tmp_l[0]
        tmp_l.pop(0)
        tmp_l.append(tmp_cvx)
  for tveos in tmp_l:
    fin_l.append(tmp_d[tveos])
  return(fin_l)

f = open('/etc/ACCESS_INFO.yaml')
accessinfo = YAML().load(f)
f.close()

f = open('/home/arista/MenuOptions.yaml')
menuoptions = YAML().load(f)
f.close()

# Check to see if we need the media menu
enableControls2 = False
try:
  with open("/home/arista/enable-media", 'r') as fh:
    enableControls2 = True
except:
  enableControls2 = False

topology = accessinfo['topology']

login = accessinfo['login_info']
nodes = accessinfo['nodes']
tag = accessinfo['tag']

cvplogin = login['cvp']
veoslogin = login['veos'][0]

cvpguilogin = cvplogin['gui'][0]
cvpguiuser = cvpguilogin['user']
cvpguipass = cvpguilogin['pw']

veosuser = veoslogin['user']
veospass = veoslogin['pw']

cvpinfo = nodes['cvp'][0]
cvp = cvpinfo['ip']

veosinfo = nodes['veos']

labcontrols = menuoptions['options']
# Check to see if this is the datacenter topo
if topology == 'datacenter':
  labcontrols2 = menuoptions['media-options']
else:
  # If topo other than datacenter, set to False
  labcontrols2 = False
  # Sort the list naturally
  veosinfo = sortVEOS(veosinfo)

if sys.stdout.isatty():

  def signal_handler(signal, frame):
    print("\n")
    quit()

  signal.signal(signal.SIGINT, signal_handler)


  ans=True
  while ans:
    print ("""
Jump Host for Arista Demo Cloud

Screen Instructions:

   * Select specific screen - Ctrl + a <number>
   * Select previous screen - Ctrl + a p
   * Select next screen - Ctrl + a n
   * Exit all screens (return to menu) - Ctrl + a \\

Device Menu:            Lab Controls
   
    """)

    counter = 0
    for veos,labcontrol in izip_longest(veosinfo,labcontrols):
      counter += 1
      sys.stdout.write("   ")
      sys.stdout.write(str(counter))
      sys.stdout.write(". ")
      sys.stdout.write(veos['hostname'])

      if labcontrol != None:
         sys.stdout.write("\t\t  ")
         sys.stdout.write(str(counter+20))
         sys.stdout.write(". ")
         optionValues = labcontrols[labcontrol][0]
         sys.stdout.write(optionValues['description'])

      sys.stdout.write("\n")
    
    devicecount = counter

    if enableControls2 and labcontrols2 != None:
      #sys.stdout.write("\n")
      counter = 0
      sys.stdout.write("\n")
      sys.stdout.write("  Media Controls")
      for labcontrol2 in labcontrols2:
         counter += 1
         sys.stdout.write("\n")
         sys.stdout.write("  ")
         sys.stdout.write(str(counter+10))
         sys.stdout.write(". ")
         optionValues = labcontrols2[labcontrol2][0]
         sys.stdout.write(optionValues['description'])
      sys.stdout.write("\n")
      sys.stdout.write("\n")

    print "  97. Screen (screen)"
    print "  98. Shell (bash)"
    print "  99. Quit (quit/exit)"
    print ""
    ans=raw_input("What would you like to do? ")

    counter = 0
    for veos in veosinfo:
      counter += 1
      if ans==str(counter) or ans==veos['hostname']:
        os.system("ssh "+veos['ip'])
        break
      elif ans=="97" or ans=="screen":
        os.system('/usr/bin/screen')
        break
      elif ans=="98" or ans=="bash" or ans=="shell":
        os.system("/bin/bash")
        break
      elif ans=="99" or ans=="quit" or ans=="exit":
        quit()
      elif ans!="" and counter==devicecount:
        #print("\n Not Valid Choice Try again")
        break

    counter2 = 20
    for labcontrol in labcontrols:
      optionValues = labcontrols[labcontrol][0]
      counter2 += 1
      if ans==str(counter2) or ans==labcontrol:
        os.system(optionValues['command'])
        break
      elif ans > devicecount and ans < 20:
        print("\n Not Valid Choice Try again")
        break

    if enableControls2:
      counter3 = 10
      for labcontrol2 in labcontrols2:
        optionValues = labcontrols2[labcontrol2][0]
        counter3 += 1
        if ans==str(counter3) or ans==labcontrol2:
          os.system(optionValues['command'])
          break
        elif ans > devicecount and ans < 10:
          print("\n Not Valid Choice Try again")
          break

else:
  os.system("/usr/lib/openssh/sftp-server")
