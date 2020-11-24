#!/bin/bash

PROJECT=$(cut -d':' -f2 <<<$(grep project /etc/atd/ACCESS_INFO.yaml))

if [ $PROJECT ]
then
  cp -r /opt/nginx/certs/$PROJECT/* /etc/nginx/certs
fi
