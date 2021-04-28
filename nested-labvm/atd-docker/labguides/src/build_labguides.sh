#!/bin/bash

while [ $(cat /etc/atd/ACCESS_INFO.yaml | shyaml get-value login_info.jump_host.pw) == 'REPLACE_PWD' ]
do
    echo "Password has not been updated yet. sleeping..."
    sleep 10
done

TOPO=$(cat /etc/atd/ACCESS_INFO.yaml | shyaml get-value topology)
ARISTA_PWD=$(cat /etc/atd/ACCESS_INFO.yaml | shyaml get-value login_info.jump_host.pw)
EOS_TYPE=$(cat /etc/atd/ACCESS_INFO.yaml | python3 -m shyaml get-value eos_type)

# Clean up previous stuff to make sure it's current
#rm -rf /home/arista/labguides/build

cp -r /opt/atd/topologies/$TOPO/labguides/* /root/labguides/

# Update the Arista user password for connecting to the labvm
find /root/labguides/source/*  -type f -print0 | xargs -0 sed -i "s/{REPLACE_PWD}/$ARISTA_PWD/g"

if [ $EOS_TYPE == 'ceos' ]
then
  find /root/labguides/source/*  -type f -print0 | xargs -0 sed -i "s/Management1/Management0/g"
fi

# chown -R arista:arista /home/arista/labguides/src/

# Build the lab guides html files
cd /root/labguides/
make html
sphinx-build -b latex source build

# Build the lab guides PDF
make latexpdf LATEXOPTS=-interaction=nonstopmode

rm -r /root/labguides/web/*

# Put the new HTML and PDF in the proper directories
mv /root/labguides/build/latex/ATD.pdf /root/labguides/web/
mv /root/labguides/build/html/* /root/labguides/web/ 

echo Labguide build complete

cd /root

python labguides.py
