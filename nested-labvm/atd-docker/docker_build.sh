#!/bin/bash

cd /home/arista/atd-docker

docker build -t c7systemd:1.0 c7systemd/.
docker build -t atddocker_kvmbuilder:1.0 kvmbuilder/.
docker build -t atddocker_desktop:1.0 desktop/.
docker build -t atddocker_cvpupdater:1.0 cvpUpdater/.
docker build -t atddocker_gitconfigletsync:1.0 gitConfigletSync/.
docker build -t atddocker_sslupdater:1.0 sslUpdater/.
docker build -t atddocker_labguides:1.0 labguides/.
docker build -t atddocker_freerad:1.0 freeradius/.
docker build -t atddocker_nginx:1.0 nginx/.
docker build -t atddocker_http:1.0 http/.
docker build -t atddocker_guacd:1.0 guacd/.
docker build -t atddocker_guacamole:1.0 guacamole/.
docker build -t atddocker_jenkins:1.0 jenkins/.
