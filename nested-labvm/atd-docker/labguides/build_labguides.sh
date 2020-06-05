#!/bin/bash

TOPO=$(cat /etc/atd/ACCESS_INFO.yaml | shyaml get-value topology)
ARISTA_PWD=$(cat /etc/atd/ACCESS_INFO.yaml | shyaml get-value login_info.jump_host.pw)

# Clean up previous stuff to make sure it's current
#rm -rf /home/arista/labguides/src/build

cp -r /opt/atd/topologies/$TOPO/labguides/* /root/labguides/src/

# Update the Arista user password for connecting to the labvm
sed -i "s/{REPLACE_PWD}/$ARISTA_PWD/g" /root/labguides/src/source/connecting.rst
sed -i "s/{REPLACE_PWD}/$ARISTA_PWD/g" /root/labguides/src/source/programmability_connecting.rst

# chown -R arista:arista /home/arista/labguides/src/

# Build the lab guides html files
cd /root/labguides/src
make html
sphinx-build -b latex source build

# Build the lab guides PDF
make latexpdf

# Put the new HTML and PDF in the proper directories
mv /root/labguides/src/build/latex/ATD.pdf /root/labguides/web/
mv /root/labguides/src/build/html/* /root/labguides/web/ 

echo Labguide build complete

sleep infinity
