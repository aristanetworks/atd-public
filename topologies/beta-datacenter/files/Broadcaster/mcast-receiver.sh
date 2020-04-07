#!/bin/bash
echo "Starting Receivers"
sudo ip route add 239.103.1.1/32 dev et2
sudo ip route add 239.103.1.2/32 dev et2
sudo ip route add 239.103.1.3/32 dev et2
iperf -s -u -B 239.103.1.1 -i 1 &
iperf -s -u -B 239.103.1.2 -i 1 &
