#!/bin/bash
#script to gather files for lab from Github

# wget from github file(s) if they do not exist
# Configlet(s)

wget https://github.com/aristanetworks/atd-public/raw/Broadcaster-Training/topologies/datacenter/configlets/Broadcaster.zip

#Jump Host Files

wget https://github.com/aristanetworks/atd-public/raw/Broadcaster-Training/topologies/datacenter/LabFiles/login.py
wget https://github.com/aristanetworks/atd-public/raw/Broadcaster-Training/topologies/datacenter/LabFiles/Broadcaster/media.py
wget https://github.com/aristanetworks/atd-public/raw/Broadcaster-Training/topologies/datacenter/LabFiles/Broadcaster/configletPushToCVP.sh
wget https://github.com/aristanetworks/atd-public/raw/Broadcaster-Training/topologies/datacenter/LabFiles/Broadcaster/pushHostDefaultConfig.sh
wget https://github.com/aristanetworks/atd-public/raw/Broadcaster-Training/topologies/datacenter/LabFiles/Broadcaster/pushHostMediaConfig.sh



#HostFiles

wget https://github.com/aristanetworks/atd-public/raw/Broadcaster-Training/topologies/datacenter/LabFiles/Broadcaster/default-host1.cfg
wget https://github.com/aristanetworks/atd-public/raw/Broadcaster-Training/topologies/datacenter/LabFiles/Broadcaster/default-host2.cfg
wget https://github.com/aristanetworks/atd-public/raw/Broadcaster-Training/topologies/datacenter/LabFiles/Broadcaster/media-host1.cfg
wget https://github.com/aristanetworks/atd-public/raw/Broadcaster-Training/topologies/datacenter/LabFiles/Broadcaster/media-host2.cfg
wget https://github.com/aristanetworks/atd-public/raw/Broadcaster-Training/topologies/datacenter/LabFiles/Broadcaster/mcast.source.sh
wget https://github.com/aristanetworks/atd-public/raw/Broadcaster-Training/topologies/datacenter/LabFiles/Broadcaster/mcast.receiver.sh

#CVP Files

wget https://github.com/aristanetworks/atd-public/raw/Broadcaster-Training/topologies/datacenter/LabFiles/ConfigureTopology.py

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
exit