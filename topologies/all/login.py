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
previous_menu = ''

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
    global previous_menu
    os.system("clear")
    # Create Device Dict to save devices and later execute based on matching the counter to a dict key
    device_dict = {}

    # Sort veos instances
    veos_info_sorted = sort_veos(veos_info)
    print("\n\n*****************************************")
    print("*****Jump Host for Arista Test Drive*****")
    print("*****************************************")
    print("\n\n==========Device SSH Menu==========\n")
    print("Screen Instructions:\n")

    print("* Select specific screen - Ctrl + a <number>")
    print("* Select previous screen - Ctrl + a p")
    print("* Select next screen - Ctrl + a n")
    print("* Exit all screens (return to menu) - Ctrl + a \\")

    print("\nPlease select from the following options:")

    counter = 1
    for veos in veos_info_sorted:
        print("{0}. {1} ({2})".format(str(counter),veos['hostname'],veos['hostname']))
        device_dict[counter] = veos['ip']
        device_dict[veos['hostname']] = veos['ip']
        counter += 1

    print("97. Screen (screen) - Opens a screen session to each of the hosts")
    print("98. Shell (shell/bash)")
    print("99. Back to Main Menu (back/exit) - CTRL + c")
    print("")
    user_input = input("What would you like to do? ")

    # Check to see if input is in device_dict
    counter = 1
    try:
      if user_input.lower() in device_dict:
          previous_menu = menu_mode
          os.system('ssh ' + device_dict[user_input])
      elif user_input.lower() == 'screen':
          os.system('/usr/bin/screen')
      elif user_input.lower() == 'bash' or user_input.lower() == 'shell':
          os.system('/bin/bash')
      elif user_input.lower() == 'back' or user_input.lower() == 'exit':
          menu_mode = previous_menu
      else:
          print("Invalid Input")
    except:
      print("Invalid Input")



def lab_options_menu():
    global menu_mode
    global previous_menu

    os.system("clear")
    print("\n\n*****************************************")
    print("*****Jump Host for Arista Test Drive*****")
    print("*****************************************")

    if menu_mode == 'LAB_OPTIONS':
      # Get Yaml Files in /home/arista/menus
      menu_files = os.listdir('/home/arista/menus')
      menu_files.sort()
      
    # Create Lab Options dict to save lab and later navigate to that menu of labs
      lab_options_dict = {}

      # Display Lab Options
      counter = 1
      print('\n==========Lab Options Menu==========\n')
      print("Please select from the following options: \n")
      
      # Iterate through lab menu files and print names without .yaml - Increment counter to reflect choices
      counter = 1
      for menu_type in menu_files:
          # Print Lab Menu and add options to lab options dict
          print('{0}. {1}'.format(str(counter),menu_type.replace('-', ' ').replace('.yaml', '')))
          lab_options_dict[str(counter)] = menu_type
          lab_options_dict[menu_type.replace('.yaml', '')] = menu_type
          counter += 1

      # Additional Menu Options
      print("\nOther Options: ")
      print("98. SSH to Devices (ssh)")
      print("99. Back to Main Menu (back/exit) - CTRL + c\n")
      
      user_input = input("\nWhat would you like to do?: ")

      # Check to see if digit is in lab_options dict
      try:
          if user_input.lower() in lab_options_dict:
              previous_menu = menu_mode
              menu_mode = 'LAB_' + lab_options_dict[user_input]
          elif user_input == '98' or user_input.lower() == 'ssh':
              previous_menu = menu_mode
              menu_mode = 'DEVICE_SSH'
          elif user_input.lower() == 'back' or user_input.lower() == 'exit':
              menu_mode = previous_menu
          else:
              print("Invalid Input")
      except:
        print("Invalid Input")



    elif 'LAB_' in menu_mode and menu_mode != 'LAB_OPTIONS':
      
      # Create Commands dict to save commands and later execute based on matching the counter to a dict key
      commands_dict = {}

      # Open yaml for the lab option (minus 'LAB_' from menu mode) and load the variables
      menu_file = open('/home/arista/menus/' + menu_mode[4:])
      menu_info = YAML().load(menu_file)
      menu_file.close()

      
      counter = 1
      for lab in menu_info['lab_list']:
        print("{0}. {1}".format(str(counter),menu_info['lab_list'][lab][0]['description']))
        commands_dict[str(counter)] = menu_info['lab_list'][lab][0]['command']
        commands_dict[lab] = menu_info['lab_list'][lab][0]['command']
        counter += 1
      print('\n')

      # Additional Menu Options
      print("Other Options: ")
      print("97. Back to Lab Options Menu (back/exit)")
      print("98. SSH to Devices (ssh)")
      print("99. Back to Main Menu (main) - CTRL + c\n")

      # User Input
      user_input = input("What would you like to do?: ")

      # Check to see if input is in commands_dict
      try:
          if user_input.lower() in commands_dict:
              previous_menu = menu_mode
              os.system(commands_dict[user_input])
          elif user_input.lower() == 'back' or user_input.lower() == 'exit':
              menu_mode = previous_menu
          elif user_input == '98' or user_input.lower() == 'ssh':
              previous_menu = menu_mode
              menu_mode = 'DEVICE_SSH'
          elif user_input == '99' or user_input.lower() == 'main':
              menu_mode = "MAIN"
          else:
              print("Invalid Input")
      except:
        print("Invalid Input")

def main_menu():
    global menu_mode
    os.system("clear")
    print("\n\n*****************************************")
    print("*****Jump Host for Arista Test Drive*****")
    print("*****************************************")
    print("\n\n==========Main Menu==========\n")
    print("Please select from the following options: ")
    print("1. SSH to Devices (ssh)")
    print("2. Labs (labs)")
    print("99. Exit LabVM (quit/exit)- CTRL + c")
    print("")

    user_input = input("What would you like to do?: ")
    
    # Check user input to see which menu to change to
    if user_input == '1' or user_input.lower() == 'ssh':
      menu_mode = 'DEVICE_SSH'
    elif user_input == '2' or user_input.lower() == 'labs':
      menu_mode = 'LAB_OPTIONS'
    elif user_input == '99' or user_input.lower() == 'exit' or user_input.lower() == 'quit':
      print("\nUser exited.")
      quit()
    else:
      print("Invalid Input")



##############################################
#################### Main ####################
##############################################

def main():
    global menu_mode
    # Create Menu Manager
    while menu_mode:
      try:
        if menu_mode == 'MAIN':
          main_menu()
        elif menu_mode == 'DEVICE_SSH':
          device_menu()
        elif 'LAB_' in menu_mode:
          lab_options_menu()
      except KeyboardInterrupt:
        if menu_mode == 'MAIN':
          print('User exited.')
          quit()
        else:
          menu_mode = 'MAIN'
        


if __name__ == '__main__':
    main()