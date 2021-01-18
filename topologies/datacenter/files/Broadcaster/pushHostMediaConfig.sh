#!/bin/bash

touch ~/enable-media

# echo "Prepping host vms and enabling eAPI"
# ssh -t 192.168.0.31 "
# enable
# configure
# aaa authorization exec default local"

# ssh -t 192.168.0.32 "
# enable
# configure
# aaa authorization exec default local"

echo "Updating File Permissions"
#sudo chown -R arista:arista /home/arista/Broadcaster/
# chmod +x /home/arista/Broadcaster/configletPushToCVP.sh
chmod +x /home/arista/Broadcaster/mcast-source.sh
chmod +x /home/arista/Broadcaster/mcast-receiver.sh

echo "Copying Configs"
#copy files over
# scp /home/arista/Broadcaster/media-host1.cfg 192.168.0.31:/mnt/flash
# scp /home/arista/Broadcaster/media-host2.cfg 192.168.0.32:/mnt/flash
# scp /home/arista/Broadcaster/default-host1.cfg 192.168.0.31:/mnt/flash
# scp /home/arista/Broadcaster/default-host2.cfg 192.168.0.32:/mnt/flash
scp /home/arista/Broadcaster/mcast-source.sh -o StrictHostKeyChecking=no 192.168.0.17:/mnt/flash
scp /home/arista/Broadcaster/mcast-receiver.sh -o StrictHostKeyChecking=no 192.168.0.18:/mnt/flash

# echo "Loading Configs"
# #config replace
# ssh -t 192.168.0.31 "configure replace flash:media-host1.cfg"
# ssh -t 192.168.0.32 "configure replace flash:media-host2.cfg"

