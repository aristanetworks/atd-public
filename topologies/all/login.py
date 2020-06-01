#!/usr/bin/python3
import os
import sys
import signal
import re
from ruamel.yaml import YAML
import json
from datetime import timedelta, datetime, timezone, date
import getopt
from rcvpapi.rcvpapi import *
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import logging
import time



######################################
########## Global Variables ##########
######################################
DEBUG = False

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

def remove_configlets( client, device, lab_configlets):
    """
    Removes all configlets except the ones defined here or starting with SYS_
    Define base configlets that are to be untouched
    mext = lab type to keep track of which base configlets to keep.  Added for RATD and RATD-Ring
    """
    base_configlets = ['ATD-INFRA']
    
    configlets_to_remove = []
    configlets_to_remain = base_configlets

    configlets = client.getConfigletsByNetElementId(device)
    for configlet in configlets['configletList']:
        if configlet['name'] not in base_configlets or configlet['name'] not in lab_configlets:
            configlets_to_remove.append(configlet['name'])
            send_to_syslog("INFO", "Configlet {0} not part of base on {1} - Removing from device".format(configlet['name'], device.hostname))
        elif configlet['name'] in base_configlets:
            configlets_to_remain.append(configlet['name'])
            send_to_syslog("INFO", "Configlet {0} is part of the base on {1} - Configlet will remain.".format(configlet['name'], device.hostname))
        else:
            pass
    device.removeConfiglets(client, configlets_to_remove)
    client.addDeviceConfiglets(device, configlets_to_remain)
    client.applyConfiglets(device)

def get_device_info( client):
    eos_devices = []
    for dev in client.inventory:
        tmp_eos = client.inventory[dev]
        tmp_eos_sw = CVPSWITCH(dev, tmp_eos['ipAddress'])
        tmp_eos_sw.updateDevice(client)
        eos_devices.append(tmp_eos_sw)
    return(eos_devices)


def update_topology(client, lab, configlets):
    # Get all the devices in CVP
    devices = get_device_info(client)
    # Loop through all devices
    # for device in devices:
    for device in devices:
        # Get the actual name of the device
        device_name = device.hostname
        
        # Define a list of configlets built off of the lab yaml file
        lab_configlets = []
        for configlet_name in configlets[lab][device_name]:
            lab_configlets.append(configlet_name)

        # Remove unnecessary configlets
        remove_configlets(client, device, lab_configlets)

        # Apply the configlets to the device
        client.addDeviceConfiglets(device, lab_configlets)
        client.applyConfiglets(device)

    # Perform a single Save Topology by default
    client.saveTopology()

def send_to_syslog(mstat,mtype):
    """
    Function to send output from service file to Syslog
    Parameters:
    mstat = Message Status, ie "OK", "INFO" (required)
    mtype = Message to be sent/displayed (required)
    """
    mmes = "\t" + mtype
    logging.info("[{0}] {1}".format(mstat,mmes.expandtabs(7 - len(mstat))))
    if DEBUG:
        print("[{0}] {1}".format(mstat,mmes.expandtabs(7 - len(mstat))))


def deploy_lab(selected_menu,selected_lab):

    # Check for additional commands in lab yaml file
    lab_file = open('/home/arista/menus/{0}'.format(selected_menu + '.yaml'))
    lab_info = YAML().load(lab_file)
    lab_file.close()

    additional_commands = []
    if 'additional_commands' in lab_info['lab_list'][selected_lab]:
        additional_commands = lab_info['lab_list'][selected_lab]['additional_commands']

    # Get access info for the topology
    f = open('/etc/ACCESS_INFO.yaml')
    access_info = YAML().load(f)
    f.close()

    # List of configlets
    lab_configlets = lab_info['labconfiglets']

    # Send message that deployment is beginning
    print("Starting deployment for {0} - {1} lab...".format(selected_menu,selected_lab))

    # Adding new connection to CVP via rcvpapi
    cvp_clnt = ''
    for c_login in access_info['login_info']['cvp']['shell']:
        if c_login['user'] == 'arista':
            while not cvp_clnt:
                try:
                    cvp_clnt = CVPCON(access_info['nodes']['cvp'][0]['internal_ip'],c_login['user'],c_login['pw'])
                    send_to_syslog("OK","Connected to CVP at {0}".format(access_info['nodes']['cvp'][0]['internal_ip']))

                except:
                    send_to_syslog("ERROR", "CVP is currently unavailable....Retrying in 30 seconds.")
                    print("CVP is currently unavailable....Retrying in 30 seconds.")
                    time.sleep(30)

    # Make sure option chosen is valid, then configure the topology
    print("Deploying configlets for {0} - {1} lab...".format(selected_menu,selected_lab))
    send_to_syslog("INFO", "Setting {0} topology to {1} setup".format(access_info['topology'], selected_lab))
    update_topology(cvp_clnt, selected_lab, lab_configlets)
    
    # Execute all tasks generated from reset_devices()
    print("Creating Change Control for for {0} - {1} lab...".format(selected_menu,selected_lab))
    cvp_clnt.getAllTasks("pending")
    tasks_to_check = cvp_clnt.tasks['pending']
    cvp_clnt.execAllTasks("pending")
    send_to_syslog("OK", 'Completed setting devices to topology: {}'.format(selected_lab))

    print("Executing change control for {0} - {1} lab. Please wait for tasks to finish...".format(selected_menu,selected_lab))
    all_tasks_completed = False
    while not all_tasks_completed:
        tasks_running = []
        for task in tasks_to_check:
            if cvp_clnt.getTaskStatus(task['workOrderId'])['taskStatus'] != 'Completed':
                tasks_running.append(task)
            elif cvp_clnt.getTaskStatus(task['workOrderId'])['taskStatus'] == 'Failed':
                print('Task {0} failed. Please check CVP for more information'.format(task['workOrderId']))
            else:
                pass

        if len(tasks_running) == 0:
            
            print("Tasks finished. Finalizing deployment for {0} - {1} lab...".format(selected_menu,selected_lab))

            # Execute additional commands if there are any for the lab
            for command in additional_commands:
                os.system(command)
                
            print("Deployment for {0} - {1} lab is complete.".format(selected_menu,selected_lab))
            all_tasks_completed = True
        
    input("Lab Setup Completed. Please press Enter to continue...")
        

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
        device_dict[str(counter)] = veos['ip']
        device_dict[veos['hostname']] = veos['ip']
        counter += 1
    
    print("\nOther Options: ")
    print("96. Screen (screen) - Opens a screen session to each of the hosts")
    print("97. Back to Previous Menu (back)")
    print("98. Shell (shell/bash)")
    print("99. Back to Main Menu (main/exit) - CTRL + c")
    print("")
    user_input = input("What would you like to do? ")

    # Check to see if input is in device_dict
    counter = 1
    try:
      if user_input.lower() in device_dict:
          previous_menu = menu_mode
          os.system('ssh ' + device_dict[user_input])
      elif user_input == '96' or user_input.lower() == 'screen':
          os.system('/usr/bin/screen')
      elif user_input == '97' or user_input.lower() == 'back':
          if menu_mode == previous_menu:
              menu_mode = 'MAIN'
          else:
              menu_mode = previous_menu
      elif user_input == '98' or user_input.lower() == 'bash' or user_input.lower() == 'shell':
          os.system('/bin/bash')
      elif user_input == '99' or user_input.lower() == 'main' or user_input == '99' or user_input.lower() == 'exit':
          menu_mode = 'MAIN'
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
      print('\n\n==========Lab Options Menu==========\n')
      print("Please select from the following options: \n")
      
      # Iterate through lab menu files and print names without .yaml - Increment counter to reflect choices
      counter = 1
      for menu_type in menu_files:
          if menu_type != 'default.yaml':
            # Print Lab Menu and add options to lab options dict
            print('{0}. {1} ({2})'.format(str(counter),menu_type.replace('-', ' ').replace('.yaml', ''), menu_type.replace('.yaml', '').lower() ))
            lab_options_dict[str(counter)] = menu_type
            lab_options_dict[menu_type.replace('.yaml', '').lower()] = menu_type
            counter += 1

      # Additional Menu Options
      print("\nOther Options: ")
      print("97. Back to Previous Menu (back)")
      print("98. SSH to Devices (ssh)")
      print("99. Back to Main Menu (main/exit) - CTRL + c\n")
      
      user_input = input("\nWhat would you like to do?: ")

      # Check to see if digit is in lab_options dict
      try:
          if user_input.lower() in lab_options_dict:
              previous_menu = menu_mode
              menu_mode = 'LAB_' + lab_options_dict[user_input]
          elif user_input == '97' or user_input.lower() == 'back':
              if menu_mode == previous_menu:
                  menu_mode = 'MAIN'
              else:
                  menu_mode = previous_menu
          elif user_input == '98' or user_input.lower() == 'ssh':
              previous_menu = menu_mode
              menu_mode = 'DEVICE_SSH'
          elif user_input == '99' or user_input.lower() == 'main' or user_input == '99' or user_input.lower() == 'exit':
              menu_mode = 'MAIN'
          else:
              print("Invalid Input")
      except:
        print("Invalid Input")



    elif 'LAB_' in menu_mode and menu_mode != 'LAB_OPTIONS':
      
      # Create Commands dict to save commands and later execute based on matching the counter to a dict key
      options_dict = {}

      # Open yaml for the lab option (minus 'LAB_' from menu mode) and load the variables
      menu_file = open('/home/arista/menus/' + menu_mode[4:])
      menu_info = YAML().load(menu_file)
      menu_file.close()

      print('\n\n==========Lab Options Menu - {0}==========\n'.format(menu_mode[4:].replace('-', ' ').replace('.yaml', '')))
      print("Please select from the following options: \n")
      
      counter = 1
      for lab in menu_info['lab_list']:
        print("{0}. {1}".format(str(counter),menu_info['lab_list'][lab]['description']))
        options_dict[str(counter)] = {'selected_lab': lab, 'selected_menu': menu_mode[4:].replace('.yaml', '')}
        options_dict[lab] = {'selected_lab': lab, 'selected_menu': menu_mode[4:].replace('.yaml', '')}
        counter += 1
      print('\n')

      # Additional Menu Options
      print("Other Options: ")
      print("97. Back to Previous Menu (back)")
      print("98. SSH to Devices (ssh)")
      print("99. Back to Main Menu (main/exit) - CTRL + c\n")

      # User Input
      user_input = input("What would you like to do?: ")

      # Check to see if input is in commands_dict
      try:
          if user_input.lower() in options_dict:
              previous_menu = menu_mode
              deploy_lab(selected_menu=options_dict[user_input]['selected_menu'],selected_lab=options_dict[user_input]['selected_lab'])
          elif user_input == '97' or user_input.lower() == 'back':
              if menu_mode == previous_menu:
                  menu_mode = 'MAIN'
              else:
                  menu_mode = previous_menu
          elif user_input == '98' or user_input.lower() == 'ssh':
              previous_menu = menu_mode
              menu_mode = 'DEVICE_SSH'
          elif user_input == '99' or user_input.lower() == 'main' or user_input == '99' or user_input.lower() == 'exit':
              menu_mode = 'MAIN'
          else:
              print("Invalid Input")
      except:
        print("Invalid Input")

def main_menu():
    global menu_mode
    global previous_menu

    os.system("clear")
    print("\n\n*****************************************")
    print("*****Jump Host for Arista Test Drive*****")
    print("*****************************************")
    print("\n\n==========Main Menu==========\n")
    print("Please select from the following options: ")

    # Create options dict to later send to deploy_lab
    options_dict = {}

    # Open yaml for the default yaml and read what file to lookup for default menu
    default_menu_file = open('/home/arista/menus/default.yaml')
    default_menu_info = YAML().load(default_menu_file)
    default_menu_file.close()


    # Open yaml for the lab option (minus 'LAB_' from menu mode) and load the variables
    menu_file = open('/home/arista/menus/{0}'.format(default_menu_info['default_menu']))
    menu_info = YAML().load(menu_file)
    menu_file.close()


    
    counter = 1
    menu = default_menu_info['default_menu'].replace('.yaml', '')
    for lab in menu_info['lab_list']:
      print("{0}. {1}".format(str(counter),menu_info['lab_list'][lab]['description']))
      options_dict[str(counter)] = {'selected_lab': lab, 'selected_menu': menu}
      options_dict[lab] = {'selected_lab': lab, 'selected_menu': menu}
      counter += 1
    print('\n')



    print("97. Additional Labs (labs)")
    print("98. SSH to Devices (ssh)")
    print("99. Exit LabVM (quit/exit) - CTRL + c")
    print("")

    user_input = input("What would you like to do?: ")
    
    # Check user input to see which menu to change to
    try:
      if user_input.lower() in options_dict:
          deploy_lab(selected_menu=options_dict[user_input]['selected_menu'],selected_lab=options_dict[user_input]['selected_lab'])
      elif user_input == '98' or user_input.lower() == 'ssh':
        previous_menu = menu_mode
        menu_mode = 'DEVICE_SSH'
      elif user_input == '97' or user_input.lower() == 'labs':
        previous_menu = menu_mode
        menu_mode = 'LAB_OPTIONS'
      elif user_input == '99' or user_input.lower() == 'exit' or user_input.lower() == 'quit':
        menu_mode = 'EXIT'
      else:
        print("Invalid Input")
    except:
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
        elif menu_mode == 'EXIT':
          print('User exited.')
          quit()
      except KeyboardInterrupt:
        if menu_mode == 'MAIN':
          print('User exited.')
          quit()
        else:
          menu_mode = 'MAIN'
        


if __name__ == '__main__':
    main()
