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

    print("\n\n==========Device SSH Menu==========\n")
    print("Screen Instructions:\n")

    print("* Select specific screen - Ctrl + a <number>")
    print("* Select previous screen - Ctrl + a p")
    print("* Select next screen - Ctrl + a n")
    print("* Exit all screens (return to menu) - Ctrl + a \\")

    print("\nPlease select from the following options:")

    counter = 0
    for veos in veos_info_sorted:
        counter += 1
        print("{0}. {1}".format(str(counter),veos['hostname']))


    print("97. Screen (screen) - Opens a screen session to each of the hosts")
    print("98. Shell (bash)")
    print("99. Back to Main Menu (back/exit)")
    print("")
    user_input = input("What would you like to do? ")

    # Set device_count to use for comparison on next iteration
    device_count = counter
    counter = 0
    for veos in veos_info_sorted:
        counter += 1
        if user_input == str(counter) or user_input.lower() == veos['hostname']:
            os.system("ssh "+veos['ip'])
        elif user_input == "97" or user_input.lower() == "screen":
            os.system('/usr/bin/screen')
        elif user_input == "98" or user_input.lower() == "bash" or user_input.lower() == "shell":
            os.system("/bin/bash")
        elif user_input == "99" or user_input.lower() == "back" or user_input.lower() == 'exit':
            menu_mode = "MAIN"
        elif user_input != "" and counter == device_count:
            print("\n Not Valid Choice Try again")
        # If entry is null or without mapping, do nothing (which will loop the menu)
        else:
            print("Invalid Entry.")



def lab_options_menu():
    global menu_mode
    # Open MenuOptions.yaml and load the variables
    f = open('/home/arista/menus/LabOptions.yaml')
    lab_options = YAML().load(f)
    f.close()
    
    # Display Lab Options
    counter = 1
    print('==========Lab Options Menu==========\n')
    print("Please select from the following options: ")
    # Iterate through lab types and pring descriptions. Increment counter to reflect choices
    for lab_type in lab_options['lab_list']:
        print(lab_type.replace('-', ' ') + ":")
        for lab in lab_options['lab_list'][lab_type]['options']:
          print("{0}. {1}".format(str(counter),lab_options['lab_list'][lab_type]['options'][lab][0][0]))
          counter += 1

    # Additional Menu Options
    print("99. Back to Main Menu (back/exit)")

    # User Input
    user_input = input("What would you like to do?: ")

    # Check to see if input is digit, if it is, check to see if it is in range of the counter
    try:
        if user_input.isdigit():
            if user_input in range(1, counter):
              print(user_input)
            elif user_input == '99':
              menu_mode = "MAIN"
            else:
              print("Invalid Input")
        elif user_input.lower() == 'back' or user_input.lower() == 'exit':
            menu_mode = "MAIN"
        else:
            print("Invalid Input")
    except:
      print("Invalid Input")

def main_menu():
    global menu_mode
    print("\n\n*****************************************")
    print("*****Jump Host for Arista Demo Cloud*****")
    print("*****************************************")
    print("\n\n==========Main Menu==========:\n")
    print("Please select from the following options: ")
    print("1. SSH to Devices (ssh)")
    print("2. Labs")
    print("99. Exit LabVM (quit/exit)")
    print("")

    user_input = input("What would you like to do?: ")
    
    # Check user input to see which menu to change to
    if user_input == '1' or user_input.lower() == 'ssh':
      menu_mode = 'DEVICE_SSH'
    elif user_input == '2' or user_input.lower() == 'labs':
      menu_mode = 'LAB_OPTIONS'
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
        elif menu_mode == 'LAB_OPTIONS':
          lab_options_menu()


if __name__ == '__main__':
    main()