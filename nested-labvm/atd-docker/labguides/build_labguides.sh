#!/bin/bash

TOPO=$(cat /etc/ACCESS_INFO.yaml | shyaml get-value topology)
ARISTA_PWD=$(cat /etc/ACCESS_INFO.yaml | shyaml get-value login_info.jump_host.pw)

# Clean up previous stuff to make sure it's current
#rm -rf /home/arista/labguides/src/build

cp -r /tmp/atd/topologies/$TOPO/labguides/* /home/arista/labguides/src/

# Update the Arista user password for connecting to the labvm
sed -i "s/{REPLACE_PWD}/$ARISTA_PWD/g" /home/arista/labguides/src/source/connecting.rst
sed -i "s/{REPLACE_PWD}/$ARISTA_PWD/g" /home/arista/src/source/programmability_connecting.rst

# chown -R arista:arista /home/arista/labguides/src/

# Build the lab guides html files
cd /root/labguides/src
make html
sphinx-build -b latex source build

# Build the lab guides PDF
make latexpdf

# Put the new HTML and PDF in the proper directories
mv /home/arista/labguides/src/build/latex/ATD.pdf /home/arista/labguides/web/
mv /home/arista/labguides/src/build/html/* /home/arista/labguides/web/ 

echo Labguide build complete

sleep infinity
