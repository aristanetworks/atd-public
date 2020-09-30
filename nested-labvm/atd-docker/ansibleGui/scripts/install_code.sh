#!/bin/bash

cEXT=( "redhat.vscode-yaml" \
  "samuelcolvin.jinjahtml" \
  "ms-python.python" \
  "ms-vscode.PowerShell" \
  "vscoss.vscode-ansible" \
  "GrapeCity.gc-excelviewer" \
  "yzhang.markdown-all-in-one" \
  "DavidAnson.vscode-markdownlint" \
  "streetsidesoftware.code-spell-checker" \
  "eamodio.gitlens"
)

rpm --import https://packages.microsoft.com/keys/microsoft.asc

echo -n  "[code]
name=Visual Studio Code
baseurl=https://packages.microsoft.com/yumrepos/vscode
enabled=1
gpgcheck=1
gpgkey=https://packages.microsoft.com/keys/microsoft.asc
">> /etc/yum.repos.d/vscode.repo

yum install -y code

for i in ${cEXT[@]}
do
su arista -c "code --install-extension $i"
done
