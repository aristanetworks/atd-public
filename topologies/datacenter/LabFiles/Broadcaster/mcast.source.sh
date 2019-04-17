#!/bin/bash
#echo Starting source 239.103,1,1-3 for 1800 seconds

for i in {1..3} ; do
    IP='239.103.1'
    IP=$IP.$i
    iperf -c $IP -u -b 0.25m -T 10 -t 1800 -i 1 &
done