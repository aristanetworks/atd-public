#!/bin/bash

# Get the current list of installable packages

PIP_INST=$(cat /tmp/atd/labvm/services/serviceUpdater.yml | shyaml get-value pipPackages.Install)
PIP_REM=$(cat /tmp/atd/labvm/services/serviceUpdater.yml | shyaml get-value pipPackages.Remove)

# Evaluate if there are items within the list
if [ "$PIP_INST" != "None" ]
then
    # Grab full list and install all packages
    N_PIP_PKGS=$(cat /tmp/atd/labvm/services/serviceUpdater.yml | shyaml get-values pipPackages.Install)
    echo "Packages to be Added: " $N_PIP_PKGS
    pip install --upgrade $N_PIP_PKGS
else
    echo "Nothing to be added."
fi
if [ "$PIP_REM" != "None" ]
then
    # Grab full list and uninstall all listed packages
    R_PIP_PKGS=$(cat /tmp/atd/labvm/services/serviceUpdater.yml | shyaml get-values pipPackages.Remove)
    echo "Packages to be Removed: $R_PIP_PKGS"
    pip uninstall -y $R_PIP_PKGS
else
    echo "Nothing to be removed."
fi