#!/bin/bash

BRANCH=$(cat /etc/atd/ATD_REPO.yaml | python3 -m shyaml get-value atd-public-branch)
TOPO=$(cat /etc/atd/ACCESS_INFO.yaml | python3 -m shyaml get-value topology)

rm -rf /tmp/atd

git clone --branch $BRANCH https://github.com/aristanetworks/atd-public.git /tmp/atd

# Update atdUpdate service

cp /tmp/atd/nested-labvm/services/atdUpdate/atdUpdate.sh /usr/local/bin/
cp /tmp/atd/nested-labvm/services/atdUpdate/atdUpdate.service /etc/systemd/system/

systemctl daemon-reload

# Add files to arista home
rsync -av /tmp/atd/topologies/$TOPO/files/ /home/arista/arista-dir
rsync -av /tmp/atd/topologies/$TOPO/files/infra /home/arista/

chown -R arista:arista /home/arista

# Update ATD containers

cd /tmp/atd/nested-labvm/atd-docker

su atdadmin -c 'bash docker_build.sh'

su atdadmin -c 'docker-compose up -d'

echo 'y' | docker image prune

systemctl restart sshd
