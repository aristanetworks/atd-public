### Generic Variables
SHELL := /bin/zsh

.PHONY: help
help: ## Display help message (*: main entry points / []: part of an entry point)
	@grep -E '^[0-9a-zA-Z_-]+\.*[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


################################################################################
# ATD-fabric
################################################################################

.PHONY: fabric-build
fabric-build: ## Run ansible playbook to build Fabric configuration for ATD Fabric and CVP (will build configuration locally on your VS Code Instance)
	ansible-playbook playbooks/fabric-deploy.yml --tags build -i inventory.yml

.PHONY: fabric-provision
fabric-provision: ## Run ansible playbook to build EVPN Fabric configuration for ATD Fabric and CV (will provision/create tasks on CVP for Change Control procedures)
	ansible-playbook playbooks/fabric-deploy.yml --tags provision -i inventory.yml

.PHONY: fabric-validate
fabric-validate: ## Run ansible playbook to validate EVPN Fabric configuration for ATD Fabric and eAPI
	ansible-playbook playbooks/fabric-validate.yml -i inventory.yml

.PHONY: fabric-backup
fabric-backup: ## Run ansible playbook to backup switch fabric via eAPI
	ansible-playbook playbooks/fabric-backup.yml -i inventory.yml

.PHONY: fabric-debug
fabric-debug: ## Run ansible playbook to build Fabric configuration for AVD Fabric and CVP with debugging enabled
	ansible-playbook playbooks/fabric-deploy.yml --tags build,debug -i inventory.yml

.PHONY: fabric-initialize
fabric-initialize: ## Initial Deployment for the AVD topology
	ansible-playbook playbooks/fabric-deploy.yml --tags provision -i inventory.yml
	ansible-playbook playbooks/fabric-init.yml -i inventory.yml

.PHONY: update-configlet
update-configlet: ## Run ansible playbook to update configlets on CloudVision
	ansible-playbook playbooks/fabric-cvp-deploy.yml --tags provision --skip-tags containers,apply -i inventory.yml

.PHONY: atd-setup
atd-setup: ## Run ansible playbook to Setup ATD Environment
	ansible-galaxy collection install arista.avd --upgrade
	ansible-galaxy collection install git+https://github.com/aristanetworks/ansible-avd.git#/ansible_collections/arista/avd/,devel
	ansible-galaxy collection install git+https://github.com/aristanetworks/ansible-cvp.git#/ansible_collections/arista/cvp/,devel
	ansible-galaxy collection install community.general
	ansible-galaxy collection install ansible.posix
	ansible-playbook playbooks/atd-setup.yml

.PHONY: atd-removelegacy
atd-removelegacy: ## Run ansible playbook AFTER running fabric-provision to remove legacy configlets (added on all ATD labs by default)
	ansible-playbook playbooks/fabric-deploy.yml --tags removelegacy --skip-tags always -i inventory.yml

.PHONY: update-devel
update-devel: ## Update to the latest arista.avd collections development branch
	ansible-galaxy collection install git+https://github.com/aristanetworks/ansible-avd.git#/ansible_collections/arista/avd/,devel
	ansible-galaxy collection install git+https://github.com/aristanetworks/ansible-cvp.git#/ansible_collections/arista/cvp/,devel

.PHONY: update-collections
update-collections: ## Update arista.avd collections to latest release branch
	ansible-galaxy collection install arista.avd --upgrade
	ansible-galaxy collection install community.general --upgrade
	ansible-galaxy collection install ansible.posix --upgrade