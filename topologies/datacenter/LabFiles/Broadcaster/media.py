#!/usr/bin/python
import os
import sys
import signal
import requests

from requests.packages.urllib3.exceptions import InsecureRequestWarning

def check_for_first_login():
    '''simply need to login once to get around Folsom bugs'''
    CHECK_FILE = '/home/arista/.CVP_LOGIN_SUCCESS'

    if not os.path.isfile(CHECK_FILE):
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        r = requests.post('https://192.168.0.5/cvpservice/login/authenticate.do',json={"userId": "cvpadmin","password": "arista"}, verify=False)
        if r.status_code == 200:
            open(CHECK_FILE, 'a').close()

if sys.stdout.isatty():

  def signal_handler(signal, frame):
    print("\n")
    quit()

  signal.signal(signal.SIGINT, signal_handler)


  ans=True
  while ans:
    check_for_first_login()
    print ("""
Lab jump host for Arista virtual lab

Screen Instructions:

   * Select specific screen - Ctrl + a <number>
   * Select previous screen - Ctrl + a p
   * Select next screen - Ctrl + a n
   * Exit all screens (return to menu) - Ctrl + a \\

Device Menu:            Lab Controls

   1. Spine1              13. Return to previous menu (return)
   2. Spine2
   3. Leaf1               The following options will configure all devices in the lab except leaf4
   4. Leaf2  (not used)   14. Media - IP Intro (media-intro)
   5. Leaf3  (not used)   15. Media - VLAN STP (media-vlan)
   6. Leaf4               16. Media - OSPF (media-ospf)
   7. Host1               17. Media - BGP  (media-bgp)
   8. Host2               18. Media - Multicast (multicast)
   9. Screen (screen)     19.
   10. Shell (bash)       20.
   11. Reset All Devices to Base (reset)
   12. Exit/Quit & return to main menu (exit)
    """)
    ans=raw_input("What would you like to do? ")
    if ans=="1" or ans=="spine1":
      os.system('ssh 192.168.0.10')
    elif ans=="2" or ans=="spine2":
      os.system('ssh 192.168.0.11')
    elif ans=="3" or ans=="leaf1":
      os.system('ssh 192.168.0.14')
    elif ans=="4" or ans=="leaf2":
      os.system('ssh 192.168.0.15')
    elif ans=="5" or ans=="leaf3":
      os.system('ssh 192.168.0.16')
    elif ans=="6" or ans=="leaf4":
      os.system('ssh 192.168.0.17')
    elif ans=="7" or ans=="host1":
      os.system('ssh 192.168.0.31')
    elif ans=="8" or ans=="host2":
      os.system('ssh 192.168.0.32')
    elif ans=="9" or ans=="screen":
      os.system('/usr/bin/screen')
    elif ans=="10" or ans=="bash":
      os.system('/bin/bash')
    elif ans=="11" or ans=="reset":
      os.system("ssh 192.168.0.5 './ConfigureTopology.py'")
      os.system("bash /home/arista/pushHostMediaConfig.sh")
    elif ans=="12":
      quit()
    elif ans=="13" or ans=="return":
      quit()
    elif ans=="14" or ans=="media-intro":
      os.system("ssh 192.168.0.5 './ConfigureTopology.py -t media-intro' >> /tmp/ConfigureTopology.log")
    elif ans=="15" or ans=="media-vlan":
      os.system("ssh 192.168.0.5 './ConfigureTopology.py -t media-vlan' >> /tmp/ConfigureTopology.log")
    elif ans=="16" or ans=="media-ospf":
      os.system("ssh 192.168.0.5 './ConfigureTopology.py -t media-ospf' >> /tmp/ConfigureTopology.log")
    elif ans=="17" or ans=="media-bgp":
      os.system("ssh 192.168.0.5 './ConfigureTopology.py -t media-bgp' >> /tmp/ConfigureTopology.log")
    elif ans=="18" or ans=="multicast":
      os.system("ssh 192.168.0.5 './ConfigureTopology.py -t multicast' >> /tmp/ConfigureTopology.log")
    elif ans=="19" or ans=="":
      print("\n Lab not available")
    elif ans=="20" or ans=="":
      print("\n Lab not available")
    elif ans=="exit":
      quit()
    elif ans !="":
      print("\n Not Valid Choice Try again")
else:
  os.system("/usr/lib/openssh/sftp-server")