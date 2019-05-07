#!/bin/bash

echo "Prepping host vms and enabling eAPI"
ssh -t 192.168.0.31 "
enable
configure
aaa authorization exec default local
management api http-commands
no shut"
ssh -t 192.168.0.32 "
enable
configure
aaa authorization exec default local
management api http-commands
no shut"

echo "Updating File Permissions"
chmod +x /home/arista/Broadcaster/media.py
chmod +x /home/arista/Broadcaster/configletPushToCVP.sh
chmod +x /home/arista/Broadcaster/mcast-source.sh
chmod +x /home/arista/Broadcaster/mcast-receiver.sh

echo "Moving media.py"
#move vs copy? could error out this script on next run.
sudo mv /home/arista/Broadcaster/media.py /usr/local/bin/

echo "Pushing configlets to CVP"
bash /home/arista/Broadcaster/configletPushToCVP.sh

echo "Copying Configs"
#copy files over
scp /home/arista/Broadcaster/media-host1.cfg 192.168.0.31:/mnt/flash
scp /home/arista/Broadcaster/media-host2.cfg 192.168.0.32:/mnt/flash
scp /home/arista/Broadcaster/mcast-source.sh 192.168.0.31:/mnt/flash
scp /home/arista/Broadcaster/mcast-receiver.sh 192.168.0.32:/mnt/flash

echo "Loading Configs"
#config replace
ssh -t 192.168.0.31 "configure replace flash:media-host1.cfg"
ssh -t 192.168.0.32 "configure replace flash:media-host1.cfg"

