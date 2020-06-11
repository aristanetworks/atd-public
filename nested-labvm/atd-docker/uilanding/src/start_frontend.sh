#!/bin/bash

TOPO=$(cat /etc/atd/ACCESS_INFO.yaml | shyaml get-value topology)
ARISTA_PWD=$(cat /etc/atd/ACCESS_INFO.yaml | shyaml get-value login_info.jump_host.pw)

# Clean up previous stuff to make sure it's current
# rm -rf /home/arista/labguides/src/build
rm -rf /opt/topo/html/labguides/*

cp -r /opt/atd/topologies/$TOPO/labguides/* /root/labguides/

# Update the Arista user password for connecting to the labvm
sed -i "s/{REPLACE_PWD}/$ARISTA_PWD/g" /root/labguides/src/source/connecting.rst
sed -i "s/{REPLACE_PWD}/$ARISTA_PWD/g" /root/labguides/src/source/programmability_connecting.rst

# chown -R arista:arista /home/arista/labguides/src/

# Build the lab guides html files
cd /root/labguides
make html
sphinx-build -b latex source build

# Build the lab guides PDF
make latexpdf

# Put the new HTML and PDF in the proper directories
mv /root/labguides/build/latex/ATD.pdf /opt/topo/html/labguides/
mv /root/labguides/build/html/* /opt/topo/html/labguides/ 

echo Labguide build complete

uilanding
