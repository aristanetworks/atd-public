#!/bin/bash

echo "enabling eAPI"
#enable eAPI if host is disabled
ssh -t 192.168.0.31 "bash FastCli -p15 -c $'enable\n config\n  management api http-commands\n no shut'"
ssh -t 192.168.0.32 "bash FastCli -p15 -c $'enable\n config\n  management api http-commands\n no shut'"

echo "copying configs"
#copy files over
scp /home/arista/media-host1.cfg 192.168.0.31:
scp /home/arista/media-host2.cfg 192.168.0.32:
scp /home/arista/mcast.source.sh 192.168.0.31:
scp /home/arista/mcast.receiver.sh 192.168.0.32:

echo "Loading Configs"
#config replace
ssh -t 192.168.0.31 "bash FastCli -p15 -c $'enable\n configure replace flash:media-host1.cfg'"
ssh -t 192.168.0.32 "bash FastCli -p15 -c $'enable\n configure replace flash:media-host2.cfg'"
