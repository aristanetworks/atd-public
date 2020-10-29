var atdHostname = window.location.hostname;

while(true) {
    try {
        document.getElementById("cvp_link").innerHTML = '<a href="https://' + atdHostname + '" target="_blank">CVP</a>';
        break
    } catch {
        continue;
    }
}

