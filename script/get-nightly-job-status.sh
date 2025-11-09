#!/bin/bash

# The script is to install jq package if needed 
# and then check if the jessie-release-nightly is get passed 

REQUIRED_PKG="jq"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok installed")
echo Checking for $REQUIRED_PKG: $PKG_OK
if [ "" = "$PKG_OK" ]; then
  echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG."
  sudo apt update
  sudo apt --yes install $REQUIRED_PKG
fi

curl -k --header "PRIVATE-TOKEN: {PRIVATE_TOKEN}" "{URL_CI}/projects/16/jobs?scope[]=passed" | jq -c 'first(.[] | select(.name | contains("jessie-release-nightly")))' >> job_log.json