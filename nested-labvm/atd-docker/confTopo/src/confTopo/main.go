package main

import (
	"encoding/base64"
	"encoding/json"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/aristanetworks/go-cvprac/v3/client"
	"github.com/gorilla/mux"
	"github.com/gorilla/websocket"
	"gopkg.in/yaml.v3"
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

type Cvp_struct struct {
	Status  string      `json:"status"`
	Version string      `json:"version"`
	Total   int         `json:"total"`
	Tasks   interface{} `json:"tasks"`
}

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
}

var ACCESS string = "/etc/atd/ACCESS_INFO.yaml"
var SLEEP_DELAY = (60 * time.Second)
var CVP_NODES = []string{"192.168.0.5"}
var TOPO_USER string = ""
var TOPO_PWD string = ""
var TEST string = "string"

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

// =============================================================
// Websocket and Web Handler GO Routines
// =============================================================

func ReadWS(ws *websocket.Conn, r *http.Request) {
	defer ws.Close()
	// Create Channel for connection status
	done := make(chan struct{})
	log.Printf("New websocket connection")
	for {
		_, msg, err := ws.ReadMessage()
		if err != nil {
			if websocket.IsUnexpectedCloseError(err, websocket.CloseGoingAway, websocket.CloseAbnormalClosure) {
				log.Printf("Error: %s\n", err)
			}
			close(done)
			break
		}
		log.Printf("Error decoding websocket msg: %s\n", err)
		log.Printf("Message: %s\n", msg)
	}
	log.Printf("Closing WS connection to\n")
}

// =============================================================
// Websocket and Web Handlers
// =============================================================

func TopoRequestHandler(w http.ResponseWriter, r *http.Request) {
	params := r.URL.Query()
	var res Cvp_struct
	_, ok := params["action"]
	if ok {
		encoded_action := params["action"][0]
		decoded_action, err := decodeID_to_string(encoded_action)
		if err != nil {
			log.Printf("Error Decoding id of: %s", encoded_action)
		}
		log.Printf("GET: %s", decoded_action)
		if decoded_action == "cvp_status" {
			log.Println("Get CVP Status")
			// Start the connection to CVP
			cvpClient, _ := client.NewCvpClient(
				client.Protocol("https"),
				client.Port(443),
				client.Hosts(CVP_NODES...),
				client.Debug(false))
			if err := cvpClient.Connect(TOPO_USER, TOPO_PWD); err != nil {
				log.Printf("ERROR: %s\n", err)
				res.Status = "Starting"
				res.Version = ""
			} else {
				data, err := cvpClient.API.GetCvpInfo()
				// Logout of CVP Session
				cvpClient.API.Logout()
				if err != nil {
					log.Printf("ERROR: %s\n", err)
					res.Status = "Starting"
					res.Version = ""
				}
				log.Printf("CVP VERSION = %s", data.Version)
				res.Status = "UP"
				res.Version = data.Version
			}
			json.NewEncoder(w).Encode(res)
		} else if decoded_action == "cvp_tasks" {
			_cvp_tasks := make(map[string]int)
			_active_tasks := 0
			cvpClient, _ := client.NewCvpClient(
				client.Protocol("https"),
				client.Port(443),
				client.Hosts(CVP_NODES...),
				client.Debug(false))
			if err := cvpClient.Connect(TOPO_USER, TOPO_PWD); err != nil {
				log.Printf("ERROR: %s\n", err)
				res.Status = "Starting"
				res.Version = ""
			} else {
				// Get tasks from CVP
				data, err := cvpClient.API.GetTaskByStatus("active")
				// Logout of CVP Session
				cvpClient.API.Logout()
				if err != nil {
					// Error getting tasks from CVP
					log.Printf("ERROR: %s\n", err)
					res.Status = "Error getting tasks"
					res.Total = _active_tasks
					res.Tasks = _cvp_tasks
				} else {
					if len(data) > 0 {
						for i := 0; i < len(data); i++ {
							if !strings.Contains(data[i].WorkOrderUserDefinedStatus, "cancelled") {
								_active_tasks++
								if _, found := _cvp_tasks[data[i].WorkOrderUserDefinedStatus]; found {
									_cvp_tasks[data[i].WorkOrderUserDefinedStatus]++
								} else {
									_cvp_tasks[data[i].WorkOrderUserDefinedStatus] = 1
								}
							}
						}
					}
					if _active_tasks > 0 {
						res.Status = "Active"
						res.Total = _active_tasks
						res.Tasks = _cvp_tasks
					} else {
						res.Status = "Complete"
						res.Total = _active_tasks
						res.Tasks = _cvp_tasks
					}
				}
				json.NewEncoder(w).Encode(res)
			}
		}
	} else {
		log.Println("No action parameter provided")
	}
}

func TopoDataHandler(w http.ResponseWriter, r *http.Request) {
	log.Println("New WS Connection")
	// Check origin for request
	upgrader.CheckOrigin = func(r *http.Request) bool { return true }

	// Upgrade the connection to a WebSocket
	ws, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Println(err)
		return
	}
	go ReadWS(ws, r)

}

func main() {
	// Loop and wait until the ACCESS_INFO file exists
	for {
		if fileExists(ACCESS) {
			break
		} else {
			log.Printf("ERROR: ACCESS_INFO file is not available...Waiting for %s\n", SLEEP_DELAY)
		}
	}
	// Try to open ACCESS_INFO yaml file
	accessinfo := Access_yaml{}
	yaml_file, _ := ioutil.ReadFile(ACCESS)
	err := yaml.Unmarshal(yaml_file, &accessinfo)
	if err != nil {
		log.Printf("%s\n", err)
	}
	TOPO_USER = accessinfo.Login_info.Jump_host.User
	TOPO_PWD = accessinfo.Login_info.Jump_host.Pw

	r := mux.NewRouter()
	// Routes consist of a path and a handler function.
	r.HandleFunc("/td-api/conftopo", TopoRequestHandler)
	r.HandleFunc("/td-api/ws-conftopo", TopoDataHandler)
	log.Printf("*** Websocket Server Started on 50010 ***")
	// Bind to a port and pass our router in
	log.Fatal(http.ListenAndServe(":50010", r))
}
