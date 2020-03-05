#!/bin/bash
#echo Starting source 239.103.1.1-3 for 1800 seconds
echo "Starting Sources"
#adding routes in kernel to prefer et1 instead of ATD underlay interface
sudo ip route add 239.103.1.1/32 dev et1
sudo ip route add 239.103.1.2/32 dev et1
sudo ip route add 239.103.1.3/32 dev et1

for i in {1..3} ; do
    IP='239.103.1'
    IP=$IP.$i
    iperf -c $IP -u -b 0.125m -T 10 -t 1800 -i 1 -&
done
