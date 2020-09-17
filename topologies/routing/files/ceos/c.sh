mkdir eos1
echo "SERIALNUMBER=eos1" >> eos1/ceos-config
echo -n "00:1c:73:b0:c6:01" >> eos1/system_mac_address
echo "username arista privilege 15 secret 5 $1$4VjIjfd1$XkUVulbNDESHFzcxDU.Tk1" >> eos1/startup-config
echo "!" >> eos1/startup-config
echo "management api http-commands" >> eos1/startup-config
echo "   no shutdown" >> eos1/startup-config
echo "!" >> eos1/startup-config
echo "daemon TerminAttr" >> eos1/startup-config
echo "   exec /usr/bin/TerminAttr -ingestgrpcurl=192.168.0.5:9910 -cvcompression=gzip -ingestauth=key,atd-lab -smashexcludes=ale,flexCounter,hardware,kni,pulse,strata -ingestexclude=/Sysdb/cell/1/agent,/Sysdb/cell/2/agent -ingestvrf=default -taillogs" >> eos1/startup-config
echo "   no shutdown" >> eos1/startup-config
echo "!" >> eos1/startup-config
echo "service routing protocols model multi-agent" >> eos1/startup-config
echo "interface Management0" >> eos1/startup-config
echo "   ip address 192.168.0.10/24" >> eos1/startup-config
echo "!" >> eos1/startup-config
echo "hostname eos1" >> eos1/startup-config
mkdir eos2
echo "SERIALNUMBER=eos2" >> eos2/ceos-config
echo -n "00:1c:73:b1:c6:01" >> eos2/system_mac_address
echo "username arista privilege 15 secret 5 $1$4VjIjfd1$XkUVulbNDESHFzcxDU.Tk1" >> eos2/startup-config
echo "!" >> eos2/startup-config
echo "management api http-commands" >> eos2/startup-config
echo "   no shutdown" >> eos2/startup-config
echo "!" >> eos2/startup-config
echo "daemon TerminAttr" >> eos2/startup-config
echo "   exec /usr/bin/TerminAttr -ingestgrpcurl=192.168.0.5:9910 -cvcompression=gzip -ingestauth=key,atd-lab -smashexcludes=ale,flexCounter,hardware,kni,pulse,strata -ingestexclude=/Sysdb/cell/1/agent,/Sysdb/cell/2/agent -ingestvrf=default -taillogs" >> eos2/startup-config
echo "   no shutdown" >> eos2/startup-config
echo "!" >> eos2/startup-config
echo "service routing protocols model multi-agent" >> eos2/startup-config
echo "interface Management0" >> eos2/startup-config
echo "   ip address 192.168.0.11/24" >> eos2/startup-config
echo "!" >> eos2/startup-config
echo "hostname eos2" >> eos2/startup-config
mkdir eos3
echo "SERIALNUMBER=eos3" >> eos3/ceos-config
echo -n "00:1c:73:b2:c6:01" >> eos3/system_mac_address
echo "username arista privilege 15 secret 5 $1$4VjIjfd1$XkUVulbNDESHFzcxDU.Tk1" >> eos3/startup-config
echo "!" >> eos3/startup-config
echo "management api http-commands" >> eos3/startup-config
echo "   no shutdown" >> eos3/startup-config
echo "!" >> eos3/startup-config
echo "daemon TerminAttr" >> eos3/startup-config
echo "   exec /usr/bin/TerminAttr -ingestgrpcurl=192.168.0.5:9910 -cvcompression=gzip -ingestauth=key,atd-lab -smashexcludes=ale,flexCounter,hardware,kni,pulse,strata -ingestexclude=/Sysdb/cell/1/agent,/Sysdb/cell/2/agent -ingestvrf=default -taillogs" >> eos3/startup-config
echo "   no shutdown" >> eos3/startup-config
echo "!" >> eos3/startup-config
echo "service routing protocols model multi-agent" >> eos3/startup-config
echo "interface Management0" >> eos3/startup-config
echo "   ip address 192.168.0.12/24" >> eos3/startup-config
echo "!" >> eos3/startup-config
echo "hostname eos3" >> eos3/startup-config
mkdir eos4
echo "SERIALNUMBER=eos4" >> eos4/ceos-config
echo -n "00:1c:73:b3:c6:01" >> eos4/system_mac_address
echo "username arista privilege 15 secret 5 $1$4VjIjfd1$XkUVulbNDESHFzcxDU.Tk1" >> eos4/startup-config
echo "!" >> eos4/startup-config
echo "management api http-commands" >> eos4/startup-config
echo "   no shutdown" >> eos4/startup-config
echo "!" >> eos4/startup-config
echo "daemon TerminAttr" >> eos4/startup-config
echo "   exec /usr/bin/TerminAttr -ingestgrpcurl=192.168.0.5:9910 -cvcompression=gzip -ingestauth=key,atd-lab -smashexcludes=ale,flexCounter,hardware,kni,pulse,strata -ingestexclude=/Sysdb/cell/1/agent,/Sysdb/cell/2/agent -ingestvrf=default -taillogs" >> eos4/startup-config
echo "   no shutdown" >> eos4/startup-config
echo "!" >> eos4/startup-config
echo "service routing protocols model multi-agent" >> eos4/startup-config
echo "interface Management0" >> eos4/startup-config
echo "   ip address 192.168.0.13/24" >> eos4/startup-config
echo "!" >> eos4/startup-config
echo "hostname eos4" >> eos4/startup-config
mkdir eos5
echo "SERIALNUMBER=eos5" >> eos5/ceos-config
echo -n "00:1c:73:b4:c6:01" >> eos5/system_mac_address
echo "username arista privilege 15 secret 5 $1$4VjIjfd1$XkUVulbNDESHFzcxDU.Tk1" >> eos5/startup-config
echo "!" >> eos5/startup-config
echo "management api http-commands" >> eos5/startup-config
echo "   no shutdown" >> eos5/startup-config
echo "!" >> eos5/startup-config
echo "daemon TerminAttr" >> eos5/startup-config
echo "   exec /usr/bin/TerminAttr -ingestgrpcurl=192.168.0.5:9910 -cvcompression=gzip -ingestauth=key,atd-lab -smashexcludes=ale,flexCounter,hardware,kni,pulse,strata -ingestexclude=/Sysdb/cell/1/agent,/Sysdb/cell/2/agent -ingestvrf=default -taillogs" >> eos5/startup-config
echo "   no shutdown" >> eos5/startup-config
echo "!" >> eos5/startup-config
echo "service routing protocols model multi-agent" >> eos5/startup-config
echo "interface Management0" >> eos5/startup-config
echo "   ip address 192.168.0.14/24" >> eos5/startup-config
echo "!" >> eos5/startup-config
echo "hostname eos5" >> eos5/startup-config
mkdir eos6
echo "SERIALNUMBER=eos6" >> eos6/ceos-config
echo -n "00:1c:73:b5:c6:01" >> eos6/system_mac_address
echo "username arista privilege 15 secret 5 $1$4VjIjfd1$XkUVulbNDESHFzcxDU.Tk1" >> eos6/startup-config
echo "!" >> eos6/startup-config
echo "management api http-commands" >> eos6/startup-config
echo "   no shutdown" >> eos6/startup-config
echo "!" >> eos6/startup-config
echo "daemon TerminAttr" >> eos6/startup-config
echo "   exec /usr/bin/TerminAttr -ingestgrpcurl=192.168.0.5:9910 -cvcompression=gzip -ingestauth=key,atd-lab -smashexcludes=ale,flexCounter,hardware,kni,pulse,strata -ingestexclude=/Sysdb/cell/1/agent,/Sysdb/cell/2/agent -ingestvrf=default -taillogs" >> eos6/startup-config
echo "   no shutdown" >> eos6/startup-config
echo "!" >> eos6/startup-config
echo "service routing protocols model multi-agent" >> eos6/startup-config
echo "interface Management0" >> eos6/startup-config
echo "   ip address 192.168.0.15/24" >> eos6/startup-config
echo "!" >> eos6/startup-config
echo "hostname eos6" >> eos6/startup-config
mkdir eos7
echo "SERIALNUMBER=eos7" >> eos7/ceos-config
echo -n "00:1c:73:b6:c6:01" >> eos7/system_mac_address
echo "username arista privilege 15 secret 5 $1$4VjIjfd1$XkUVulbNDESHFzcxDU.Tk1" >> eos7/startup-config
echo "!" >> eos7/startup-config
echo "management api http-commands" >> eos7/startup-config
echo "   no shutdown" >> eos7/startup-config
echo "!" >> eos7/startup-config
echo "daemon TerminAttr" >> eos7/startup-config
echo "   exec /usr/bin/TerminAttr -ingestgrpcurl=192.168.0.5:9910 -cvcompression=gzip -ingestauth=key,atd-lab -smashexcludes=ale,flexCounter,hardware,kni,pulse,strata -ingestexclude=/Sysdb/cell/1/agent,/Sysdb/cell/2/agent -ingestvrf=default -taillogs" >> eos7/startup-config
echo "   no shutdown" >> eos7/startup-config
echo "!" >> eos7/startup-config
echo "service routing protocols model multi-agent" >> eos7/startup-config
echo "interface Management0" >> eos7/startup-config
echo "   ip address 192.168.0.16/24" >> eos7/startup-config
echo "!" >> eos7/startup-config
echo "hostname eos7" >> eos7/startup-config
mkdir eos8
echo "SERIALNUMBER=eos8" >> eos8/ceos-config
echo -n "00:1c:73:b7:c6:01" >> eos8/system_mac_address
echo "username arista privilege 15 secret 5 $1$4VjIjfd1$XkUVulbNDESHFzcxDU.Tk1" >> eos8/startup-config
echo "!" >> eos8/startup-config
echo "management api http-commands" >> eos8/startup-config
echo "   no shutdown" >> eos8/startup-config
echo "!" >> eos8/startup-config
echo "daemon TerminAttr" >> eos8/startup-config
echo "   exec /usr/bin/TerminAttr -ingestgrpcurl=192.168.0.5:9910 -cvcompression=gzip -ingestauth=key,atd-lab -smashexcludes=ale,flexCounter,hardware,kni,pulse,strata -ingestexclude=/Sysdb/cell/1/agent,/Sysdb/cell/2/agent -ingestvrf=default -taillogs" >> eos8/startup-config
echo "   no shutdown" >> eos8/startup-config
echo "!" >> eos8/startup-config
echo "service routing protocols model multi-agent" >> eos8/startup-config
echo "interface Management0" >> eos8/startup-config
echo "   ip address 192.168.0.17/24" >> eos8/startup-config
echo "!" >> eos8/startup-config
echo "hostname eos8" >> eos8/startup-config
mkdir eos9
echo "SERIALNUMBER=eos9" >> eos9/ceos-config
echo -n "00:1c:73:b8:c6:01" >> eos9/system_mac_address
echo "username arista privilege 15 secret 5 $1$4VjIjfd1$XkUVulbNDESHFzcxDU.Tk1" >> eos9/startup-config
echo "!" >> eos9/startup-config
echo "management api http-commands" >> eos9/startup-config
echo "   no shutdown" >> eos9/startup-config
echo "!" >> eos9/startup-config
echo "daemon TerminAttr" >> eos9/startup-config
echo "   exec /usr/bin/TerminAttr -ingestgrpcurl=192.168.0.5:9910 -cvcompression=gzip -ingestauth=key,atd-lab -smashexcludes=ale,flexCounter,hardware,kni,pulse,strata -ingestexclude=/Sysdb/cell/1/agent,/Sysdb/cell/2/agent -ingestvrf=default -taillogs" >> eos9/startup-config
echo "   no shutdown" >> eos9/startup-config
echo "!" >> eos9/startup-config
echo "service routing protocols model multi-agent" >> eos9/startup-config
echo "interface Management0" >> eos9/startup-config
echo "   ip address 192.168.0.18/24" >> eos9/startup-config
echo "!" >> eos9/startup-config
echo "hostname eos9" >> eos9/startup-config
mkdir eos10
echo "SERIALNUMBER=eos10" >> eos10/ceos-config
echo -n "00:1c:73:b9:c6:01" >> eos10/system_mac_address
echo "username arista privilege 15 secret 5 $1$4VjIjfd1$XkUVulbNDESHFzcxDU.Tk1" >> eos10/startup-config
echo "!" >> eos10/startup-config
echo "management api http-commands" >> eos10/startup-config
echo "   no shutdown" >> eos10/startup-config
echo "!" >> eos10/startup-config
echo "daemon TerminAttr" >> eos10/startup-config
echo "   exec /usr/bin/TerminAttr -ingestgrpcurl=192.168.0.5:9910 -cvcompression=gzip -ingestauth=key,atd-lab -smashexcludes=ale,flexCounter,hardware,kni,pulse,strata -ingestexclude=/Sysdb/cell/1/agent,/Sysdb/cell/2/agent -ingestvrf=default -taillogs" >> eos10/startup-config
echo "   no shutdown" >> eos10/startup-config
echo "!" >> eos10/startup-config
echo "service routing protocols model multi-agent" >> eos10/startup-config
echo "interface Management0" >> eos10/startup-config
echo "   ip address 192.168.0.19/24" >> eos10/startup-config
echo "!" >> eos10/startup-config
echo "hostname eos10" >> eos10/startup-config
mkdir eos11
echo "SERIALNUMBER=eos11" >> eos11/ceos-config
echo -n "00:1c:73:c10:c6:01" >> eos11/system_mac_address
echo "username arista privilege 15 secret 5 $1$4VjIjfd1$XkUVulbNDESHFzcxDU.Tk1" >> eos11/startup-config
echo "!" >> eos11/startup-config
echo "management api http-commands" >> eos11/startup-config
echo "   no shutdown" >> eos11/startup-config
echo "!" >> eos11/startup-config
echo "daemon TerminAttr" >> eos11/startup-config
echo "   exec /usr/bin/TerminAttr -ingestgrpcurl=192.168.0.5:9910 -cvcompression=gzip -ingestauth=key,atd-lab -smashexcludes=ale,flexCounter,hardware,kni,pulse,strata -ingestexclude=/Sysdb/cell/1/agent,/Sysdb/cell/2/agent -ingestvrf=default -taillogs" >> eos11/startup-config
echo "   no shutdown" >> eos11/startup-config
echo "!" >> eos11/startup-config
echo "service routing protocols model multi-agent" >> eos11/startup-config
echo "interface Management0" >> eos11/startup-config
echo "   ip address 192.168.0.20/24" >> eos11/startup-config
echo "!" >> eos11/startup-config
echo "hostname eos11" >> eos11/startup-config
mkdir eos12
echo "SERIALNUMBER=eos12" >> eos12/ceos-config
echo -n "00:1c:73:c11:c6:01" >> eos12/system_mac_address
echo "username arista privilege 15 secret 5 $1$4VjIjfd1$XkUVulbNDESHFzcxDU.Tk1" >> eos12/startup-config
echo "!" >> eos12/startup-config
echo "management api http-commands" >> eos12/startup-config
echo "   no shutdown" >> eos12/startup-config
echo "!" >> eos12/startup-config
echo "daemon TerminAttr" >> eos12/startup-config
echo "   exec /usr/bin/TerminAttr -ingestgrpcurl=192.168.0.5:9910 -cvcompression=gzip -ingestauth=key,atd-lab -smashexcludes=ale,flexCounter,hardware,kni,pulse,strata -ingestexclude=/Sysdb/cell/1/agent,/Sysdb/cell/2/agent -ingestvrf=default -taillogs" >> eos12/startup-config
echo "   no shutdown" >> eos12/startup-config
echo "!" >> eos12/startup-config
echo "service routing protocols model multi-agent" >> eos12/startup-config
echo "interface Management0" >> eos12/startup-config
echo "   ip address 192.168.0.21/24" >> eos12/startup-config
echo "!" >> eos12/startup-config
echo "hostname eos12" >> eos12/startup-config
mkdir eos13
echo "SERIALNUMBER=eos13" >> eos13/ceos-config
echo -n "00:1c:73:c12:c6:01" >> eos13/system_mac_address
echo "username arista privilege 15 secret 5 $1$4VjIjfd1$XkUVulbNDESHFzcxDU.Tk1" >> eos13/startup-config
echo "!" >> eos13/startup-config
echo "management api http-commands" >> eos13/startup-config
echo "   no shutdown" >> eos13/startup-config
echo "!" >> eos13/startup-config
echo "daemon TerminAttr" >> eos13/startup-config
echo "   exec /usr/bin/TerminAttr -ingestgrpcurl=192.168.0.5:9910 -cvcompression=gzip -ingestauth=key,atd-lab -smashexcludes=ale,flexCounter,hardware,kni,pulse,strata -ingestexclude=/Sysdb/cell/1/agent,/Sysdb/cell/2/agent -ingestvrf=default -taillogs" >> eos13/startup-config
echo "   no shutdown" >> eos13/startup-config
echo "!" >> eos13/startup-config
echo "service routing protocols model multi-agent" >> eos13/startup-config
echo "interface Management0" >> eos13/startup-config
echo "   ip address 192.168.0.22/24" >> eos13/startup-config
echo "!" >> eos13/startup-config
echo "hostname eos13" >> eos13/startup-config
mkdir eos14
echo "SERIALNUMBER=eos14" >> eos14/ceos-config
echo -n "00:1c:73:c13:c6:01" >> eos14/system_mac_address
echo "username arista privilege 15 secret 5 $1$4VjIjfd1$XkUVulbNDESHFzcxDU.Tk1" >> eos14/startup-config
echo "!" >> eos14/startup-config
echo "management api http-commands" >> eos14/startup-config
echo "   no shutdown" >> eos14/startup-config
echo "!" >> eos14/startup-config
echo "daemon TerminAttr" >> eos14/startup-config
echo "   exec /usr/bin/TerminAttr -ingestgrpcurl=192.168.0.5:9910 -cvcompression=gzip -ingestauth=key,atd-lab -smashexcludes=ale,flexCounter,hardware,kni,pulse,strata -ingestexclude=/Sysdb/cell/1/agent,/Sysdb/cell/2/agent -ingestvrf=default -taillogs" >> eos14/startup-config
echo "   no shutdown" >> eos14/startup-config
echo "!" >> eos14/startup-config
echo "service routing protocols model multi-agent" >> eos14/startup-config
echo "interface Management0" >> eos14/startup-config
echo "   ip address 192.168.0.23/24" >> eos14/startup-config
echo "!" >> eos14/startup-config
echo "hostname eos14" >> eos14/startup-config
mkdir eos15
echo "SERIALNUMBER=eos15" >> eos15/ceos-config
echo -n "00:1c:73:c14:c6:01" >> eos15/system_mac_address
echo "username arista privilege 15 secret 5 $1$4VjIjfd1$XkUVulbNDESHFzcxDU.Tk1" >> eos15/startup-config
echo "!" >> eos15/startup-config
echo "management api http-commands" >> eos15/startup-config
echo "   no shutdown" >> eos15/startup-config
echo "!" >> eos15/startup-config
echo "daemon TerminAttr" >> eos15/startup-config
echo "   exec /usr/bin/TerminAttr -ingestgrpcurl=192.168.0.5:9910 -cvcompression=gzip -ingestauth=key,atd-lab -smashexcludes=ale,flexCounter,hardware,kni,pulse,strata -ingestexclude=/Sysdb/cell/1/agent,/Sysdb/cell/2/agent -ingestvrf=default -taillogs" >> eos15/startup-config
echo "   no shutdown" >> eos15/startup-config
echo "!" >> eos15/startup-config
echo "service routing protocols model multi-agent" >> eos15/startup-config
echo "interface Management0" >> eos15/startup-config
echo "   ip address 192.168.0.24/24" >> eos15/startup-config
echo "!" >> eos15/startup-config
echo "hostname eos15" >> eos15/startup-config
mkdir eos16
echo "SERIALNUMBER=eos16" >> eos16/ceos-config
echo -n "00:1c:73:c15:c6:01" >> eos16/system_mac_address
echo "username arista privilege 15 secret 5 $1$4VjIjfd1$XkUVulbNDESHFzcxDU.Tk1" >> eos16/startup-config
echo "!" >> eos16/startup-config
echo "management api http-commands" >> eos16/startup-config
echo "   no shutdown" >> eos16/startup-config
echo "!" >> eos16/startup-config
echo "daemon TerminAttr" >> eos16/startup-config
echo "   exec /usr/bin/TerminAttr -ingestgrpcurl=192.168.0.5:9910 -cvcompression=gzip -ingestauth=key,atd-lab -smashexcludes=ale,flexCounter,hardware,kni,pulse,strata -ingestexclude=/Sysdb/cell/1/agent,/Sysdb/cell/2/agent -ingestvrf=default -taillogs" >> eos16/startup-config
echo "   no shutdown" >> eos16/startup-config
echo "!" >> eos16/startup-config
echo "service routing protocols model multi-agent" >> eos16/startup-config
echo "interface Management0" >> eos16/startup-config
echo "   ip address 192.168.0.25/24" >> eos16/startup-config
echo "!" >> eos16/startup-config
echo "hostname eos16" >> eos16/startup-config
mkdir eos17
echo "SERIALNUMBER=eos17" >> eos17/ceos-config
echo -n "00:1c:73:c16:c6:01" >> eos17/system_mac_address
echo "username arista privilege 15 secret 5 $1$4VjIjfd1$XkUVulbNDESHFzcxDU.Tk1" >> eos17/startup-config
echo "!" >> eos17/startup-config
echo "management api http-commands" >> eos17/startup-config
echo "   no shutdown" >> eos17/startup-config
echo "!" >> eos17/startup-config
echo "daemon TerminAttr" >> eos17/startup-config
echo "   exec /usr/bin/TerminAttr -ingestgrpcurl=192.168.0.5:9910 -cvcompression=gzip -ingestauth=key,atd-lab -smashexcludes=ale,flexCounter,hardware,kni,pulse,strata -ingestexclude=/Sysdb/cell/1/agent,/Sysdb/cell/2/agent -ingestvrf=default -taillogs" >> eos17/startup-config
echo "   no shutdown" >> eos17/startup-config
echo "!" >> eos17/startup-config
echo "service routing protocols model multi-agent" >> eos17/startup-config
echo "interface Management0" >> eos17/startup-config
echo "   ip address 192.168.0.26/24" >> eos17/startup-config
echo "!" >> eos17/startup-config
echo "hostname eos17" >> eos17/startup-config
mkdir eos18
echo "SERIALNUMBER=eos18" >> eos18/ceos-config
echo -n "00:1c:73:c17:c6:01" >> eos18/system_mac_address
echo "username arista privilege 15 secret 5 $1$4VjIjfd1$XkUVulbNDESHFzcxDU.Tk1" >> eos18/startup-config
echo "!" >> eos18/startup-config
echo "management api http-commands" >> eos18/startup-config
echo "   no shutdown" >> eos18/startup-config
echo "!" >> eos18/startup-config
echo "daemon TerminAttr" >> eos18/startup-config
echo "   exec /usr/bin/TerminAttr -ingestgrpcurl=192.168.0.5:9910 -cvcompression=gzip -ingestauth=key,atd-lab -smashexcludes=ale,flexCounter,hardware,kni,pulse,strata -ingestexclude=/Sysdb/cell/1/agent,/Sysdb/cell/2/agent -ingestvrf=default -taillogs" >> eos18/startup-config
echo "   no shutdown" >> eos18/startup-config
echo "!" >> eos18/startup-config
echo "service routing protocols model multi-agent" >> eos18/startup-config
echo "interface Management0" >> eos18/startup-config
echo "   ip address 192.168.0.27/24" >> eos18/startup-config
echo "!" >> eos18/startup-config
echo "hostname eos18" >> eos18/startup-config
mkdir eos19
echo "SERIALNUMBER=eos19" >> eos19/ceos-config
echo -n "00:1c:73:c18:c6:01" >> eos19/system_mac_address
echo "username arista privilege 15 secret 5 $1$4VjIjfd1$XkUVulbNDESHFzcxDU.Tk1" >> eos19/startup-config
echo "!" >> eos19/startup-config
echo "management api http-commands" >> eos19/startup-config
echo "   no shutdown" >> eos19/startup-config
echo "!" >> eos19/startup-config
echo "daemon TerminAttr" >> eos19/startup-config
echo "   exec /usr/bin/TerminAttr -ingestgrpcurl=192.168.0.5:9910 -cvcompression=gzip -ingestauth=key,atd-lab -smashexcludes=ale,flexCounter,hardware,kni,pulse,strata -ingestexclude=/Sysdb/cell/1/agent,/Sysdb/cell/2/agent -ingestvrf=default -taillogs" >> eos19/startup-config
echo "   no shutdown" >> eos19/startup-config
echo "!" >> eos19/startup-config
echo "service routing protocols model multi-agent" >> eos19/startup-config
echo "interface Management0" >> eos19/startup-config
echo "   ip address 192.168.0.28/24" >> eos19/startup-config
echo "!" >> eos19/startup-config
echo "hostname eos19" >> eos19/startup-config
mkdir eos20
echo "SERIALNUMBER=eos20" >> eos20/ceos-config
echo -n "00:1c:73:c19:c6:01" >> eos20/system_mac_address
echo "username arista privilege 15 secret 5 $1$4VjIjfd1$XkUVulbNDESHFzcxDU.Tk1" >> eos20/startup-config
echo "!" >> eos20/startup-config
echo "management api http-commands" >> eos20/startup-config
echo "   no shutdown" >> eos20/startup-config
echo "!" >> eos20/startup-config
echo "daemon TerminAttr" >> eos20/startup-config
echo "   exec /usr/bin/TerminAttr -ingestgrpcurl=192.168.0.5:9910 -cvcompression=gzip -ingestauth=key,atd-lab -smashexcludes=ale,flexCounter,hardware,kni,pulse,strata -ingestexclude=/Sysdb/cell/1/agent,/Sysdb/cell/2/agent -ingestvrf=default -taillogs" >> eos20/startup-config
echo "   no shutdown" >> eos20/startup-config
echo "!" >> eos20/startup-config
echo "service routing protocols model multi-agent" >> eos20/startup-config
echo "interface Management0" >> eos20/startup-config
echo "   ip address 192.168.0.29/24" >> eos20/startup-config
echo "!" >> eos20/startup-config
echo "hostname eos20" >> eos20/startup-config
