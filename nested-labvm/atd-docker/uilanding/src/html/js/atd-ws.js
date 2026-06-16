document.addEventListener('alpine:init', () => {
    Alpine.store('atd', {
        cvp: { status: '', version: '' },
        tasks: null,
        get taskSummary() {
            var tasks = this.tasks;
            if (!tasks || tasks.status !== 'Active' || !tasks.tasks) {
                return 'No pending tasks in CVP.';
            }
            var parts = [];
            for (var s in tasks.tasks) {
                parts.push(tasks.tasks[s] + ' ' + s);
            }
            return parts.join(', ') + ' task' + (parts.length !== 1 ? 's' : '');
        }
    });
    if (_pendingStatusData) {
        _applyStatusData(_pendingStatusData);
        _pendingStatusData = null;
    }
});

var atdURL = window.location.origin;
if (atdURL.includes('https')) {
    atdURL = atdURL.replace('https:', 'wss:');
} else {
    atdURL = atdURL.replace('http:', 'ws:');
}
atdURL += '/td-ws';

var event_timer_ids = {};
var topo_notify = false;
var _pendingStatusData = null;

function _applyStatusData(data) {
    if ('cvp' in data && window.Alpine && Alpine.store('atd')) {
        var store = Alpine.store('atd');
        if (data.cvp && typeof data.cvp === 'object') {
            store.cvp.status = data.cvp.status || '';
            store.cvp.version = data.cvp.version || '';
        }
        if ('tasks' in data) {
            store.tasks = data.tasks || null;
        }
    }
    if ('uptime' in data) {
        instanceCountdown('countdown_timer', data.uptime.boottime, data.uptime.runtime);
    }
}

createWS(atdURL);

function createWS(SOCK_URL) {
    var ws = new WebSocket(SOCK_URL);
    ws.onopen = function() {
        ws.send(JSON.stringify({ type: 'hello', data: { action: 'status' } }));
    };
    ws.onclose = function(evt) {
        if (!evt.wasClean) {
            setTimeout(function() { createWS(SOCK_URL); }, 500);
        }
    };
    ws.onmessage = function(evt) {
        var received_msg = JSON.parse(evt.data);
        if (received_msg.type === 'ping') {
            ws.send(JSON.stringify({ type: 'pong', data: { message: 'pong' } }));
        } else if (received_msg.type === 'status') {
            var data = received_msg.data;
            if (window.Alpine && Alpine.store('atd')) {
                _applyStatusData(data);
            } else {
                _pendingStatusData = data;
            }
            ws.send(JSON.stringify({ type: 'update', data: { message: 'ACK' } }));
        }
    };
}

function instanceCountdown(element, boot_time, runtime) {
    var el = document.getElementById(element);
    if (!el) return;
    if (event_timer_ids.hasOwnProperty(element)) {
        clearInterval(event_timer_ids[element]);
        delete event_timer_ids[element];
    }
    var interval = setInterval(function() {
        var countdown_diff = (boot_time + (runtime * 60 * 60)) - Math.floor(new Date().getTime() / 1000);
        var text = '00:00:00';
        if (countdown_diff > 0) {
            var h = Math.floor((countdown_diff / (60 * 60)) % 24);
            var m = Math.floor((countdown_diff / 60) % 60);
            var s = Math.floor(countdown_diff % 60);
            text = h.toString().padStart(2, '0') + ':' + m.toString().padStart(2, '0') + ':' + s.toString().padStart(2, '0');
            if (countdown_diff < 30 * 60 && !topo_notify) {
                alert('Your topology will shutdown in ' + m + ' minutes.');
                topo_notify = true;
            }
        }
        el.textContent = text;
        el.classList.toggle('timer-warning', countdown_diff <= 0 || countdown_diff < 30 * 60);
    }, 1000);
    event_timer_ids[element] = interval;
}
