package main

import (
	cvpapi "github.com/aristanetworks/go-cvprac/v3/api"
)

type Cred_struct struct {
	Pw   string `yaml:"pw"`
	User string `yaml:"user"`
}

type Login_struct struct {
	Jump_host Cred_struct `yaml:"jump_host"`
}

type Access_yaml struct {
	Login_info     Login_struct `yaml:"login_info"`
	Nodes          interface{}  `yaml:"nodes"`
	Topology       string       `yaml:"topology"`
	Eos_type       string       `yaml:"eos_type"`
	Version        string       `yaml:"version"`
	Cvp_mode       string       `yaml:"cvp_mode"`
	Zone           string       `yaml:"zone"`
	Name           string       `yaml:"name"`
	Project        string       `yaml:"project"`
	Title          string       `yaml:"title"`
	Cvp            string       `yaml:"cvp"`
	Disabled_links []string     `yaml:"disabled_links"`
	Labguides      string       `yaml:"labguides"`
}

type ConfigueCvp struct {
	Lab        string
	Lab_module string
	Lab_list   map[string]Lab_list_struct
	Lab_cfgs   map[string]map[string][]string
	Cc_ids     []string
	Task_ids   []string
	Status     string
	Inventory  []*cvpapi.NetElement
}

type Configlets_List_struct struct {
	Name string
	Key  string
}

type ConfInventory struct {
	Cvp  *cvpapi.NetElement
	Cfgs []cvpapi.Configlet
}

type Lab_list_struct struct {
	Description     string   `yaml:"description"`
	Additional_cmds []string `yaml:"additional_commands"`
}

type Menu_data struct {
	Lab_lists     map[string]Lab_list_struct     `yaml:"lab_list"`
	Labconfiglets map[string]map[string][]string `yaml:"labconfiglets"`
}

type Cvp_struct struct {
	Status  string      `json:"status"`
	Version string      `json:"version"`
	Total   int         `json:"total"`
	Tasks   interface{} `json:"tasks"`
}

type Received_msg struct {
	Type string        `json:"type"`
	Data Received_data `json:"data"`
}

type Received_data struct {
	Lab    string `json:"lab"`
	Module string `json:"module"`
}

type Client_data struct {
	Status string `json:"status"`
}
type Client_pkg struct {
	Type      string      `json:"type"`
	Timestamp string      `json:"time"`
	Data      Client_data `json:"data"`
}
