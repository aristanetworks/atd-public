## Labvm
This directory will contain the necessary data/files needed to help modify the labvm on the fly without a rebuild of the base labvm via Ansible.

Structure of the `labvm/` directory:

- `services/` - This will contain services that will be packaged up and used to update the labvm.  

- `services/serviceUpdater.yml` - File used by `atdServiceUpdater.py to check and see which service should be checked for changes

Example structure:

- `services/atdServiceUpdater/` - Directory that will hold all files needed for `atdServiceUpdater`
- `services/atdServiceUpdater/atdServiceUpdater.py` - Script to performs the action
- `service/atdServiceUpdater/atdServiceUpdater.service` - The `systemctl` service file.
