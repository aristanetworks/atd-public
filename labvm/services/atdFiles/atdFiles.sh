#!/bin/bash

# Find out what topology is running
TOPO=`cat /etc/ACCESS_INFO.yaml | shyaml get-value topology`

# Clean up previous stuff to make sure it's current
rm -rf /var/www/html/atd/labguides/
rm -rf /home/arista/

# Clone the atd-public repo
git clone https://github.com/aristanetworks/atd-public.git /tmp/atd

# Add files to arista home
cp -R /tmp/atd/topologies/$TOPO/files/* /home/arista

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

# Clean up the repo, no need to keep it
rm -rf /tmp/atd
