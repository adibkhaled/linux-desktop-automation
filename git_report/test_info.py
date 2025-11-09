#!/usr/bin/env python3
#
#  Copyright (c) 2024 Vimec Applied Vision Technology B.V.
#

import common
import send_report
import datetime
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ---------------------------------------------------------------------------
# @function need_test: Search issues for need test keyword
# @parameter note: issue notes
# @comment: Pass need_test value to filter those issue which donot have test info
# ---------------------------------------------------------------------------
def need_test(note):
    if re.search(
        r"Testing needed\?\nNo|Testing needed\nNo|no *testing",
        note,
        re.IGNORECASE | re.MULTILINE,
    ):
        need_test = "No"
        return need_test


def single_commits(commits, issue_dict):
    author_dict = {}
    unique_dict = {}
    for commit in commits:
        if (
            ("vicbot" not in commit.author_name)
            and ("vicbot2" not in commit.author_name)
            and ("api2025" not in commit.author_name)
        ):
            author_dict[commit.short_id] = common.parse_committer_name(
                commit.author_name
            )

    names = set(author_dict.values())
    for name in names:
        unique_dict[name] = []
        for short_id in author_dict.keys():
            if (author_dict[short_id] == name) and (issue_dict[short_id]):
                if issue_dict[short_id][0].is_test == "No":
                    unique_dict[name].append(short_id)
    print(unique_dict)
    return unique_dict


def generate_output_file(no_info_list, issue_dict, person):
    output = "| Commit | Issue | Title | Test Info Available |\n"
    output += "| ------ | ------ | ------ | ------ |\n"
    for commit_id in no_info_list:
        output += "| {} ".format(commit_id)
        output += "| {} ".format(issue_dict[commit_id][0].issue)
        output += "| {} ".format(issue_dict[commit_id][0].title)
        output += "| {} |\n".format(issue_dict[commit_id][0].is_test)

    out_file = "_".join(person.split()) + "_ctr.txt"
    with open(out_file, "w", encoding="utf-8") as file:
        file.write(output)
    return out_file


def generate_output_html(no_info_list, issue_dict, person):
    if len(no_info_list) > 0:
        out_file = "_".join(person.split()) + "_ctr.html"
        total_file = "all_items_ctr.html"

        row_file = "git_report/html/HTML_Testing_Table_Row_Template.txt"
        template_file = "git_report/html/HTML_Testing_Table_Template.txt"
        started = False
        for commit_id in no_info_list:
            if issue_dict[commit_id][0].issue != "None":
                link = (
                    "https://gitlab.vimec.nl/Vimec/v-center-linux/-/issues/{}".format(
                        issue_dict[commit_id][0].issue[2:6]
                    )
                )
            else:
                link = "None"

            fin1 = open(row_file, "rt", encoding="utf-8")

            contents = fin1.read()
            replaced = contents.replace("COMMIT_DATA", commit_id)
            if link == "None":
                replaced = replaced.replace(
                    '<a href="ISSUE_LINK">ISSUE</a>', "ISSUE</a>"
                )
                replaced = replaced.replace("ISSUE</a>", issue_dict[commit_id][0].issue)
            replaced = replaced.replace("ISSUE_LINK", link)
            replaced = replaced.replace("COMMIT_LINK", issue_dict[commit_id][0].web_url)
            replaced = replaced.replace("ISSUE", issue_dict[commit_id][0].issue[1:6])
            replaced = replaced.replace("TITLE_DATA", issue_dict[commit_id][0].title)
            replaced = replaced.replace("IS_INFO", issue_dict[commit_id][0].is_test)
            replaced += "\nROW_INFO_HERE"
            fin1.close()
            if not started:
                fin2 = open(template_file, "rt", encoding="utf-8", errors="ignore")
                all_contents = fin2.read()
                new_replaced = all_contents.replace("ROW_INFO_HERE", replaced)
                fout = open(out_file, "wt", errors="ignore")

                fout.write(new_replaced)
                fout.close()

            else:
                fin2 = open(out_file, "rt", encoding="utf-8", errors="ignore")
                all_contents = fin2.read()
                new_replaced = all_contents.replace("ROW_INFO_HERE", replaced)
                fout = open(out_file, "w")

                fout.write(new_replaced)
                fout.close()

            started = True

        with open(out_file, encoding="utf-8", errors="ignore") as f:
            new_text = f.read().replace("ROW_INFO_HERE", "")

        with open(total_file, "a", encoding="utf-8", errors="ignore") as f:
            f.write(new_text)

        with open(out_file, "w", encoding="utf-8", errors="ignore") as f:
            f.write(new_text)

            person_name = str(person.split()[0])
            text = """
    
    Hi {}, <br><br>
    
    There are some issues on which you have worked on that do not have any test information yet. Please add this info as a comment to the issue.<br> 
    The template for test info can be retrieved in: {URL_CI}/Vimec/v-center-linux/-/blob/develop/documentation/ReleaseProcess.md <br><br>
        
    Thanks.<br>
    
        """.format(
                person_name
            )

        with open(out_file, encoding="utf-8") as f:
            new_text = f.read().replace("TEXT_TO_BE_ADDED", text)

        with open(out_file, "w", encoding="utf-8") as f:
            f.write(new_text)

        with open(total_file, encoding="utf-8") as f:
            all_text = f.read().replace("TEXT_TO_BE_ADDED", person_name)

        with open(total_file, "w", encoding="utf-8") as f:
            f.write(all_text)

        return (out_file, total_file)


def output_to_file(issue_dict, output_file):
    num = 1

    test_info = {"Yes": 0, "No": 0, "None": 0}
    test_needed = {"Yes": 0, "No": 0, "None": 0}

    output = "| # | Commit | Issue | Author | Title | Test Info Available | Test needed | Other Notes |\n"
    output += (
        "| ------ | ------ | ------ | ------ | ------ | ------ | ------ | ------ |\n"
    )
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

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(output)

    return (test_info, test_needed, num - 1)


def check_day_to_run(day_to_run):
    day = datetime.datetime.today().strftime("%A")
    return day_to_run if day == day_to_run else None


def main():
    monday, wednesday = "Monday", "Wednesday"
    if check_day_to_run(monday) or check_day_to_run(wednesday) is not None:
        common.clean_dir()
        common.clean_log()
        send_report.send_overview_missing_mail()
        common.clean_dir()
    else:
        print("Runs only: " + monday + " or " + wednesday)


if __name__ == "__main__":
    main()
