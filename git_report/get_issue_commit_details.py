#!/usr/bin/env python3
#
#  Copyright (c) 2024 Vimec Applied Vision Technology B.V.
#

import datetime
import test_info
import create_test_summary as summery
from collections import defaultdict
import common


class CommitDetail:
    def __init__(self):
        self.author = ""
        self.date = ""
        self.is_test = ""
        self.issue = "None"
        self.msg = ""
        self.need_test = ""
        self.web_url = ""
        self.test_stat = ""
        self.other_note = ""
        self.title = ""

    def __str__(self):
        return "| {} | {} | {} | {} | {} | {} | {} | {} | {} |".format(
            self.issue,
            self.author,
            self.date,
            self.msg,
            common.print_shape(self.is_test),
            common.print_shape(self.need_test),
            common.print_shape(self.test_stat),
            self.other_note,
            self.web_url,
            self.title,
        )


def past_time(time_ago):
    parsed_time = [time_ago.split()[:2]]
    time_dict = dict((fmt, float(amount)) for amount, fmt in parsed_time)
    dt = datetime.timedelta(**time_dict)
    p_time = datetime.datetime.now() - dt
    return p_time.strftime("%Y-%m-%d")


def get_branch_name(branch):
    return branch


def get_tag_name(project, tag_name):
    if tag_name:
        tag = project.tags.get("{}".format(tag_name))
        tag_created_time = tag.commit["created_at"]
    else:
        tag_created_time = past_time("6 weeks ago")
    return tag_created_time


def get_until_tag(project, until_tag):
    if until_tag:
        until_tag = project.tags.get("{}".format(until_tag))
        tag_until_time = until_tag.commit["created_at"]
    else:
        tag_until_time = datetime.datetime.today().strftime("%Y-%m-%d")
    return tag_until_time


# ---------------------------------------------------------------------------
# @function get_issues_commit_details: geting issue details, commit and branch name from gitlab
# @parameter project, tag_name, until_tag and branch
# @comment: commit_detail.issue found any issue then return issue details, commit and branch name
# ---------------------------------------------------------------------------
def get_issues_commit_details(project, tag_name, until_tag, branch):

    branch_name = get_branch_name(branch)
    tag_created_time = get_tag_name(project, tag_name)
    tag_until_time = get_until_tag(project, until_tag)

    print(
        "branch: {} tage_date: {} tag_until: {}".format(
            branch_name, tag_created_time, tag_until_time
        )
    )

    commits = project.commits.list(
        all=True,
        query_parameters={
            "ref_name": branch_name,
            "since": tag_created_time,
            "until": tag_until_time,
        },
    )

    issue_dict = defaultdict(list)
    issues_list = []
    for commit in commits:
        print(commit.short_id, " : ", commit.title)
        commit_detail = CommitDetail()
        commit_detail.date = common.parse_committed_date(commit.committed_date)
        commit_detail.issue = common.detect_issue(commit.title)

        if commit_detail.author == "":
            commit_detail.author = common.parse_committer_name(commit.author_name)

        if commit_detail.issue == "None":
            commit_detail.issue = common.detect_issue_from_mr(
                commit.merge_requests()[0]["description"]
            )

        commit_detail.web_url = commit.web_url
        common.log_insert(
            "++++++++++++++++++++++++++++++++++++\
            ++++++++++++++++++++++++++++++++++++++",
            common.logging.INFO,
        )
        common.log_insert(commit_detail.issue, common.logging.INFO)

        commit_detail.msg = commit.title
        issue_id = commit_detail.issue[2:6]
        commit_detail.title = commit.merge_requests()[0]["title"].replace(
            "Resolve ", ""
        )

        if (
            (commit_detail.issue != "None")
            and (issue_id not in issues_list)
            and (commit_detail.author not in ["vicbot", "vicbot2", "api2025"])
        ):
            issues_list.append(issue_id)

            try:
                issue = project.issues.get(issue_id)
                if issue.state != "closed":
                    common.log_insert(
                        f"Issue #{issue.id} is not closed; skipping.",
                        common.logging.INFO,
                    )
                    continue
            except Exception:
                pass
            notes_list = issue.notes.list()

            for (
                note
            ) in (
                notes_list
            ):  # Search each note for regex matches of Test info and no testing
                common.log_insert(note.body, common.logging.INFO)
                if not commit_detail.is_test:
                    commit_detail.is_test = common.is_test_info(note.body)

                if not commit_detail.need_test and branch_name == "develop":
                    commit_detail.need_test = test_info.need_test(note.body)
                elif not commit_detail.need_test and branch_name != "develop":
                    commit_detail.need_test = summery.need_test(note.body)

                if not commit_detail.test_stat:
                    commit_detail.test_stat = common.test_stat(note.body)
                if not commit_detail.other_note:
                    commit_detail.other_note = common.other_note(note.body)

            if not commit_detail.is_test:
                commit_detail.is_test = "No"

            if branch_name == "develop":
                if not commit_detail.need_test:
                    commit_detail.need_test = "Yes"
                issue_dict[commit.short_id].append(commit_detail)
            else:
                if not commit_detail.need_test:
                    commit_detail.need_test = "Unknown"
                    commit_detail.test_stat = "Unknown"

                if not commit_detail.test_stat:
                    commit_detail.test_stat = "Not yet"

                issue_dict[commit.short_id].append(commit_detail)

        # if there is no issue attached to the commit.
        elif commit_detail.issue == "None":
            commit_detail.is_test = "?"
            commit_detail.need_test = "?"
            commit_detail.test_stat = "No issue"
            warning = "No issue found for commit: " + commit.short_id
            common.log_insert(warning, common.logging.WARNING)

    return issue_dict, commits, branch_name
