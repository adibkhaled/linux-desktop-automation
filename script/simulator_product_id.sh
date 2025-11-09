#!/bin/bash

<<'###DESCRIPTION'
The script is need for updating the product id. 
This is a special script to reset the ResetPin. PLEASE USE THE BELOW conf in VCenter.ini file if you want to use this script:

[PRODUCTID]
TriggerBoard=7 7 -1 - 1
TriggerPin=0 8 -1 -1 
TriggerModule=-1 -1 -1 -1
ResetBoard=7 7 -1 -1
ResetPin=5 6 0 0
ResetSign=1 1 1 1
MaxID=2 10 0 0 
Mode=2 2 0 0 0 
Type=2 1 0 0
ID_0=A B
ID_1=1 2 3 4 5 6 7 8 9 10

This configuration is for INSPECTIDTYPE_TOOL and INSPECTIDTYPE_CAROUSEL.

Where: /home/vimec/vic (put the script in this folder)
Who: root
How: ./simulator_product_id 0 [input pin number]

###DESCRIPTION 

COUNT=0
simulatepin=/home/vimec/vic/bin/vic/simulateinputpin
while true
do
  $simulatepin 5 1 500 7 &
  ((COUNT++))
  echo count=${COUNT}
  if [ ${COUNT} -eq 5 ];
  then
    echo "Reset chuck" $COUNT
    $simulatepin 6 1 300 7 &
    ((COUNT=0))
  fi
  sleep 0.110;$simulatepin $1 2 1500 7 &
sleep 2
done