#!/bin/bash

# This script will sync all the Arista roles for Ansible with the
# most recent version of the arista-ansible-role-test framework.

# It is best to run this script from a fresh clone of the
# role test framework, with an empty parent directory where
# the updates will be performed. The script will clone each of
# the Arista roles, update the role, and push the changes back
# to the role's repo.

# You must have access to write to the master branch of the
# Arista roles for this to work properly.

roles=(
    ansible-eos-acl
    ansible-eos-bgp
    ansible-eos-bridging
    ansible-eos-interfaces
    ansible-eos-ipv4
    ansible-eos-mlag
    ansible-eos-route-control
    ansible-eos-system
    ansible-eos-virtual-router
    ansible-eos-vxlan
)

cwd=`pwd`

for role in ${roles[@]}
do
    echo Updating $role with the latest arista-ansible-role-test version

    # cd to the parent directory
    cd $cwd/..

    # clone a copy of the current role
    git clone https://github.com/arista-eosplus/${role}.git
    cd $role

    # pull the subtree down from the master repo and push the commit back to the role repo
    git remote add role-test https://github.com/arista-eosplus/arista-ansible-role-test.git
    git subtree pull --prefix=test/arista-ansible-role-test --squash role-test master -m "Pull in arista-ansible-role-test updates"
    git push

    echo
    echo
done
