#!/bin/bash

echo "Starting atdStartup"

TOPO=$(cat /etc/atd/ACCESS_INFO.yaml | python3 -m shyaml get-value topology)
APWD=$(cat /etc/atd/ACCESS_INFO.yaml | python3 -m shyaml get-value login_info.jump_host.pw)

if [ "$(cat /etc/atd/ACCESS_INFO.yaml | grep eos_type)" ]
then
    EOS_TYPE=$(cat /etc/atd/ACCESS_INFO.yaml | python3 -m shyaml get-value eos_type)
else
    EOS_TYPE=veos
fi

# Update ssh-key in EOS configlet for Arista user
ARISTA_SSH=$(cat /home/arista/.ssh/id_rsa.pub)

sed -i "/username arista ssh-key/cusername arista ssh-key ${ARISTA_SSH}" /opt/atd/topologies/$TOPO/configlets/ATD-INFRA

# Update arista user password for Guacamole

find /opt/atd/nested-labvm/atd-docker/*  -type f -print0 | xargs -0 sed -i "s/{ARISTA_REPLACE}/$APWD/g" 
find /opt/atd/topologies/$TOPO/files/*  -type f -print0 | xargs -0 sed -i "s/{ARISTA_REPLACE}/$APWD/g" 


# Perform check to see if docker auth file exists
if ! [ -f "/home/atdadmin/.docker/config.json" ]
then
    echo "Docker auth file not found, creating..."
    gcloud auth configure-docker gcr.io,us.gcr.io --quiet
    su atdadmin -c "gcloud auth configure-docker gcr.io,us.gcr.io --quiet"
fi

# Update the base configlets for ceos/veos mgmt numbering

if [ $EOS_TYPE == 'ceos' ]
then
    sed -i 's/Management1/Management0/g' /opt/atd/topologies/$TOPO/configlets/*
fi

# Copy topo image to app directory
rsync -av /opt/atd/topologies/$TOPO/atd-topo.png /opt/atd/topologies/$TOPO/files/apps/uilanding

# Add files to arista home
rsync -av --update /opt/atd/topologies/$TOPO/files/ /home/arista/arista-dir
# rsync -av /opt/atd/topologies/$TOPO/files/infra /home/arista/

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

# Copy Static cEOS startup-configs if present
if [ -d "/opt/atd/topologies/$TOPO/files/ceos" ]
then
    rsync -av /opt/atd/topologies/$TOPO/files/ceos/ /opt/ceos/nodes
fi

# Update ATD containers

cd /opt/atd/nested-labvm/atd-docker

# su atdadmin -c 'bash docker_build.sh'

# Setting arista user ids for coder container
export ArID=$(id -u arista)
export ArGD=$(id -g arista)
export AtID=$(id -u atdadmin)
export AtGD=$(id -g atdadmin)

docker compose up -d --remove-orphans --force-recreate

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
    # ===============================================
    # Adding below section to adjust veth pair MTUs to 10000
    # ===============================================
    sleep 5
    for i in $(ifconfig | awk '/veth/{print $1}')
    do
        echo $i
        ip link set $i mtu 10000
    done
    # ===============================================
    # End veth mtu adjustment section
    # ===============================================
fi

# if VTEP file present
if [ -f "/etc/atd/.provisioned" ]
then
    if [ -f "/etc/atd/.init" ]
    then
        bash docker_run.sh
        while : ; do
            [[ -f "/etc/atd/.vtep.sh" ]] && break
            echo "Pausing until file exists."
            sleep 1
        done
        bash /etc/atd/.vtep.sh
    else
        bash /etc/atd/.vtep.sh
    fi
fi
