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

echo "copying configs"
#copy files over
scp /home/arista/Broadcaster/default-host1.cfg 192.168.0.31:/mnt/flash
scp /home/arista/Broadcaster/default-host2.cfg 192.168.0.32:/mnt/flash

echo "Loading Configs"
#config replace
ssh -t 192.168.0.31 "configure replace flash:default-host1.cfg"
ssh -t 192.168.0.32 "configure replace flash:default-host2.cfg"
