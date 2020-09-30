#!/bin/bash

yum install -y wget

wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm

yum install -y ./google-chrome-stable_current_*.rpm

rm -rf google-chrome-stable_current_*.rpm

sed -i 's:Exec=/usr/bin/google-chrome-stable:Exec=/usr/bin/google-chrome-stable --password-store=basic --no-first-run:g' /usr/share/applications/google-chrome.desktop

mkdir -p /etc/opt/chrome/policies/managed
