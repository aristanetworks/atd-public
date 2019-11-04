#!/bin/bash
iperf -s -u -B 239.103.1.1 -i 1 &
iperf -s -u -B 239.103.1.2 -i 1 &