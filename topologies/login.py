#!/usr/bin/python
import os
import sys
import signal
import yaml
from itertools import izip_longest

f = open('access_info.yml')
accessinfo = yaml.safe_load(f)
f.close()

f = open('menuoptions.yaml')
menuoptions = yaml.safe_load(f)
f.close()

labcontrols = menuoptions['options']

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
      counter = counter + 1
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

    print "   99. Quit"
    print ""
    ans=raw_input("What would you like to do? ")
    devicecount = counter

    counter = 0
    for veos in veosinfo:
      counter = counter + 1
      if ans==str(counter) or ans==veos['hostname']:
        os.system("ssh "+veos['ip'])
        break
      elif ans=="99" or ans=="quit" or ans=="exit":
        quit()
      elif ans!="" and counter==devicecount:
        #print("\n Not Valid Choice Try again")
        break;

    counter2 = 20
    for labcontrol in labcontrols:
      optionValues = labcontrols[labcontrol][0]
      counter2 = counter2 + 1
      if ans==str(counter2) or ans==labcontrol:
        print optionValues['command']
        break
      elif ans > devicecount and ans < 20:
        print("\n Not Valid Choice Try again")
        break

else:
  os.system("/usr/lib/openssh/sftp-server")
