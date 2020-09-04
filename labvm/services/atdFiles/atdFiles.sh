#!/bin/bash

# Add in while wait check until ACCESS_INFO is available
   
while : ; do
    [[ -f "/etc/ACCESS_INFO.yaml" ]] && break
    echo "Pausing until file exists."
    sleep 1
done

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

# Add current Node.js repo
curl -sL https://deb.nodesource.com/setup_14.x | sudo bash -

# Install Python3-pip
apt install python3-pip nodejs -y

# Install python3 modules
pip3 install --upgrade pip
pip3 install ruamel.yaml bs4 tornado scp paramiko rcvpapi

# Setup NPM and webssh2
npm install forever -g
git clone https://github.com/billchurch/webssh2.git /opt/webssh2
cp /tmp/atd/topologies/all/webssh2-config.json /opt/webssh2/app/config.json
sed -i "s/{REPLACE_ARISTA}/$LAB_ARISTA_PWD/g" /opt/webssh2/app/config.json
npm --prefix /opt/webssh2/app install --production
npm --prefix /opt/webssh2/app install forever
forever start /opt/webssh2/app/index.js

# Clean up previous stuff to make sure it's current
rm -rf /var/www/html/atd/labguides/

# Make sure login.py and ConfigureTopology.py is current
mkdir /usr/local/bin/ConfigureTopology
cp /tmp/atd/topologies/all/ConfigureTopology.py /usr/local/bin/ConfigureTopology/ConfigureTopology.py
cp /tmp/atd/topologies/all/__init__.py /usr/local/bin/ConfigureTopology/__init__.py
cp /tmp/atd/topologies/all/login.py /usr/local/bin/login.py
cp /tmp/atd/topologies/all/labUI.py /usr/local/bin/labUI.py
chmod +x /usr/local/bin/labUI.py

# Copy over new nginx config if it exists and restart service
if [ ! -z '/tmp/atd/topologies/all/nginx.conf' ]
then
    cp /tmp/atd/topologies/all/nginx.conf /etc/nginx/sites-enabled/default
    systemctl restart nginx
fi

# Add files to arista home
rsync -av /tmp/atd/topologies/$TOPO/files/ /home/arista

# Update arista password and copy the updated guacamole user-mapping.xml file 
sed -i "s/{REPLACE_ARISTA}/$LAB_ARISTA_PWD/g" /home/arista/infra/user-mapping.xml
cp /home/arista/infra/user-mapping.xml /etc/guacamole/

# Update file permissions in /home/arista
chown -R arista:arista /home/arista

# Update file permissions in /home/aristagui

chown -R aristagui:aristagui /home/aristagui

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
if [ ! -z "$(grep "app" /etc/ACCESS_INFO.yaml)" ] && [ -d "/home/arista/modules" ]
then
    MODULE=$(cat /etc/ACCESS_INFO.yaml | shyaml get-value app)
    if [ $MODULE != "none" ]
    then
        # Code to start the lab module page
        nohup labUI.py &
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
mv /tmp/atd/topologies/$TOPO/labguides/build/html/* /var/www/html/atd/labguides/

# Copy over the modules images to the web directory
if [ -d /tmp/atd/topologies/$TOPO/labguides/source/images/modules ]
then
    cp -r /tmp/atd/topologies/$TOPO/labguides/source/images/modules /var/www/html/atd/labguides/_images/
fi

# Change the permission for the web directory files
chown -R www-data:www-data /var/www/html/atd/labguides
