#!/bin/bash

# Find out what topology is running
TOPO=$(cat /etc/ACCESS_INFO.yaml | shyaml get-value topology)
ARISTA_PWD=$(cat /etc/ACCESS_INFO.yaml | shyaml get-value login_info.jump_host.pw)

# Get the current arista password:
for i in $(seq 1 $(cat /etc/ACCESS_INFO.yaml | shyaml get-length login_info.veos))
do
TMP=$((i-1))
if [ $( cat /etc/ACCESS_INFO.yaml | shyaml get-value login_info.veos.$TMP.user ) = "arista" ]
then
    LAB_ARISTA_PWD=$( cat /etc/ACCESS_INFO.yaml | shyaml get-value login_info.veos.$TMP.pw )
    AR_LEN=$( echo -n $LAB_ARISTA_PWD | wc -m)
fi
done


# Adding in temporary pip install/upgrade for rCVP API
pip install rcvpapi
pip install --upgrade rcvpapi

# Install Python3-pip
apt install python3-pip -y

# Install python3 ruamel.yaml
pip3 install ruamel.yaml bs4

# Clean up previous stuff to make sure it's current
rm -rf /var/www/html/atd/labguides/

# Make sure login.py and ConfigureTopology.py is current
cp /tmp/atd/topologies/all/login.py /usr/local/bin/login.py
cp /tmp/atd/topologies/all/ConfigureTopology.py /usr/local/bin/ConfigureTopology.py
cp /tmp/atd/topologies/all/labModule.py /usr/local/bin/labModule.py
chmod +x /usr/local/bin/ConfigureTopology.py
chmod +x /usr/local/bin/labModule.py

# Add files to arista home
rsync -av /tmp/atd/topologies/$TOPO/files/ /home/arista

# Update arista password and copy the updated guacamole user-mapping.xml file 
sed -i "s/{REPLACE_ARISTA}/$LAB_ARISTA_PWD/g" /home/arista/infra/user-mapping.xml
cp /home/arista/infra/user-mapping.xml /etc/guacamole/

# Update file permissions in /home/arista
chown -R arista:arista /home/arista

# Update all occurrences for the arista lab credentials

if [ $AR_LEN == 7 ]
then
        FIRST='|  ``password: "{REPLACE_ARISTA}"``           |'
        FREPLACE='| ``password: "'$LAB_ARISTA_PWD'"``           |'
        SECOND='|  Sets the password to ``{REPLACE_ARISTA}``  |'
        FSECOND='| Sets the password to ``'$LAB_ARISTA_PWD'``  |'
        sed -i "s/$FIRST/$FREPLACE/g" /tmp/atd/topologies/$TOPO/labguides/source/*.rst
        sed -i "s/$SECOND/$FSECOND/g" /tmp/atd/topologies/$TOPO/labguides/source/*.rst
fi
sed -i "s/{REPLACE_ARISTA}/$LAB_ARISTA_PWD/g" /tmp/atd/topologies/$TOPO/labguides/source/*.rst

# Update the Arista user password for connecting to the labvm
sed -i "s/{REPLACE_PWD}/$ARISTA_PWD/g" /tmp/atd/topologies/$TOPO/labguides/source/*.rst

# Perform check for module lab
if [ ! -z "$(grep "default_lab" /etc/ACCESS_INFO.yaml)" ] && [ -d "/home/arista/modules" ]
then
    MODULE=$(cat /etc/ACCESS_INFO.yaml | shyaml get-value default_lab)
    if [ $MODULE != "none" ]
    then
        # ==== TODO ====
        # Add in code to modify NGINX config and restart NGINX service
        #
        # Code to start the lab module page
        nohup labModule.py &
    fi
fi

# Build the lab guides html files
cd /tmp/atd/topologies/$TOPO/labguides
make html
sphinx-build -b latex source build

# Build the lab guides PDF
make latexpdf
mkdir /var/www/html/atd/labguides/

# Put the new HTML and PDF in the proper directories
mv /tmp/atd/topologies/$TOPO/labguides/build/latex/ATD.pdf /var/www/html/atd/labguides/
mv /tmp/atd/topologies/$TOPO/labguides/build/html/* /var/www/html/atd/labguides/ && chown -R www-data:www-data /var/www/html/atd/labguides
