#!/bin/bash

if [[ $# -lt 1 ]] ; then
  echo "usage: $0 <ipaddres>"

  echo "
  $ ./restart_vcenter_remote.sh target-ipaddress

  This will automatically do these steps:
    - kill the running software on the target
    - restart the software
  "
  exit 0
fi

ipaddress=$1

echo Connecting to $ipaddress 
ssh root@$ipaddress "/home/vimec/scripts/killvcenter"
ssh root@$ipaddress "export DISPLAY=\":0\";/home/vimec/scripts/vcenter 1>/dev/null 2>/dev/null &"
sleep 2m