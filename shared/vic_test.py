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


class LocalRun:
    def execute_here(self, command):
        p = Popen(
            command,
            stdout=PIPE,
            stderr=None,
            stdin=PIPE,
            shell=True,  # only for local runs inside a container and no user input
            universal_newlines=True,
        )
        stdout, _ = p.communicate()
        if stdout and stdout != "\n":
            print(str(p.returncode) + "): " + stdout.strip())
        if p.returncode != 0:
            sys.exit(p.returncode)
        return stdout

    def compare_ex(self, date, res_name, backup):
        self.execute_here("sed '1d' baseline_" + backup + ".out > baseline_tmp.out")
        self.execute_here(
            "diff -wB  baseline_tmp.out "
            + res_name
            + "&&  echo EQUAL > res_tmp.out || echo NOT_EQUAL > res_tmp.out"
        )

    def read_result(self):
        result = self.execute_here("cat res_tmp.out")
        return result

    def after_success(self, date, backup):
        self.execute_here(
            'echo  "\e[1;32m>>>> TEST PASSED <<<< \e[0;39m >> res and tmp files will be deleted .. "'
        )
        self.execute_here(
            "echo " + date + " \t " + backup + ' " \t Test PASSED" >> Results_History'
        )

    def after_fail(self, date, backup, res_name):
        self.execute_here(
            'echo  "\e[1;31m>>>> TEST FAILED <<<< \e[0;39m >> res files will be saved .. "'
        )
        self.execute_here(
            "echo " + date + " \t " + backup + ' " \t Test FAILED" >> Results_History'
        )
        self.execute_here("mv " + res_name + " baseline_" + date + "_" + backup)

    def create_test_list(self):
        self.execute_here("find . -name run_test.py > test_list")


class RemoteRun:
    def __init__(self, IP=""):
        self.IP = IP

    def check_IP(self):
        assert len(self.IP) > 7, "You should enter a valid IP"

    def execute_there(self, cmd):
        command = ["ssh", "root@" + self.IP, cmd]
        p = Popen(
            command, stdout=PIPE, stderr=None, stdin=PIPE, universal_newlines=True
        )
        stdout, _ = p.communicate()
        if stdout and stdout != "\n":
            print(str(p.returncode) + "): " + stdout.strip())
        if p.returncode != 0:
            sys.exit(p.returncode)

    def copy_file(self, file):
        command = ["scp", "-r", "root@" + self.IP + ":/home/vimec/vic/" + file, "."]
        p = Popen(
            command, stdout=PIPE, stderr=None, stdin=PIPE, universal_newlines=True
        )
        stdout, _ = p.communicate()
        if stdout and stdout != "\n":
            print(str(p.returncode) + "): " + stdout.strip())
        if p.returncode != 0:
            sys.exit(p.returncode)

    def clean_there(self):
        self.execute_there(
            'cd /home/vimec/vic ; ls | grep messagelog && rm messagelog* ; \
                                  echo "messagelogs removed." || echo "No logs to delete." '
        )
        self.execute_there(
            'cd /home/vimec/vic ; ls | grep res_ && rm res_* ; \
                                  echo "res files removed." || echo "No res files to delete." '
        )

    def prepare_there(self):
        self.execute_there(
            'export DISPLAY=":0"; cd /home/vimec/scripts; ./killvcenter ; ./cleareventlog; ./vcenter 1>/dev/null 2>/dev/null & '
        )
        time.sleep(25)

    def kill_there(self):
        self.execute_there("cd /home/vimec/vic; ./killvcenter")

    def pulse_there(self, num, pin, width, board):
        print(
            "/home/vimec/vic/bin/vic/simulateinputpin "
            + str(num)
            + " "
            + str(pin)
            + " "
            + str(width)
            + " "
            + str(board)
        )
        self.execute_there(
            "/home/vimec/vic/bin/vic/simulateinputpin "
            + str(num)
            + " "
            + str(pin)
            + " "
            + str(width)
            + " "
            + str(board)
        )

    def install_latest(self):
        self.execute_there(
            "cd /home/admin/update; rm -f vic-ssd* ; dpkg --force-overwrite -i *deb > /dev/nul"
        )


def get_date():
    d = datetime.datetime.today().strftime("%d")
    m = datetime.datetime.today().strftime("%B")[0:3]
    y = datetime.datetime.today().strftime("%Y")
    date = m + "_" + d + "_" + y
    return date


def check_input_ip():
    if len(sys.argv) != 2:
        print("Please provide ip of the VIC VM")
        sys.exit(1)


def cmd_line_args():
    parser = argparse.ArgumentParser(
        prog="run_test.py",
        usage="%(prog)s <IP> [-bk <backup>]",
        description="runs test on the system with the given IP after loading the given backup on it.",
    )
    parser.add_argument(
        "ip", help="IP of a vimec system, can be a vm or a real hardware system."
    )
    parser.add_argument(
        "-bk", "--backup", help="configuration to be used while running this test."
    )
    return parser.parse_args()


def clean_here(TEST_PATH):
    for file in os.listdir(TEST_PATH):
        if os.path.isfile(file) and (
            file.endswith("_tmp.out") or file.startswith("res_")
        ):
            os.remove(file)


def define_backup(TEST_CONF, bkp):
    if bkp:
        if TEST_CONF == "GENERIC":
            backup = ""
            bkp_res = bkp
        elif TEST_CONF == "SEVERAL":
            backup = bkp
            bkp_res = bkp
    else:
        backup = ""
        bkp_res = ""
    return (backup, bkp_res)


def detect_crash(string):
    if re.search(r"finished \(rc\=-1\)", string):
        state = "CRASH"
    else:
        state = "NO_CRASH"
    return state


def click_there(runner, x, y, message):
    runner.execute_there(
        'export DISPLAY=":0" ; xdotool mousemove '
        + str(x)
        + "  "
        + str(y)
        + ' ; xdotool click 1 ; sleep 0.5 ; echo "'
        + message
        + '"'
    )


# Next: add image search functionality when open cv problem with the vm is solved.
### UI functions


def click_utilities(runner):
    click_there(runner, 750, 45, "Clicked Utilities")


def click_event(runner):
    click_there(runner, 60, 125, "Clicked Event Log")


def click_event_save(runner):
    click_there(runner, 800, 765, "Clicked Save")


def click_event_yes(runner):
    click_there(runner, 650, 430, "Clicked Yes")


def click_user(runner):
    click_there(runner, 60, 40, "Clicked User")


def go_to_user(runner):
    click_there(runner, 340, 270, "Entering user")


def enter_user(runner):
    runner.execute_there(
        'export DISPLAY=":0" ; xdotool key v; xdotool key i ; xdotool key  m;\
         xdotool key  e; xdotool key c; sleep 0.5 ; echo "Wrote Vimec"'
    )


def click_password(runner):
    click_there(runner, 335, 305, "Clicked Password")


def enter_password(runner):  # Next: write this in a more secure way
    runner.execute_there(
        'export DISPLAY=":0" ; xdotool key H   ; xdotool key l ; xdotool key 0xffbd ;xdotool key g ;\
        xdotool key i; xdotool key h ; xdotool key B; xdotool key l ;  sleep 0.5 ; echo "Entered Password"'
    )


def click_login(runner):
    click_there(runner, 410, 350, "Clicked Login")


def vimec_login(r):
    click_user(r)
    go_to_user(r)
    enter_user(r)
    click_password(r)
    enter_password(r)
    click_login(r)


def click_display(runner):
    click_there(runner, 200, 40, "Clicked Display")


def click_validation(runner):
    click_there(runner, 64, 448, "Clicked Validation")


def click_validate_list(runner):
    click_there(runner, 197, 345, "Clicked Validate List")


def click_inspection(runner):
    click_there(runner, 280, 40, "Clicked Inspection")
