#!/bin/bash

#Authenticate onto CVP
curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d '{
    "userId": "arista",
    "password": "arista"
  }' 'https://192.168.0.5/cvpservice/login/authenticate.do' -c cookie.txt -k

echo "Authenticated"

#push files onto CVP using REST API. files to be located in home directory
curl -X POST --header 'Content-Type: multipart/form-data' --header 'Accept: application/json' -F 'file=@/home/arista/Broadcaster/Broadcaster.zip' 'https://192.168.0.5/cvpservice/configlet/importConfiglets.do' -b cookie.txt -k

echo "File Pushed"
