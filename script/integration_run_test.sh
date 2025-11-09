#!/bin/bash

if [[ $# -lt 1 ]] ; then
  echo "usage: $0 <ipaddres>"

  echo "
  $ ./integration_run_test target-ipaddress

  This will automatically do these steps:
    - Copy the regression and integration testcase in v-center-linux
    - Run the play script for all integration and regression testcases
  "
  exit 0
fi

ipaddress=$1
testcase=${2:-integration}
echo Connecting to $ipaddress
echo Run $testcase

# Get OS version (just the number, e.g. 12)
OS_VERSION=$(ssh root@${ipaddress} "grep -oP '(?<=^VERSION_ID=).+' /etc/os-release | tr -d '\"'")

echo "Remote host $ipaddress is running Debian version: $OS_VERSION"

if [ "$OS_VERSION" = "12" ]; then
    echo "OS 12 detected"
    ssh root@$ipaddress "apt-get -y --fix-broken install; apt-get -y install git"
    ssh vimec@$ipaddress "rm -rf /home/vimec/v-center-testing && git clone https://gitlab.vimec.nl/Vimec/v-center-testing.git /home/vimec/v-center-testing"
    ssh vimec@$ipaddress "source /home/vimec/venv/bin/activate && cd /home/vimec/v-center-testing && python3 test/play.py $testcase"
else
    echo "OS (version=$OS_VERSION)"
    ssh root@$ipaddress "apt-get -y --fix-broken install; apt-get -y install git"
    ssh root@$ipaddress "rm -rf /home/vimec/v-center-testing && git clone https://gitlab.vimec.nl/Vimec/v-center-testing.git /home/vimec/v-center-testing"
    ssh root@$ipaddress "cd /home/vimec/v-center-testing && python3 test/play.py $testcase"
fi