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
git fetch

# Perform check on the current branch/tag to the targeted
if [[ "$(git branch --show-current)" = "$BRANCH" ]]
then
    echo "Target branch matches current branch"
    git checkout .
    git pull
else
    echo "Branches do not match, updating to branch $BRANCH"
    git checkout .
    git checkout $BRANCH
    git pull
fi

# Update eosUpdate script

rsync -av /opt/atd/nested-labvm/services/eosUpdate/eosUpdate.sh /usr/local/bin/

# Update eosStartup script

rsync -av /opt/atd/nested-labvm/services/eosStartup/eosStartup.sh /usr/local/bin/

echo "Executing eosStartup"
bash /usr/local/bin/eosStartup.sh
