#!/bin/bash

BRANCH=$(cat /etc/atd/ATD_REPO.yaml | python3 -m shyaml get-value atd-public-branch)

if  [ -z "$(cat /etc/atd/ATD_REPO.yaml | grep repo)" ]
then
    REPO="https://github.com/aristanetworks/atd-public.git"
else
    REPO=$(cat /etc/atd/ATD_REPO.yaml | python3 -m shyaml get-value public-repo)
fi

# Perform git repo check
cd /opt/atd

# Check the current repo compared to the targeted repo
if [[ ! "$(git remote get-url origin)" = "$REPO" ]]
then
    echo "Repos do not match, updating to $REPO"
    git remote set-url origin $REPO
fi

# Fetch updates from the remote repo
git fetch origin

# Reset local state to match the remote branch exactly
git checkout .
git checkout $BRANCH
git reset --hard origin/$BRANCH

# Update cvpUpdate script

rsync -av /opt/atd/nested-labvm/services/cvpUpdate/cvpUpdate.sh /usr/local/bin/

# Update cvpStartup script

rsync -av /opt/atd/nested-labvm/services/cvpStartup/cvpStartup.sh /usr/local/bin/

echo "Executing cvpStartup"
bash /usr/local/bin/cvpStartup.sh
