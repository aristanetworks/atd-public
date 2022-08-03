package main

import (
	"log"
	"sync"

	"github.com/aristanetworks/go-cvprac/v3/client"
)

// ===============================================================
// CVP GO Routines
// ===============================================================

func updateDeviceConfigs(_node_data ConfInventory, _lab_data *ConfigueCvp, wg *sync.WaitGroup) {
	var _cfgs_remove []Configlets_List_struct
	var _cfgs_remain []Configlets_List_struct
	// Build Set of device Cfgs
	var _device_cfgs []string
	_device_cfgs = append(_device_cfgs, BASE_CFGS...)
	_device_cfgs = append(_device_cfgs, _lab_data.Lab_cfgs[_lab_data.Lab][_node_data.Cvp.Hostname]...)
	for i := 0; i < len(_node_data.Cfgs); i++ {
		if stringExists(_node_data.Cfgs[i].Name, _device_cfgs) {
			_cfgs_remain = append(_cfgs_remain, Configlets_List_struct{
				Name: _node_data.Cfgs[i].Name,
				Key:  _node_data.Cfgs[i].Key,
			})
		}
	}
}

// ===============================================================
// CVP Utilities
// ===============================================================

func getCvpInventory() map[string]ConfInventory {
	var cvp_inventory map[string]ConfInventory
	// Get all devices in inventory
	_all_inventory, _ := CVP_client.API.GetInventory()
	// Iterate through devices
	for i := 0; i < len(_all_inventory); i++ {
		var _hostname string = _all_inventory[i].Hostname
		// Get current device configs
		var _dev_cvp ConfInventory
		_dev_cfgs, _ := CVP_client.API.GetConfigletsByDeviceID(_all_inventory[i].SystemMacAddress)
		_dev_cvp.Cvp = &_all_inventory[i]
		_dev_cvp.Cfgs = _dev_cfgs
		cvp_inventory[_hostname] = _dev_cvp
	}
	return cvp_inventory
}

func configureTopo(module_opt string, lab_opt string) {
	// Function to configure the topology for a lab
	var topo_conf ConfigueCvp
	var module_info Menu_data
	var cvp_inventory map[string]ConfInventory
	topo_conf.Lab = lab_opt
	topo_conf.Lab_module = module_opt
	module_info, err := loadMenu(module_opt)
	if err == nil {
		topo_conf.Lab_cfgs = module_info.Labconfiglets
		topo_conf.Lab_list = module_info.Lab_lists
		// Check and connect to CVP
		if cvpCheckAndConnect(CVP_client) {
			_, err := CVP_client.API.GetCvpInfo()
			if err != nil {
				log.Printf("ERROR: %s\n", err)
			} else {
				// Connected CVP!
				log.Println("Getting current configlets for nodes via CVP")
				topo_conf.Status = "Getting current configlets for nodes via CVP"
				// Getting all devices and configlets associated
				cvp_inventory = getCvpInventory()
				// Section to start Removing old configlets and Apply new configlets to each device
				// Set WaitGroup vars
				var _instance_count int = len(cvp_inventory)
				instance_wait_group := new(sync.WaitGroup)
				instance_wait_group.Add(_instance_count)
				// Iterate through all nodes in inventory
				for _, _node_value := range cvp_inventory {
					// Create a separate GO Routine for each node
					go updateDeviceConfigs(_node_value, &topo_conf, instance_wait_group)
				}
				// Wait for all GO Routines to finish
				instance_wait_group.Wait()

			}
		}
	}
}

func cvpCheckAndConnect(cvp_client *client.CvpClient) bool {
	if cvp_client.SessID == "" {
		log.Println("CVP is not active, re-trying to connect.")
		if err := cvp_client.Connect(TOPO_USER, TOPO_PWD); err != nil {
			log.Printf("CVP is not running or is starting up: %s\n", err)
			return false
		} else {
			log.Println("CVP is up and running")
			return true
		}
	} else {
		// Verify that the CVP SessionID is active
		_, err := cvp_client.API.GetCvpInfo()
		if err != nil {
			log.Println("CVP Session is no longer active")
			cvp_client.SessID = ""
			return false
		} else {
			log.Println("CVP is active.")
			return true
		}
	}
}
