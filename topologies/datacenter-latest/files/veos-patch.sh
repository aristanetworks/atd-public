#!/bin/bash

echo 'Gatering necessary files.'
mkdir /home/arista/patch
git clone git@github.com:/aristanetworks/atd.git /home/arista/patch/

cd /home/arista/patch

git checkout -b veos-patch origin/veos-patch

cd patches/4.23.0.1F

echo "Adding patch file spine and leaf nodes.."
for i in 192.168.0.10 192.168.0.11 192.168.0.14 192.168.0.15 192.168.0.16 192.168.0.17
do
scp KernelVersion-patch-bug431736.i686.rpm arista@$i:/mnt/flash/
ssh arista@$i copy flash:/KernelVersion-patch-bug431736.i686.rpm extension:/
ssh arista@$i extension KernelVersion-patch-bug431736.i686.rpm
done
echo "Done!"
