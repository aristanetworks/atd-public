#!/bin/bash

echo "Enabling eAPI"
#enable eAPI if host is disabled
ssh -t 192.168.0.31 "bash FastCli -p15 -c $'enable\n config\n  management api http-commands\n no shut'"
ssh -t 192.168.0.32 "bash FastCli -p15 -c $'enable\n config\n  management api http-commands\n no shut'"

echo "Updating File Permissions"
chmod +x /home/arista/Broadcaster/media.py
chmod +x /home/arista/Broadcaster/configletPushToCVP.sh
chmod +x /home/arista/Broadcaster/mcast.source.sh
chmod +x /home/arista/Broadcaster/mcast.receiver.sh

echo "Moving media.py"
sudo mv /home/arista/Broadcaster/media.py /usr/local/bin/

echo "Pushing configlets to CVP"
bash /home/arista/Broadcaster/configletPushToCVP.sh

echo "Copying Configs"
#copy files over
scp /home/arista/media-host1.cfg 192.168.0.31:
scp /home/arista/media-host2.cfg 192.168.0.32:
scp /home/arista/mcast.source.sh 192.168.0.31:
scp /home/arista/mcast.receiver.sh 192.168.0.32:

echo "Loading Configs"
#config replace
ssh -t 192.168.0.31 "bash FastCli -p15 -c $'enable\n configure replace flash:media-host1.cfg'"
ssh -t 192.168.0.32 "bash FastCli -p15 -c $'enable\n configure replace flash:media-host2.cfg'"
