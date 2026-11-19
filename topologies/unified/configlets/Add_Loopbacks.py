from sys import path
path.append('/usr/lib64/python2.7/site-packages/')
import yaml
from cvplibrary import CVPGlobalVariables, GlobalVariableNames, Device

ztp = CVPGlobalVariables.getValue(GlobalVariableNames.ZTP_STATE)
ip = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_IP)

if ztp == 'true':
    user = CVPGlobalVariables.getValue(GlobalVariableNames.ZTP_USERNAME)
    passwd = CVPGlobalVariables.getValue(GlobalVariableNames.ZTP_PASSWORD)
else:
    user = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_USERNAME)
    passwd = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_PASSWORD)

ss = Device(ip,user,passwd)

def get_hostname():
    show_hostname = ss.runCmds(["enable", {"cmd": "show hostname"}])[1]
    hostname = show_hostname['response']['hostname']
    return hostname

def get_bgpasn():
    show_ip_bgp_summary = ss.runCmds(["enable", {"cmd": "show ip bgp summary"}])[1]
    asn = show_ip_bgp_summary['response']['vrfs']['default']['asn']
    return asn

def create_routes(hostname):
    number = hostname[-1:]
    if 'leaf' in hostname:
        switch_type = "10"
    elif 'spine' in hostname:
        switch_type = "20"
    for x in range(100, 200):
        print "interface Loopback%d" % (x)
        print "   ip add 10.%s.%s.%d/32" % (switch_type, number, x)
    return

def add_bgp_conf(asn):
    print 'router bgp %s' % asn
    print '   redistribute connected'
    return
    
def main():
    hostname = get_hostname()
    if 'leaf' or 'spine' in hostname:
        create_routes(hostname)
        asn = get_bgpasn()
        add_bgp_conf(asn)

if __name__ == "__main__":
    main()
