#!/bin/bash
source "$(dirname "$0")/common_function.sh"
actual_version=$(echo  "$2" | cut -d'-' -f1)
compare_version="3.16.0.5"

copy_send_coredumplog