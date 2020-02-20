#!/bin/bash

yum install -y epel-release

yum install -y xrdp

systemctl enable xrdp.service
