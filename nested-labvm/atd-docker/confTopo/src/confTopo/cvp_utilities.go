package main

import (
	"log"
	"strconv"
	"sync"
	"time"

	cvpapi "github.com/aristanetworks/go-cvprac/v3/api"
	"github.com/aristanetworks/go-cvprac/v3/client"
)

var TZ string = "America/Chicago"
var COUNTRY_CODE string = "United States"

// ===============================================================
// CVP GO Routines
// ===============================================================

func updateDeviceConfigs(_node_data ConfInventory, _lab_data *ConfigueCvp, _cfg_data map[string]cvpapi.Configlet, wg *sync.WaitGroup) {
	defer wg.Done()
	var _cfgs_remove []cvpapi.Configlet
	var _cfgs_remain []cvpapi.Configlet
	// Build Set of device Cfgs
	var _device_cfgs []string
	_device_cfgs = append(_device_cfgs, BASE_CFGS...)
	_device_cfgs = append(_device_cfgs, _lab_data.Lab_cfgs[_lab_data.Lab][_node_data.Cvp.Hostname]...)

	// Loop through cfgs currently assigned to a node and remove if not needed
	for i := 0; i < len(_node_data.Cfgs); i++ {
		if !stringExists(_node_data.Cfgs[i].Name, _device_cfgs) {
			log.Printf("Configlet %s is not part of the lab configlets on %s - Removing from device\n", _node_data.Cfgs[i].Name, _node_data.Cvp.Hostname)
			_cfgs_remove = append(_cfgs_remove, _node_data.Cfgs[i])
		}
	}
	// Loop through the cfgs that need to be applied to a device
	for i := 0; i < len(_device_cfgs); i++ {
		_cfg_name := _device_cfgs[i]
		_cfg_info, _ok := _cfg_data[_cfg_name]
		if _ok {
			log.Printf("Configlet %s will be applied to %s\n", _device_cfgs[i], _node_data.Cvp.Hostname)
			_cfgs_remain = append(_cfgs_remain, _cfg_info)
		}
	}
	// Make call to remove configlets for device
	_remove, err_remove := CVP_client.API.RemoveConfigletsFromDevice("GO-Conftopo", _node_data.Cvp, true, _cfgs_remove...)
	log.Printf("Remove: %s\n", _remove)
	// Make API call to apply configlets for a device
	_apply, err_apply := CVP_client.API.ApplyConfigletsToDevice("GO-ConfTopo", _node_data.Cvp, true, _cfgs_remain...)
	log.Printf("Apply: %s\n", _apply)
	if err_remove != nil {
		log.Printf("Error removing configlets from device %s\n", _node_data.Cvp.Hostname)
	}
	if err_apply != nil {
		log.Printf("Error adding configlets to device %s\n", _node_data.Cvp.Hostname)
	}
}

func checkTaskStatus(_task_id int, wg *sync.WaitGroup) {
	defer wg.Done()
	var _task_status *cvpapi.CvpTask
	_task_status, err := CVP_client.API.GetTaskByID(_task_id)
	if err != nil {
		log.Printf("Error getting task status for %d\n", _task_id)
	} else {
		for {
			if _task_status.WorkOrderState == "COMPLETED" {
				log.Printf("Task %d is Complete\n", _task_id)
				break
			} else if _task_status.WorkOrderState == "FAILED" {
				log.Printf("Task %d Failed\n", _task_id)
				break
			} else {
				log.Printf("Task %d is currently %s", _task_id, _task_status.WorkOrderState)
				time.Sleep(2 * time.Second)
			}
		}
	}
}

// ===============================================================
// CVP Utilities
// ===============================================================

func getCvpInventory() map[string]ConfInventory {
	cvp_inventory := make(map[string]ConfInventory)
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

func configureTopo(module_opt string, lab_opt string, Cvp_client *client.CvpClient) {
	// Function to configure the topology for a lab
	var topo_conf ConfigueCvp
	var module_info Menu_data
	cvp_inventory := make(map[string]ConfInventory)
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
				// var _cc_task_info []cvpapi.ChangeControlTaskInfo
				var _task_ids_list []int
				// Connected CVP!
				log.Println("Getting current configlets for nodes via CVP")
				topo_conf.Status = "Getting current configlets for nodes via CVP"
				// Getting all devices and configlets associated
				cvp_inventory = getCvpInventory()
				// Section to start Removing old configlets and Apply new configlets to each device
				// Grab data for all configlets that will be used for the lab
				cfg_lab_data := make(map[string]cvpapi.Configlet)
				// Get Configlet data for base CFGS
				for i := 0; i < len(BASE_CFGS); i++ {
					_cfg_info, err := CVP_client.API.GetConfigletByName(BASE_CFGS[i])
					if err != nil {
						log.Printf("Error getting Configlet data for %s\n", BASE_CFGS[i])
					} else {
						log.Printf("Grabbed configlet data for %s\n", BASE_CFGS[i])
						cfg_lab_data[BASE_CFGS[i]] = *_cfg_info
					}
				}
				// Get Configlet data for lab Configlets
				for _, value := range topo_conf.Lab_cfgs[topo_conf.Lab] {
					for i := 0; i < len(value); i++ {
						_cfg_info, err := CVP_client.API.GetConfigletByName(value[i])
						if err != nil {
							log.Printf("Error getting Configlet data for %s\n", value[i])
						} else {
							log.Printf("Grabbed configlet data for %s\n", topo_conf.Lab_cfgs[topo_conf.Lab])
							cfg_lab_data[value[i]] = *_cfg_info
						}
					}
				}
				// Set WaitGroup vars
				var _instance_count int = len(cvp_inventory)
				instance_wait_group := new(sync.WaitGroup)
				instance_wait_group.Add(_instance_count)
				// Iterate through all nodes in inventory
				for _, _node_value := range cvp_inventory {
					// Create a separate GO Routine for each node
					go updateDeviceConfigs(_node_value, &topo_conf, cfg_lab_data, instance_wait_group)
				}
				log.Println("Started all Update Devices")
				// Wait for all GO Routines to finish
				instance_wait_group.Wait()
				log.Printf("Finished updating Configlet assignments for %d devices\n", _instance_count)
				// Get All Task IDs that have been generated
				// Section to temporarily manually execute each task individually
				// ================================================================
				available_tasks, err := CVP_client.API.GetTaskByStatus("PENDING")
				// ================================================================
				//
				// Commenting out section below due to not approving/executing CC
				// ================================================================
				// available_tasks, err := CVP_client.API.GetChangeControlAvailableTasks("PENDING", 0, 0)
				// ================================================================
				if err != nil {
					log.Println("Error getting Pending Tasks")
				} else {
					for i := 0; i < len(available_tasks); i++ {
						// Section to temporarily manually execute each task individually
						// ================================================================
						_task_id_int, _ := strconv.Atoi(available_tasks[i].WorkOrderID)
						_task_ids_list = append(_task_ids_list, _task_id_int)
						// ================================================================
						//
						// Commenting out section below due to not approving/executing CC
						// ================================================================
						// var _task_order int
						// _task_order = i + 1
						// _cc_task_info = append(_cc_task_info, cvpapi.ChangeControlTaskInfo{
						// 	TaskID:              available_tasks[i].WorkOrderID,
						// 	TaskOrder:           _task_order,
						// 	SnapshotTemplateKey: "",
						// 	ClonedCcID:          "",
						// })
						// ================================================================
					}
					// Section to temporarily manually execute each task individually
					// ================================================================
					err := CVP_client.API.ExecuteTasks(_task_ids_list)
					if err != nil {
						log.Println("Error executing tasks")
					} else {
						var _task_count int = len(_task_ids_list)
						task_wait_group := new(sync.WaitGroup)
						task_wait_group.Add(_task_count)
						// Start a GO Routine to check the status of all tasks
						for i := 0; i < len(_task_ids_list); i++ {
							go checkTaskStatus(_task_ids_list[i], task_wait_group)
						}
						task_wait_group.Wait()
						log.Println("Finished all tasks")

					}
					// ================================================================
					// Commenting out section below due to not approving/executing CC
					// ================================================================
					// current_time := time.Now().Format("2006-01-02 15:04:05")
					// cc, err_cc := CVP_client.API.CreateChangeControl("CC", TZ, COUNTRY_CODE, current_time, "", "Custom", "false", _cc_task_info)
					// if err_cc != nil {
					// 	log.Println("Error creating Change Control")
					// } else {

					// }
					// ================================================================
				}

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
