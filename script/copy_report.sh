#!/bin/bash

ipaddress=$1
DIR=$2
ERROR_DIR="error_images"
echo "The ip address is: $ipaddress"
# Get latest report and add in the pipeline report artifacts
REPORT_FILE=$(ssh root@$ipaddress "ls -t1 /home/vimec/v-center-testing/$DIR/*.html |  head -n 1")
ERROR_DIR=$(ssh root@$ipaddress "ls -t1 /home/vimec/v-center-testing/$DIR/$ERROR_DIR/ |  head -n 1")
echo "Latest report is : $REPORT_FILE"
echo "Latest error : $ERROR_DIR"

if [ -f $REPORT_FILE ]; then
   mkdir -p $DIR/error_images
   echo "The $DIR folder is created"
   scp -r root@$ipaddress:$REPORT_FILE $DIR/
fi
if [ -f  $ERROR_DIR]; then
   scp -r root@$ipaddress:/home/vimec/v-center-testing/$DIR/$ERROR_DIR/ $DIR/
fi