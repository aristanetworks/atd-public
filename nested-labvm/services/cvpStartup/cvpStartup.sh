#!/bin/bash

echo "Starting cvpStartup"

TOPO=$(cat /etc/atd/ACCESS_INFO.yaml | python3 -m shyaml get-value topology)
APWD=$(cat /etc/atd/ACCESS_INFO.yaml | python3 -m shyaml get-value login_info.jump_host.pw)

if [ "$(cat /etc/atd/ACCESS_INFO.yaml | grep eos_type)" ]
then
    EOS_TYPE=$(cat /etc/atd/ACCESS_INFO.yaml | python3 -m shyaml get-value eos_type)
else
    EOS_TYPE=veos
fi

# Perform check to see if docker auth file exists
if ! [ -f "/home/atdadmin/.docker/config.json" ]
then
    echo "Docker auth file not found, creating..."
    gcloud auth configure-docker gcr.io,us.gcr.io --quiet
    su atdadmin -c "gcloud auth configure-docker gcr.io,us.gcr.io --quiet"
fi

cd /opt/atd/nested-labvm/atd-docker
# if VTEP file present
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
