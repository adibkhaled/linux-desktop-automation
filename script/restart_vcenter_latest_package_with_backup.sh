#!/bin/bash
source "$(dirname "$0")/common_function.sh" 
actual_version=$(echo  "$2" | cut -d'-' -f1)
compare_version="3.16.0.5"

IFS='.' read -ra v_components <<< "$actual_version"
IFS='.' read -ra compare_components <<< "$compare_version"

kill_vcenter
clearcoredumplog

if [ "${v_components[0]}" -gt "${compare_components[0]}" ] ||
   [ "${v_components[0]}" -eq "${compare_components[0]}" -a "${v_components[1]}" -gt "${compare_components[1]}" ] ||
   [ "${v_components[0]}" -eq "${compare_components[0]}" -a "${v_components[1]}" -eq "${compare_components[1]}" -a "${v_components[2]}" -gt "${compare_components[2]}" ] ||
   [ "${v_components[0]}" -eq "${compare_components[0]}" -a "${v_components[1]}" -eq "${compare_components[1]}" -a "${v_components[2]}" -eq "${compare_components[2]}" -a "${v_components[3]}" -gt "${compare_components[3]}" ]; then
   
   if [ "${v_components[0]}" -eq "3" -a "${v_components[1]}" -eq "99" -a "${v_components[2]}" -eq "99" ]; then
      echo "Development package"
      install_buster_package
   else
      echo "Release $actual_version greater than $compare_version"
      download_install_buster_package
   fi
else
   echo "Version older or same as like $compare_version"
   install_buster_package
fi
copy_backup_files
startvic