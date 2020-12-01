#!/bin/bash

# cd /home/arista/atd-docker

docker build --build-arg UID=$(id -u arista) -t atddocker_login:1.0 login/.
docker build --build-arg UID=$(id -u atdadmin) -t atddocker_kvmbuilder:1.0 kvmbuilder/.
docker build --build-arg UID=$(id -u arista) -t atddocker_desktop:1.0 desktop/.
docker build --build-arg UID=$(id -u arista) -t atddocker_cvpupdater:1.0 cvpUpdater/.
docker build --build-arg UID=$(id -u arista) -t atddocker_gitconfigletsync:1.0 gitConfigletSync/.
docker build --build-arg UID=$(id -u arista) -t atddocker_sslupdater:1.0 sslUpdater/.
docker build -t atddocker_labguides:1.0 labguides/.
docker build -t atddocker_freerad:1.0 freeradius/.
docker build -t atddocker_nginx:1.0 nginx/.
docker build -t atddocker_guacd:1.0 guacd/.
docker build -t atddocker_guacamole:1.0 guacamole/.
docker build -t atddocker_jenkins:1.0 jenkins/.
docker build -t atddocker_uptime:1.0 uptime/.
docker build -t atddocker_uilanding:1.0 uilanding/.
docker build -t atddocker_ceosbuilder:1.0 ceosbuilder/.
docker build -t atddocker_monitor:1.0 monitor/.
docker build -t atddocker_coder:1.0 coder/.

# Pull any remote repo images
docker pull mpergament/avd-cpv-atd-nested:latest
docker pull mpergament/aristarobot:latest
