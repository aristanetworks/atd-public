#!/bin/bash

PROJECT=$(cut -d':' -f2 <<<$(grep project /etc/atd/ACCESS_INFO.yaml))

if [ $PROJECT == 'atds-280712' ]
then
  cp -r /opt/nginx/certs/prod/topo-atd.* /etc/nginx/certs
  touch /etc/nginx/certs/prod.txt
else
  cp -r /opt/nginx/certs/dev/topo-atd.* /etc/nginx/certs
  touch /etc/nginx/certs/dev.txt
fi
