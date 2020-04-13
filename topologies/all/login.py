#!/usr/bin/python3
import os
import sys
import signal
import re
from ruamel.yaml import YAML
from itertools import zip_longest


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

# Set default menu mode
menu_mode = 'MAIN'

###################################################
#################### Functions ####################
###################################################

def text_to_int(text):
  return int(text) if text.isdigit() else text

def signal_handler(signal, frame):
    print("\n")
    quit()

def natural_keys(text):
  return [ text_to_int(char) for char in re.split(r'(\d+)', text) ]

def sort_veos(vd):
  tmp_l = []
  tmp_d = {}
  fin_l = []
  for t_veos in vd:
    tmp_l.append(t_veos['hostname'])
    tmp_d[t_veos['hostname']] = t_veos
  tmp_l.sort(key=natural_keys)
  # If cvx in list, move to end
  if 'cvx' in tmp_l[0]:
        tmp_cvx = tmp_l[0]
        tmp_l.pop(0)
        tmp_l.append(tmp_cvx)
  for t_veos in tmp_l:
    fin_l.append(tmp_d[t_veos])
  return(fin_l)

def device_menu(veos_info_sorted,lab_controls,enable_controls2,lab_controls2):
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
  for veos,lab_control in zip_longest(veos_info_sorted,lab_controls):
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

      device_count = counter

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
  print("  99. Back to Main Menu (back)")
  print("")
  user_input = input("What would you like to do? ")

  counter = 0
  for veos in veos_info_sorted:
      counter += 1
      if user_input == str(counter) or user_input == veos['hostname']:
          os.system("ssh "+veos['ip'])
          break
      elif user_input == "97" or user_input == "screen":
          os.system('/usr/bin/screen')
          break
      elif user_input == "98" or user_input == "bash" or user_input == "shell":
          os.system("/bin/bash")
          break
      elif user_input == "99" or user_input == "back":
          menu_mode = "MAIN"
      elif user_input != "" and counter == device_count:
          #print("\n Not Valid Choice Try again")
          break
      # If entry is null or without mapping, do nothing (which will loop the menu)
      else:
          print("Invalid Entry.")
          break

  counter2 = 20
  for lab_control in lab_controls:
      optionValues = lab_controls[lab_control][0]
      counter2 += 1
      if user_input == str(counter2) or user_input == lab_control:
          os.system(optionValues['command'])
          break
      elif user_input > device_count and user_input < 20:
          print("\n Not Valid Choice Try again")
          break

  if enable_controls2:
      counter3 = 10
      for lab_control2 in lab_controls2:
          option_values = lab_controls2[lab_control2][0]
          counter3 += 1
          if user_input == str(counter3) or user_input == lab_control2:
              os.system(option_values['command'])
              break
          elif user_input > device_count and user_input < 10:
              print("\n Not Valid Choice Try again")
              break

def main_menu():
  print("Main Menu: \n")
  print("1. SSH to Devices (ssh)")
  print("99. Exit LabVM (quit/exit)")
  print("")

  user_input = input("What would you like to do?: ")
  
  # Check user input to see which menu to change to
  if user_input == '1' or user_input.lower() == 'ssh':
    menu_mode = 'DEVICE_SSH'
    print(menu_mode)
  elif user_input == '99' or user_input.lower() == 'exit' or user_input.lower() == 'quit':
    print("User exited.")
    quit()
  else:
    print("Invalid Input")



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
        veos_info_sorted = sort_veos(veos_info)

    if sys.stdout.isatty():

        signal.signal(signal.SIGINT, signal_handler)

        # Create Menu Manager
        while menu_mode:
          if menu_mode == 'MAIN':
            main_menu()
          elif menu_mode == 'DEVICE_SSH':
            print('device_menu')
            device_menu(veos_info_sorted,lab_controls,enable_controls2,lab_controls2)
            
        else:
            os.system("/usr/lib/openssh/sftp-server")

if __name__ == '__main__':
    main()