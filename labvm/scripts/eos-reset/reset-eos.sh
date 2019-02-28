#~/bin/bash

echo "STARTING"
echo "Getting EOS Underlay IPs"
./update_hosts.py
echo "hosts file created"
echo "Getting base CVP Configlets for EOS devices"
./get-cvp-configlets.py -u arista -p arista
echo "Configlets gathered"
echo "Starting Ansible Playbook"
ansible-playbook ansible-reset.yml --ask-pass
echo "Done!"