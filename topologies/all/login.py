#!/usr/bin/python3
import os
import sys
import signal
import re
from ruamel.yaml import YAML
from itertools import zip_longest
from ruamel.yaml import YAML

######################################
########## Global Variables ##########
######################################

# Open ACCESS_INFO.yaml and load the variables
f = open('/etc/ACCESS_INFO.yaml')
access_info = YAML().load(f)
f.close()

# Open MenuOptions.yaml and load the variables
f = open('/home/arista/MenuOptions.yaml')
menu_options = YAML().load(f)
f.close()

# Set Main Script Variables
topology = access_info['topology']
login_info = access_info['login_info']
nodes = access_info['nodes']
tag = access_info['tag']
cvp_login = login_info['cvp']
veos_login = login_info['veos'][0]
cvp_gui_login = cvp_login['gui'][0]
cvp_gui_user = cvp_gui_login['user']
cvp_gui_pass = cvp_gui_login['pw']
veos_user = veos_login['user']
veos_pass = veos_login['pw']
cvp_info = nodes['cvp'][0]
cvp = cvp_info['ip']
veos_info = nodes['veos']

###################################################
#################### Functions ####################
###################################################

def atoi(text):
  return int(text) if text.isdigit() else text

def signal_handler(signal, frame):
    print("\n")
    quit()

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


##############################################
#################### Main ####################
##############################################

def main():

    # Check to see if we need the media menu
    enable_controls2 = False
    try:
        with open("/home/arista/enable-media", 'r') as fh:
            enable_controls2 = True
    except:
        enable_controls2 = False

    # Check to see if we need the media menu
    enable_controls2 = False
    try:
        with open("/home/arista/enable-media", 'r') as fh:
            enable_controls2 = True
    except:
        enable_controls2 = False



    lab_controls = menu_options['options']
    # Check to see if this is the datacenter or datacenter-latest topo
    if 'datacenter' in topology:
        lab_controls2 = menu_options['media-options']
    else:
    # If topo other than datacenter, set to False
        lab_controls2 = False

    # Catch for routing and datacenter-latest topos to sort login menu naturally
    if topology != 'datacenter':
    # Sort the list naturally
        veosinfo = sortVEOS(veos_info)

    if sys.stdout.isatty():

        signal.signal(signal.SIGINT, signal_handler)

        ans = True
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
            for veos,lab_control in zip_longest(veosinfo,lab_controls):
                counter += 1
                sys.stdout.write("   ")
                sys.stdout.write(str(counter))
                sys.stdout.write(". ")
                sys.stdout.write(veos['hostname'])

                if lab_control != None:
                    sys.stdout.write("\t\t  ")
                    sys.stdout.write(str(counter+20))
                    sys.stdout.write(". ")
                    optionValues = lab_controls[lab_control][0]
                    sys.stdout.write(optionValues['description'])

                sys.stdout.write("\n")

                devicecount = counter

            if enable_controls2 and lab_controls2 != None:
                #sys.stdout.write("\n")
                counter = 0
                sys.stdout.write("\n")
                sys.stdout.write("  Media Controls")
                for lab_control2 in lab_controls2:
                    counter += 1
                    sys.stdout.write("\n")
                    sys.stdout.write("  ")
                    sys.stdout.write(str(counter+10))
                    sys.stdout.write(". ")
                    optionValues = lab_controls2[lab_control2][0]
                    sys.stdout.write(optionValues['description'])
                sys.stdout.write("\n")
                sys.stdout.write("\n")

            print("  97. Screen (screen) - Opens a screen session to each of the hosts")
            print("  98. Shell (bash)")
            print("  99. Quit (quit/exit)")
            print("")
            ans = input("What would you like to do? ")

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
                # If entry is null, set 'ans' back to True to loop back to start.
                elif ans == "":
                    ans = True
                    break

            counter2 = 20
            for lab_control in lab_controls:
                optionValues = lab_controls[lab_control][0]
                counter2 += 1
                if ans==str(counter2) or ans==lab_control:
                    os.system(optionValues['command'])
                    break
                elif ans > devicecount and ans < 20:
                    print("\n Not Valid Choice Try again")
                    break

            if enable_controls2:
                counter3 = 10
                for lab_control2 in lab_controls2:
                    optionValues = lab_controls2[lab_control2][0]
                    counter3 += 1
                    if ans==str(counter3) or ans==lab_control2:
                        os.system(optionValues['command'])
                        break
                    elif ans > devicecount and ans < 10:
                        print("\n Not Valid Choice Try again")
                        break

        else:
            os.system("/usr/lib/openssh/sftp-server")

if __name__ == '__main__':
    main()