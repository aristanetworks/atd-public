#!/bin/bash
#
# ---------  CONFIGURATION --------
LOCAL_IP="DMF_SWITCH_IP"
LOCAL_NETMASK="255.255.255.0"
LOCAL_GATEWAY="192.168.0.1"
CONTROLER_IP="DMF_CONTROLLER_IP"
NUMBER_OF_INTERFACES=INTERFACE_COUNT_REPLACE # eth0 management, others for I/O

MAC_ADDRESS_INDEX=MAC_ADDRESS_INDEX_REPLACE  #meaning of index below
# 1 00:00:00:00:00:0a
# 2 00:00:00:00:00:0b
# 3 00:00:00:00:00:0c
# 4 etc....
# 
# -------------------------------
# 1 - start vDMF switch
# 2 - deploy CONFIGURE.sh (edit vi CONFIGURE.sh)
# ------------------------------------
#
# Modify MININET python configuration file (MAC & number of interfafes) 

echo "Starting DMF Configuration"
# CHECK IF DMF IS CONFIGURED
if [ -f ".dmfConfigured" ]; then
    echo "DMF is Configured already"
    exit
fi

cp bmf-topo_A.py bmf-topo.py
dpid_index_REPLACE=$((9+MAC_ADDRESS_INDEX))
echo "        dpid_index = $dpid_index_REPLACE" >> bmf-topo.py
echo ""  >> bmf-topo.py
echo "        info( '*** Adding filter switch\n')"  >> bmf-topo.py
echo "        filter_switches = []"  >> bmf-topo.py
echo "        for filter in range(1, num_filter+1):"  >> bmf-topo.py
echo "            filter_switches.append(add_switch('F'+\`filter\`, 0, dpid_index))"  >> bmf-topo.py
echo "            dpid_index += 1"  >> bmf-topo.py
echo ""  >> bmf-topo.py
echo "#---  JGR Add physical interface" >> bmf-topo.py
echo "        info( 'JGR: Adding physical interfaces\n' )" >> bmf-topo.py
echo"" >> bmf-topo.py

IF_NUMBER=1
while ((IF_NUMBER < NUMBER_OF_INTERFACES))
  do
    echo "        intfName = 'eth$IF_NUMBER'" >> bmf-topo.py
    echo "        _intf = Intf(intfName, node=filter_switches[0])" >> bmf-topo.py
    echo "" >> bmf-topo.py
    ((IF_NUMBER=IF_NUMBER+1))
  done
cat bmf-topo_Z.py >> bmf-topo.py
cp bmf-topo.py /opt/t6-mininet/bmf-topo.py

# Modify script starting controler
cp 1_0 1
sed -i "s/CONTROLER_IP/$CONTROLER_IP/g" "1"
sudo cp 1 /usr/local/bin/1

# modify LOCAL_IP & add interfaces
cp interfaces_0 interfaces
echo "address $LOCAL_IP" >> interfaces
echo "netmask $LOCAL_NETMASK" >> interfaces
echo "gateway $LOCAL_GATEWAY" >> interfaces
echo ""

IF_NUMBER=1
while ((IF_NUMBER < NUMBER_OF_INTERFACES)) 
  do
    echo "auto eth$IF_NUMBER" >> interfaces
    echo '' >> interfaces
    ((IF_NUMBER=IF_NUMBER+1))

  done
sudo cp interfaces /etc/network/interfaces
touch .dmfConfigured