#!/usr/bin/env bash
#For initial setup of AVD 3.x.x on ATD environment
echo -n "Install or update arista.avd collection? [ install | update ]"
read collectioninstall
if [ $collectioninstall = 'install' ]
then
  ansible-galaxy collection install arista.avd
elif [ $collectioninstall = 'update' ]
then
  ansible-galaxy collection install arista.avd --upgrade
else
  echo "invalid option"
fi
echo -n "Install/update python packages? [ yes | no ] "
read pythonpkgs
if [ $pythonpkgs = 'yes' ]
then
  echo "Installing additional packages"
  pip3 install -r /home/coder/.ansible/collections/ansible_collections/arista/avd/requirements.txt
  echo "Done"
else
  echo "Skipped python package install/update"
fi
echo -n "Install/update devel branch? [ yes | no ] "
read pythonpkgs
if [ $pythonpkgs = 'yes' ]
then
  echo -n "Update Ansible version (maybe required) [ yes | no ] "
  read ansibleupd
  if [ $ansibleupd = 'yes' ]
  then
    sudo pip3 uninstall -y ansible
    sudo pip3 uninstall -y ansible-base
    sudo pip3 install ansible
  fi
  echo "Installing additional packages for devel"
  ansible-galaxy collection install git+https://github.com/aristanetworks/ansible-avd.git#/ansible_collections/arista/avd/,devel
  pip3 install -r /home/coder/.ansible/collections/ansible_collections/arista/avd/requirements-dev.txt
  echo "Done"
else
  echo "Devel branch install skipped"
fi