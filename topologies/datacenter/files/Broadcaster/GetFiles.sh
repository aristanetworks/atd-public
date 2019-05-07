#!/bin/bash
#script to gather files for lab from Github

# wget from github file(s) if they do not exist
# Configlet(s)

wget https://github.com/aristanetworks/atd-public/raw/Broadcaster-Training/topologies/datacenter/files/Broadcaster/Broadcaster.zip

#Jump Host Files


wget https://raw.githubusercontent.com/aristanetworks/atd-public/Broadcaster-Training/topologies/datacenter/LabFiles/login.py
wget https://raw.githubusercontent.com/aristanetworks/atd-public/Broadcaster-Training/topologies/datacenter/files/Broadcaster/media.py
wget https://raw.githubusercontent.com/aristanetworks/atd-public/Broadcaster-Training/topologies/datacenter/files/Broadcaster/pushHostDefaultConfig.sh
wget https://raw.githubusercontent.com/aristanetworks/atd-public/Broadcaster-Training/topologies/datacenter/files/Broadcaster/pushHostMediaConfig.sh


#HostFiles

wget https://raw.githubusercontent.com/aristanetworks/atd-public/Broadcaster-Training/topologies/datacenter/files/Broadcaster/default-host1.cfg
wget https://raw.githubusercontent.com/aristanetworks/atd-public/Broadcaster-Training/topologies/datacenter/files/Broadcaster/default-host2.cfg
wget https://raw.githubusercontent.com/aristanetworks/atd-public/Broadcaster-Training/topologies/datacenter/files/Broadcaster/media-host1.cfg
wget https://raw.githubusercontent.com/aristanetworks/atd-public/Broadcaster-Training/topologies/datacenter/files/Broadcaster/media-host2.cfg
wget https://raw.githubusercontent.com/aristanetworks/atd-public/Broadcaster-Training/topologies/datacenter/files/Broadcaster/mcast-source.sh
wget https://raw.githubusercontent.com/aristanetworks/atd-public/Broadcaster-Training/topologies/datacenter/files/Broadcaster/mcast-receiver.sh

#CVP Files

wget https://raw.githubusercontent.com/aristanetworks/atd-public/Broadcaster-Training/topologies/datacenter/LabFiles/ConfigureTopology.py

#Move Files
scp /home/arista/ConfigureTopology.py arista@192.168.0.5:
sudo mv /home/arista/media.py /usr/local/bin/media.py
sudo mv /home/arista/login.py /usr/local/bin/login.py
sudo chmod +x /usr/local/bin/media.py
sudo chmod +x /usr/local/bin/login.py
sudo chmod +x /home/arista/configletPushToCVP.sh
sudo chmod +x /home/arista/mcast.source.sh
sudo chmod +x /home/arista/mcast.receiver.sh
echo "pushing configlets to CVP"
bash /home/arista/configletPushToCVP.sh
echo "Applied updated menus - re-login please"

exit 0