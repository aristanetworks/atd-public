#!/bin/bash

PROJECT=$(cut -d':' -f2 <<<$(grep project /etc/atd/ACCESS_INFO.yaml) | awk '{print $1}')

if [ $PROJECT ]
then
  cp -r /opt/nginx/certs/$PROJECT/* /etc/nginx/certs
fi
