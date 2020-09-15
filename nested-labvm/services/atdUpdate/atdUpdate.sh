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

rm -rf /opt/atd

git clone --branch $BRANCH $REPO /opt/atd

# Update ssh-key in EOS configlet for Arista user
ARISTA_SSH=$(cat /home/arista/.ssh/id_rsa.pub)

sed -i "/username arista ssh-key/cusername arista ssh-key ${ARISTA_SSH}" /opt/atd/topologies/$TOPO/configlets/ATD-INFRA

# Update arista user password for Guacamole

sed -i "s/{ARISTA_REPLACE}/$APWD/g" /opt/atd/topologies/$TOPO/files/infra/user-mapping.xml

# Update atdUpdate service

cp /opt/atd/nested-labvm/services/atdUpdate/atdUpdate.sh /usr/local/bin/
cp /opt/atd/nested-labvm/services/atdUpdate/atdUpdate.service /etc/systemd/system/

systemctl daemon-reload

# Add files to arista home
rsync -av /opt/atd/topologies/$TOPO/files/ /home/arista/arista-dir
rsync -av /opt/atd/topologies/$TOPO/files/infra /home/arista/

# Perform check if there is a scripts directory
if [ -d "/opt/atd/topologies/$TOPO/files/scripts" ]
then
    rsync -av /opt/atd/topologies/$TOPO/files/scripts /home/arista/GUI_Desktop/
fi

chown -R arista:arista /home/arista

# Update ATD containers

cd /opt/atd/nested-labvm/atd-docker

su atdadmin -c 'bash docker_build.sh'

su atdadmin -c 'docker-compose up -d --remove-orphans'

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
