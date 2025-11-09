#!/usr/bin/env python3
# 
#  Copyright (c) 2024 Vimec Applied Vision Technology B.V.
# 

import re
import common
import send_report

# ---------------------------------------------------------------------------
# @function need_test: Search issues for need test keyword
# @parameter note: issue notes
# @comment: Pass need_test value to filter those issue which need test
# ---------------------------------------------------------------------------
def need_test(note):
    need_test = ""
    if re.search(
        r"Testing needed\?(\s)*No|Testing needed:\
        *(\s)*No|no *testing",
        note,
        re.IGNORECASE | re.MULTILINE,
    ):
        need_test = "No"
    elif re.search(
        r"Testing needed\?(\s)*yes|Testing needed:\
        *(\s)*yes|test\s*needed|needs*\s*test",
        note,
        re.IGNORECASE | re.MULTILINE,
    ):
        need_test = "Yes"
    return need_test


def output_to_file(issue_dict, output_file):
    num = 1
    unknown_value = 0
    test_info = {"Yes": 0, "No": 0, "None": 0}
    test_needed = {"Yes": 0, "No": 0, "None": 0}
    test_stat = {
        "Pass": 0,
        "Fail": 0,
        "Blocked": 0,
        "Ongoing": 0,
        "No testing": 0,
        "Not yet": 0,
        "Unknown": unknown_value,
        "No issue": unknown_value,
    }

    output = "| # | Commit | Issue | Author | Commit Date | Title |\
             Test Info Available | Test Needed | Test Status | Other Notes |\n"

    output += "| ------ | ------ | ------ | ------ | ------ |\
                 ------ | ------ | ------ | ------ | ------ |\n"
    for issue, commit_details in issue_dict.items():

        output += "| {} | {} ".format(num, issue)
        num += 1
        one_commit = True
        for commit_detail in commit_details:
            if not one_commit:
                output += "| "
            one_commit = False
            output += "{}\n".format(commit_detail)
            common.commit_details_map(commit_detail.is_test, test_info)
            common.commit_details_map(commit_detail.need_test, test_needed)
            common.commit_details_map(commit_detail.test_stat, test_stat)

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(output)

    return (test_info, test_needed, test_stat, num - 1)


def main():
    common.clean_dir()
    common.clean_log()
    send_report.create_gitlab_report()
    common.clean_dir()


if __name__ == "__main__":
    main()
