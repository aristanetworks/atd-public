package main

import (
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"os"

	"gopkg.in/yaml.v3"
)

// ====================================================
// Utility Functions
// ====================================================

func decodeID(tmp_data string) (map[string]interface{}, error) {
	decoded, err := base64.StdEncoding.DecodeString(tmp_data)
	if err != nil {
		log.Println("Decode Error: ", err)
		return nil, err
	}
	decoded_json := map[string]interface{}{}
	if err := json.Unmarshal(decoded, &decoded_json); err != nil {
		log.Println("Error converting to JSON: ", err)
		return nil, err
	}

	return decoded_json, nil
}

func decodeID_to_string(tmp_data string) (string, error) {
	decoded, err := base64.StdEncoding.DecodeString(tmp_data)
	if err != nil {
		log.Println("Decode Error: ", err)
		return "", err
	}
	var decoded_json string
	if err := json.Unmarshal(decoded, &decoded_json); err != nil {
		log.Println("Error converting to JSON: ", err)
		return "", err
	}

	return decoded_json, nil
}

func encodeID(tmp_data map[string]interface{}) string {
	en_json, err := json.Marshal(tmp_data)
	if err != nil {
		log.Fatal("ERROR")
	}
	encoded_string := base64.StdEncoding.EncodeToString(en_json)
	return encoded_string
}

func fileExists(filename string) bool {
	info, err := os.Stat(filename)
	if os.IsNotExist(err) {
		return false
	}
	return !info.IsDir()
}

func loadMenu(module_opt string) (Menu_data, error) {
	var _menu_file string
	moduleinfo := Menu_data{}
	_menu_file = fmt.Sprintf("%s/%s.yaml", MENU_DIR, module_opt)
	if fileExists(_menu_file) {
		yaml_file, _ := ioutil.ReadFile(_menu_file)
		err := yaml.Unmarshal(yaml_file, &moduleinfo)
		if err != nil {
			log.Printf("%s\n", err)
			return moduleinfo, err
		}
	}
	return moduleinfo, nil
}

func stringExists(_search string, _list []string) bool {
	for _, _value := range _list {
		if _search == _value {
			return true
		}
	}
	return false
}
