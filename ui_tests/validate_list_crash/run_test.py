#!/usr/bin/env python3
# 
#  Copyright (c) 2024 Vimec Applied Vision Technology B.V.
# 

import os
import sys
import time
import traceback
import datetime
import argparse
import re
from subprocess import Popen, PIPE

sys.path.append("../../shared")
import vic_test

"""
Steps:
===================
- Starts vcenter.
- Clears previous eventlog.
- Logins as vimec.
- Clicks display.
- Opens validation.
- Clicks validate list.
- Saves the new eventlog. 
- Greps vicdisplayvalidation rc=-1.
- Compares the result to a saved baseline.
- If files are equal, means there is a crash, so test fails. 
- All backups have the same baseline. 
"""

### TAGS 
TEST_TYPE = 'REGRESS'   #Next: add type functionality later ('REGRESS or PROGRESS', is it testing existing code or new feature?) 
TEST_CONF = 'GENERIC'   # baseline common to all backups (or there is no baseline)? SEVERAL = no, GENERIC = yes

def main():
    # Setup Stage
    print("\nSetup >>>>>>>>> ")
    args = vic_test.cmd_line_args()
    IP = args.ip
    backup, bkp_res = vic_test.define_backup(TEST_CONF, args.backup)

    l = vic_test.LocalRun()
    i_path=l.execute_here("pwd")
    TEST_PATH=i_path.strip()

    r = vic_test.RemoteRun(IP)
    r.check_IP()

    date = vic_test.get_date()
    res_name = "res_" + date + "_" + bkp_res + ".out"

    r.prepare_there()
    r.clean_there()

    # Running Stage
    print("\nRunning >>>>>>>>> ")
    vic_test.click_user(r)
    vic_test.go_to_user(r)
    vic_test.enter_user(r)
    vic_test.click_password(r)
    vic_test.enter_password(r)
    vic_test.click_login(r)
    vic_test.click_display(r)
    vic_test.click_validation(r)
    vic_test.click_validate_list(r)
    vic_test.click_utilities(r)
    vic_test.click_event(r)
    vic_test.click_event_save(r)
    vic_test.click_event_yes(r)

    r.kill_there()
    r.execute_there("cd /home/vimec/vic; grep vicdisplayvalidation ./messagelog* \
        | cut -d \" \" -f9- > " + res_name)
    #l.execute_here("grep finish " + res_name + " > res_grep_tmp.out")

    # Comparing Stage
    print("\nComparing >>>>>>>>> ")
    r.copy_file(res_name)

    eventlog_file = open(res_name, 'r')
    eventlog_grep = eventlog_file.readlines()
    eventlog_file.close()

    state=""
    for line in eventlog_grep:
        if vic_test.detect_crash(line) == "CRASH":
            state = "CRASH"
            break

    if state == "CRASH":
        l.after_fail(date,bkp_res,res_name)
        vic_test.clean_here(TEST_PATH)
    else:
        l.after_success(date,bkp_res)
        vic_test.clean_here(TEST_PATH)
        r.clean_there()

if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        pass
    except Exception:
        traceback.print_exc(file=sys.stdout)
    sys.exit(1)
