package main

import (
	"log"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader {
	ReadBufferSize: 1024,
	WriteBufferSize: 1024,
}

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

func TopoRequestHandler(w http.ResponseWriter, r *http.Request) {
	log.Printf("GET STATUS\n")
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
	r := mux.NewRouter()
	// Routes consist of a path and a handler function.
	r.HandleFunc("/td-go/conftopo", TopoRequestHandler)
	r.HandleFunc("/td-go/ws-conftopo", TopoDataHandler)
	log.Printf("*** Websocket Server Started on 50021 ***")
	// Bind to a port and pass our router in
	log.Fatal(http.ListenAndServe(":50021", r))
}
