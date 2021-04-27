#!/bin/bash

eval $( fixuid )

# Start Configlet Sync
python kvm-topo-builder.py