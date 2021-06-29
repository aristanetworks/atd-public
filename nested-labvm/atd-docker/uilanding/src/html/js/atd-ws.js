var atdURL = window.location.origin;
if ( atdURL.includes('https') ) {
    atdURL = atdURL.replace("https:","wss:");
}
else {
    atdURL = atdURL.replace("http:","ws:");
}

atdURL += "/td-ws";
var ws = new WebSocket(atdURL);

createWS(atdURL);


function createWS(SOCK_URL) {
    // Create a websocket connection
    ws = new WebSocket(SOCK_URL);
    ws.onopen = function()
    {
        // Web Socket is connected, send data using send()
        ws.send(JSON.stringify({
            type:"hello",
            data: {
                action: "status"
            }
        }));
    };
    
    ws.onclose = function(evt) {
        if ( !evt.wasClean ) {
            setTimeout(function() {
                createWS(SOCK_URL);
            },500)
        }
    }

    ws.onmessage = function (evt) 
    { 
        var re_data = evt.data;
        var received_msg = JSON.parse(re_data);
        if (received_msg['type'] == 'ping') {
            ws.send(JSON.stringify({
                type: "pong", 
                data: {
                    message: 'pong'
                }
            }));
        }
        else if (received_msg['type'] == 'status') {
            var reg_data = received_msg['data'];
            console.log(reg_data);
            if ('cvp' in reg_data) {
                _cvp_info = "<h3>CVP " + reg_data['cvp']['version'] + " is currently " + reg_data['cvp']['status'] + "</h3>";
                if ('tasks' in reg_data) {
                    if (reg_data['tasks']) {
                        if (reg_data['tasks']['status'] == 'Active') {
                            _cvp_info += "Currently " + reg_data['tasks']['total'] + " Active tasks.";
                            console.log(reg_data['tasks']['tasks']);
                        }
                        else {
                            _cvp_info += "No pending tasks in CVP.";
                        }
                    }
                }
                document.getElementById("cvp_info").innerHTML = _cvp_info
            }
            ws.send(JSON.stringify({
                type: "update", 
                data: {
                    message: 'ACK'
                }
            }));
        }    
    }
}
