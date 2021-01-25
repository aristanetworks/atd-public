#!/bin/bash

BRANCH=$(cat /etc/atd/ATD_REPO.yaml | python3 -m shyaml get-value atd-public-branch)
TOPO=$(cat /etc/atd/ACCESS_INFO.yaml | python3 -m shyaml get-value topology)
APWD=$(cat /etc/atd/ACCESS_INFO.yaml | python3 -m shyaml get-value login_info.jump_host.pw)

if  [ -z "$(cat /etc/atd/ATD_REPO.yaml | grep repo)" ]
then
    REPO="https://github.com/aristanetworks/atd-public.git"
else
    REPO=$(cat /etc/atd/ATD_REPO.yaml | python3 -m shyaml get-value public-repo)
fi

if [ "$(cat /etc/atd/ACCESS_INFO.yaml | grep eos_type)" ]
then
    EOS_TYPE=$(cat /etc/atd/ACCESS_INFO.yaml | python3 -m shyaml get-value eos_type)
else
    EOS_TYPE=veos
fi

rm -rf /opt/atd

git clone --branch $BRANCH $REPO /opt/atd

# Update atdUpdate service

rsync -av /opt/atd/nested-labvm/services/atdUpdate/atdUpdate.sh /usr/local/bin/

# Update ssh-key in EOS configlet for Arista user
ARISTA_SSH=$(cat /home/arista/.ssh/id_rsa.pub)

sed -i "/username arista ssh-key/cusername arista ssh-key ${ARISTA_SSH}" /opt/atd/topologies/$TOPO/configlets/ATD-INFRA

# Update arista user password for Guacamole

find /opt/atd/nested-labvm/atd-docker/*  -type f -print0 | xargs -0 sed -i "s/{ARISTA_REPLACE}/$APWD/g" 
find /opt/atd/topologies/$TOPO/files/*  -type f -print0 | xargs -0 sed -i "s/{ARISTA_REPLACE}/$APWD/g" 



# Update the base configlets for ceos/veos mgmt numbering

if [ $EOS_TYPE == 'ceos' ]
then
    sed -i 's/Management1/Management0/g' /opt/atd/topologies/$TOPO/configlets/*
fi

# Copy topo image to app directory
rsync -av /opt/atd/topologies/$TOPO/atd-topo.png /opt/atd/topologies/$TOPO/files/apps/uilanding

# Add files to arista home
rsync -av --update /opt/atd/topologies/$TOPO/files/ /home/arista/arista-dir
rsync -av /opt/atd/topologies/$TOPO/files/infra /home/arista/

# Perform check if there is a scripts directory
if [ -d "/opt/atd/topologies/$TOPO/files/scripts" ]
then
    rsync -av /opt/atd/topologies/$TOPO/files/scripts /home/arista/GUI_Desktop/
fi

# Perform a check for the repo directory for datacenter
if ! [ -d "/home/arista/arista-dir/apps/coder/labfiles/lab6/repo" ] && [ $TOPO == "datacenter" ]
then
    mkdir -p /home/arista/arista-dir/apps/coder/labfiles/lab6/repo
    cd /home/arista/arista-dir/apps/coder/labfiles/lab6/repo
    git init --bare
fi

chown -R arista:arista /home/arista

# Update ATD containers

cd /opt/atd/nested-labvm/atd-docker

su atdadmin -c 'bash docker_build.sh'

# Setting arista user ids for coder container
export ArID=$(id -u arista)
export ArGD=$(id -g arista)

/usr/local/bin/docker-compose up -d --remove-orphans --force-recreate

echo 'y' | docker image prune

systemctl restart sshd

# if cEOS Startup present, run it
if [ -f "/opt/ceos/scripts/.ceos.txt" ]
then
    while : ; do
        [[ -f "/opt/ceos/scripts/Startup.sh" ]] && break
        echo "Pausing until file exists."
        sleep 1
    done
    bash /opt/ceos/scripts/Startup.sh
fi
