#!/bin/bash

# Find out what topology is running
TOPO=$(cat /etc/ACCESS_INFO.yaml | shyaml get-value topology)
ARISTA_PWD=$(cat /etc/ACCESS_INFO.yaml | shyaml get-value login_info.jump_host.pw)

# Clean up previous stuff to make sure it's current
rm -rf /var/www/html/atd/labguides/

# Make sure login.py and ConfigureTopology.py is current
cp -u /tmp/atd/topologies/all/login.py /usr/local/bin/login.py
cp -u /tmp/atd/topologies/all/ConfigureTopology.py /usr/local/bin/ConfigureTopology.py

# Add files to arista home
rsync -av /tmp/atd/topologies/$TOPO/files/ /home/arista

# Update file permissions in /home/arista
chown -R arista:arista /home/arista

# Update the Arista user password for connecting to the labvm
sed -i "s/{REPLACE_PWD}/$ARISTA_PWD/g" /tmp/atd/labguides/source/connecting.rst
sed -i "s/{REPLACE_PWD}/$ARISTA_PWD/g" /tmp/atd/labguides/source/programmability_connecting.rst

# Copy over ConfigureTopology to CVP
scp /home/arista/ConfigureTopology.py arista@192.168.0.5/~/

# Build the lab guides html files
cd /tmp/atd/labguides
make html
sphinx-build -b latex source build

# Build the lab guides PDF
make latexpdf
mkdir /var/www/html/atd/labguides/

# Put the new HTML and PDF in the proper directories
mv /tmp/atd/labguides/build/latex/ATD.pdf /var/www/html/atd/labguides/
mv /tmp/atd/labguides/build/html/* /var/www/html/atd/labguides/ && chown -R www-data:www-data /var/www/html/atd/labguides
