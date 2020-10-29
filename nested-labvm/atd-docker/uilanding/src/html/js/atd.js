var atdHostname = window.location.hostname;

function updateCVP() {
    document.getElementById("cvp_link").innerHTML = '<a href="https://' + atdHostname + '" target="_blank">CVP</a>';
}