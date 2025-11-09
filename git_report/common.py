#!/usr/bin/env python3
#
#  Copyright (c) 2024 Vimec Applied Vision Technology B.V.
#

import os
import gitlab
import re
import logging
import argparse

# ---------------------------------------------------------------------------
# @function: All the common functions are in this script
# ---------------------------------------------------------------------------


def clean_dir():
    for file in os.listdir("."):
        if os.path.isfile(file) and file.endswith("_ctr.txt"):
            os.remove(file)

        if os.path.isfile(file) and file.endswith("_ctr.html"):
            os.remove(file)


def clean_log():
    for file in os.listdir("."):
        if os.path.isfile(file) and file.endswith("_ctr.log"):
            os.remove(file)


def print_shape(status):
    if status == "Blocked":
        shape = "⛔"
    elif status == "Unknown" or status == "No issue":
        shape = "❓"
    elif status == "Pass" or status == "Yes":
        shape = "✅"
    elif status == "Fail" or status == "No":
        shape = "❌"
    elif status == "Ongoing":
        shape = "▶️"
    elif status == "Not needed" or status == "No testing":
        shape = "❎"
    elif status == "Not yet":
        shape = "❔"
    elif status == "Test needed":
        shape = "🔎"
    else:
        shape = status
    return shape


def detect_issue(title):
    m = re.search(r"^\[#\d{4}\]", title)
    if m:
        return m.group(0)
    else:
        return "None"


def detect_issue_from_mr(title):
    m = re.search(r"#\d{4}", title)
    if m:
        issue = "[" + m.group(0).strip() + "]"
        return issue
    else:
        return "None"


# ---------------------------------------------------------------------------
# @function init_project: to initialized the project
# @parameter gitlab_url
# @parameter private_token: token from gitlab
# @parameter project_id: v-center-linux project gitlab id is 16
# ---------------------------------------------------------------------------
def init_project():
    gl = gitlab.Gitlab(
        "{URL_CI}",
        private_token="{PRIVATE_TOKEN}",
        ssl_verify=False,
    )
    gl.auth()
    project_id = 16  # v-center project ID
    return gl.projects.get(project_id)


def parse_committed_date(date):
    parsed_date = date.split("T")[0]
    return parsed_date


# ---------------------------------------------------------------------------
# @function is_test_info: Search issues for test info keyword
# @parameter note: issue notes
# @comment: regular expresion to get test info
# ---------------------------------------------------------------------------
def is_test_info(note):
    if re.search(r"test\s*info", note, re.IGNORECASE):
        is_test = "Yes"
        return is_test


def test_stat(note):
    test_stat = ""
    if re.search(r"test\s*status:*(\s)*pass", note, re.IGNORECASE | re.MULTILINE):
        test_stat = "Pass"
    elif re.search(r"test\s*status:*(\s)*fail", note, re.IGNORECASE | re.MULTILINE):
        test_stat = "Fail"
    elif re.search(r"test\s*status:*(\s)*blocked", note, re.IGNORECASE | re.MULTILINE):
        test_stat = "Blocked"
    elif re.search(r"test\s*status:*(\s)*Auto", note, re.IGNORECASE | re.MULTILINE):
        test_stat = "Ongoing"
    elif re.search(
        r"Testing needed\?(\s)*No|Testing needed:\
        *(\s)*No|no *testing",
        note,
        re.IGNORECASE | re.MULTILINE,
    ):
        test_stat = "No testing"
    return test_stat


def other_note(note):
    other_note = ""
    if re.search(r"test\s*notes:*(\s)*\".*\"", note, re.IGNORECASE | re.MULTILINE):
        m = re.search(r"\".*\"", note, re.IGNORECASE | re.MULTILINE)
        other_note = m.group()[1:-1]
    return other_note


def parse_committer_name(name):
    if re.search(r"\.", name):
        split_name = name.split(".")
        first_name = split_name[0][0].upper() + split_name[0][1:]
        last_name = split_name[1][0].upper() + split_name[1][1:]
        parsed_name = first_name + " " + last_name
        return parsed_name
    else:
        return name


def log_insert(text, level):
    logger = logging.getLogger("test_info")
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler("TestInfo_ctr.log")
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)

    formatter = logging.Formatter(
        fmt="%(asctime)-10s:\
            %(levelname)-8s %(message)s",
        datefmt="%m-%d %H:%M",
    )
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(ch)
        logger.addHandler(fh)

        if level == logging.DEBUG:
            logger.debug(text)
        elif level == logging.INFO:
            logger.info(text)
        elif level == logging.WARNING:
            logger.warning(text)
        elif level == logging.ERROR:
            logger.error(text)

    fh.close()
    ch.close()
    logger.removeHandler(fh)
    logger.removeHandler(ch)

    return ()


def check_tag(version):
    return re.search(r"^3\.\d+\.\d+\.\d+(-RC\d+)?$", version)


def commit_details_map(commit_details_value, test_list):
    """Comit details value checks with test_list
    Args:
      commit_details_value: commit_detail.is_test, commit_detail.need_test, commit_detail.test_stat.
      test_list: The test_list are dictionary value of test_info, test_needed and test_stat.
    Returns:
      The test_list counts
    """
    for key in test_list.keys():
        if commit_details_value == key:
            test_list[key] += 1
            return test_list[key]


def cmd_line_args():
    parser = argparse.ArgumentParser(
        prog="creat_test_summary.py",
        usage="%(prog)s <since_tag>\
        [-t2 <until_tag>] [-b <branch>]",
        description="This script generates\
        a gitlab wiki page with information on testing the release commits.",
    )

    parser.add_argument(
        "t1",
        help="VCenter tag e.g: 3.13.4.0 or 3.13.4.0-RC1, \
        This is the mandatory since tag, it will fetch all commits since its creation date.",
    )

    parser.add_argument(
        "-t2",
        "--untilTag",
        help="Add until tag to commits list,\
        commits will be fetched since <since_tag> until <until_tag>.",
    )

    parser.add_argument(
        "-b", "--branch", help="Change branch name, default is develop."
    )
    return parser.parse_args()
