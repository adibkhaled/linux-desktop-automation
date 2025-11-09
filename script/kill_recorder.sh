#!/bin/bash
# This script to kill all the record process 
ps -ef | grep record | grep -v grep | awk '{print $2}' | xargs kill -9