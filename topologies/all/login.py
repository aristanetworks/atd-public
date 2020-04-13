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

# Set Main Script Variables
topology = access_info['topology']
login_info = access_info['login_info']
nodes = access_info['nodes']
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

def device_menu():
  global menu_mode

  veos_info_sorted = sort_veos(veos_info)

  print ("""
  \t==========Device SSH Menu==========
  \tScreen Instructions:

  \t* Select specific screen - Ctrl + a <number>
  \t* Select previous screen - Ctrl + a p
  \t* Select next screen - Ctrl + a n
  \t* Exit all screens (return to menu) - Ctrl + a \\

  \tPlease select from the following options:
  """

  counter = 0
  for veos in veos_info_sorted:
      counter += 1
      print("\t{0}. {1}".format(str(counter),veos['hostname']))


  print("  97. Screen (screen) - Opens a screen session to each of the hosts")
  print("  98. Shell (bash)")
  print("  99. Back to Main Menu (back)")
  print("")
  user_input = input("What would you like to do? ")

  # Set device_count to use for comparison on next iteration
  device_count = counter
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
          break
      elif user_input != "" and counter == device_count:
          #print("\n Not Valid Choice Try again")
          break
      # If entry is null or without mapping, do nothing (which will loop the menu)
      else:
          print("Invalid Entry.")
          break



def lab_options():
  # Open MenuOptions.yaml and load the variables
  f = open('/home/arista/MenuOptions.yaml')
  lab_options = YAML().load(f)
  f.close()

  counter = 0
  for option in lab_options:
    print(str(counter) + option)

def main_menu():
  global menu_mode
  print("*****Jump Host for Arista Demo Cloud*****\n")
  print("==========Main Menu==========: \n")
  print("Please select from the following options: ")
  print("1. SSH to Devices (ssh)")
  print("99. Exit LabVM (quit/exit)")
  print("")

  user_input = input("What would you like to do?: ")
  
  # Check user input to see which menu to change to
  if user_input == '1' or user_input.lower() == 'ssh':
    menu_mode = 'DEVICE_SSH'
  elif user_input == '99' or user_input.lower() == 'exit' or user_input.lower() == 'quit':
    print("User exited.")
    quit()
  else:
    print("Invalid Input")



##############################################
#################### Main ####################
##############################################

def main():


    # Create Menu Manager
    while menu_mode:
      if menu_mode == 'MAIN':
        main_menu()
      elif menu_mode == 'DEVICE_SSH':
        device_menu()


if __name__ == '__main__':
    main()