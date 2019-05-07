#!/bin/bash
#script to gather files for media lab from Github

# wget from github file(s) if they do not exist
# mkdir if does not exist., all files in /home/arista/Broadcaster/

mkdir /home/arista/Broadcaster/

# Configlet(s)

wget  https://raw.githubusercontent.com/aristanetworks/atd-public/Broadcaster-Training/topologies/datacenter/files/Broadcaster/Broadcaster.zip -O /home/arista/Broadcaster/
#Jump Host Files

wget https://raw.githubusercontent.com/aristanetworks/atd-public/Broadcaster-Training/topologies/datacenter/LabFiles/login.py
wget https://raw.githubusercontent.com/aristanetworks/atd-public/Broadcaster-Training/topologies/datacenter/files/Broadcaster/media.py
wget https://raw.githubusercontent.com/aristanetworks/atd-public/Broadcaster-Training/topologies/datacenter/files/Broadcaster/pushHostDefaultConfig.sh
wget https://raw.githubusercontent.com/aristanetworks/atd-public/Broadcaster-Training/topologies/datacenter/files/Broadcaster/pushHostMediaConfig.sh
wget https://raw.githubusercontent.com/aristanetworks/atd-public/Broadcaster-Training/topologies/datacenter/files/Broadcaster/configletPushToCVP.sh


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
scp /home/arista/Broadcaster/ConfigureTopology.py arista@192.168.0.5:
sudo mv /home/arista/Broadcaster/media.py /usr/local/bin/media.py
sudo mv /home/arista/Broadcaster/login.py /usr/local/bin/login.py
sudo chmod +x /usr/local/bin/media.py
sudo chmod +x /usr/local/bin/login.py
sudo chmod +x /home/arista/Broadcaster/configletPushToCVP.sh
sudo chmod +x /home/arista/Broadcaster/mcast-source.sh
sudo chmod +x /home/arista/Broadcaster/mcast-receiver.sh
echo "pushing configlets to CVP"
bash /home/arista/Broadcaster/configletPushToCVP.sh
echo "Applied updated menus - re-login please"

exit 0
