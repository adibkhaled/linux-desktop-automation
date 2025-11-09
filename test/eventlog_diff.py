#! /usr/bin/env python3
# 
#  Copyright (c) 2024 Vimec Applied Vision Technology B.V.
# 
"""
Compare the event log between two different software versions.
"""

from difflib import Differ
import os
import re
import traceback
import sys
import argparse
import time
from report import logging


def cmd_line_log_file():
    parser = argparse.ArgumentParser(
        prog="log_file_diff.py",
        usage="%(prog)s <previous_release>\
        [-c <current_release>]",
        description="This script generates\
        eventlog file error difference between current and previous release",
    )

    parser.add_argument(
        "-p",
        "--previous_release",
        help="VCenter release version e.g: 3.13.4.0 or 3.13.4.0-RC1, \
        Add previous release to get old release eventlog",
    )

    parser.add_argument(
        "-c",
        "--current_release",
        help="Add current release to get new/current release eventlog",
    )
    return parser.parse_args()


def get_log_folder():
    log_folder = "vcenter_logs"

    if not os.path.exists(log_folder):
        os.mkdir(log_folder)
        logging.info(f"{log_folder} created!")

    return log_folder


output_file = "output_" + time.strftime("%Y-%m-%d") + "_diff.txt"
stmp_file_path = os.path.join(get_log_folder(), "tmp_src.log")
dtmp_file_path = os.path.join(get_log_folder(), "tmp_des.log")
diff_file_path = os.path.join(get_log_folder(), output_file)


def get_file_names_with_strings(str_list):
    file_list = os.listdir(get_log_folder())
    for file in file_list:
        if str_list in file:
            logging.info(f"File found: {file}")
            return file


def get_src_file_path():
    arg = cmd_line_log_file()
    pre_version = arg.previous_release
    src_file_path = os.path.join(
        get_log_folder(), get_file_names_with_strings(pre_version)
    )
    return src_file_path


def get_des_file_path():
    arg = cmd_line_log_file()
    cur_version = arg.current_release
    des_file_path = os.path.join(
        get_log_folder(), get_file_names_with_strings(cur_version)
    )
    return des_file_path


def get_error_info(temp_file, actual_file):
    the_body = ""
    with open(temp_file, "w", encoding='utf-8') as tmp_file:
        with open(actual_file, "r", encoding='utf-8') as log:
            for line in log:
                if "error" in line or "warning" in line:
                    output = re.sub(r".*?(?=\[error\]|\[warning\])", "", line, 1)
                    tmp_file.write(output)
                    the_body += output


def compare_diff(src_file, des_file, diff_file):
    arg = cmd_line_log_file()
    pre_version = arg.previous_release
    cur_version = arg.current_release

    with open(diff_file, "w", encoding='utf-8') as dFile:
        with open(src_file, encoding='utf-8') as file_src, open(des_file, encoding='utf-8') as file_des:
            differ = Differ()
            dFile.write(
                f"The error changes in vcenter log files between {pre_version} and {cur_version} release\n")

            for line in differ.compare(file_src.readlines(), file_des.readlines()):
                for prefix in ("-", "+"):
                    if line.startswith(prefix):
                        dFile.write(line)


def remove_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        print(file_path + " file path does not exist")


def diff_status(d_file):
    with open(d_file, "r", encoding='utf-8') as file:
        for line in file:
            for prefix in "+" or "-":
                if prefix in line:
                    logging.error(f"There are difference in the {d_file}")
                    return 0
                break


def main():
    remove_file(diff_file_path)
    get_error_info(stmp_file_path, get_src_file_path())
    get_error_info(dtmp_file_path, get_des_file_path())
    compare_diff(stmp_file_path, dtmp_file_path, diff_file_path)
    remove_file(stmp_file_path)
    remove_file(dtmp_file_path)
    logging.info(f"The v-center log comapre file is in: {diff_file_path}")
    logging.info("Event log compare is done!!")
    sys.exit(diff_status(diff_file_path))


if __name__ == "__main__":
    try:
        exit(main())
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
    sys.exit(1)
