#!/usr/bin/env python3
# 
#  Copyright (c) 2024 Vimec Applied Vision Technology B.V.
#  

import os
import sys
import time
import traceback
import datetime
from subprocess import Popen, PIPE

sys.path.append("./shared")
import vic_test

BACKUPS_PATH = "/home/admin/backup"


def main():
    start_time = time.time()
    date = vic_test.get_date()

    vic_test.check_input_ip()
    IP = sys.argv[1]
    r = vic_test.RemoteRun(IP)
    r.check_IP()
    l = vic_test.LocalRun()

    r.execute_there(
        "cd " + BACKUPS_PATH + " ; ls > /home/vimec/vic/backup_list_tmp.out "
    )
    r.execute_there("sed -i s/.tgz// /home/vimec/vic/backup_list_tmp.out")
    r.copy_file("backup_list_tmp.out")

    bk_file = open("backup_list_tmp.out", "r")
    bkps = bk_file.readlines()
    bk_file.close()

    l.create_test_list()
    test_file = open("test_list", "r")
    test_list = test_file.readlines()
    test_file.close()

    for bkp in bkps:
        try:
            strip_bkp = bkp.strip()
            print("\nBackup is: ", strip_bkp, " >>>> \n")
            tgz_bkp = strip_bkp + ".tgz"
            r.execute_there(
                "cd " + BACKUPS_PATH + " ; tar -xzvf " + tgz_bkp + " -C / > /dev/null"
            )
            r.install_latest()

            for test in test_list:
                try:
                    strip_test = test.strip()
                    test_path = os.path.dirname(strip_test)
                    print("\nTest is: ", test_path, " >>>> \n")
                    os.chdir(test_path)
                    command = "python3 run_test.py " + IP + " -bk " + strip_bkp
                    l.execute_here(command)
                    os.chdir("../..")
                except:
                    pass
                    print("IGNORED AN EXCEPTION")
        except:
            pass
            print("IGNORED AN EXCEPTION")

    vic_test.clean_here(".")

    end_time = time.time()
    print("--- Runtime: %s seconds ---" % (end_time - start_time))


if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        pass
    except Exception:
        traceback.print_exc(file=sys.stdout)
    sys.exit(1)
