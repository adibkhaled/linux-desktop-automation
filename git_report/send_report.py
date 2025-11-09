#!/usr/bin/env python3
#
#  Copyright (c) 2024 Vimec Applied Vision Technology B.V.
#

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import time

import common
import get_issue_commit_details as issue_details
import test_info
import create_test_summary as summery
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


mailserver = "smtp.vimec.nl"
mailserver_port = 25
subject_missing = "Missing Test Info.."
subject_overview = "Test Info Overview.."
sender_email = "adib.binkhaled@vimec.nl"
login_name = sender_email
login_password = ""
commit_log_file = "Commits_Log_ctr.txt"

recipient_list = ["manisha.navgire", "adib.binkhaled"]


def create_email(name):
    step = name.split(maxsplit=1)
    name_address = ".".join(step).lower().replace(" ", "")
    if name != "LI Junting":
        email = name_address + "@vimec.nl"
        return email
    else:
        return sender_email


def send_email(message, recipient, subject):
    # Log in to server using secure context and send email
    server = smtplib.SMTP(mailserver, mailserver_port)
    server.ehlo()

    if len(login_password) > 0:
        server.login(login_name, login_password)
    try:
        print("Sending email [" + subject + "] to", recipient, "..")
        server.sendmail(sender_email, recipient, message)
        server.quit()
    except smtplib.SMTPRecipientsRefused as ex:
        print(
            "Email [" + subject + "] was NOT sent, exception caught:",
            getattr(ex, "message", repr(ex)),
        )


def send_report(file, recipient, subject):
    # Create a multipart message and set headers
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = recipient

    with open(file, "r", encoding="utf-8") as f:
        html = f.read()

    part = MIMEText(html, "html")
    message.attach(part)

    send_email(message.as_string(), recipient, subject)


def send_overview(file, recipient, subject):
    # Create a multipart message and set headers
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = recipient

    with open(file, "r", encoding="utf-8") as f:
        html = f.read()

    part = MIMEText(html, "html")
    message.attach(part)

    send_email(message.as_string(), recipient, subject)


# ---------------------------------------------------------------------------
# @function send_overview_missing_mail: To send missing and overview mail
# @comment: Using develop branch to send the mail.
# ---------------------------------------------------------------------------
def send_overview_missing_mail():
    final_items_ctr_html = "final_items_ctr.html"
    project = common.init_project()

    issue_dict, commits, final_branch = issue_details.get_issues_commit_details(
        project, tag_name=None, until_tag=None, branch="develop"
    )
    is_test, is_info, num = test_info.output_to_file(issue_dict, commit_log_file)
    unique_dict = test_info.single_commits(commits, issue_dict)

    overview_text = """
    
    Hi, <br><br>
    
    Please find below an overview of test iformation availability:<br><br>
        All commits (On develop branch ): {} <br>
        Commits with test info: {} <br>
        Commits with no test info: {} <br>
        Commits with no issue connected: {} <br>
    
        """.format(
        num, is_info["Yes"], is_info["No"], is_info["None"]
    )

    for name, ids in unique_dict.items():
        if len(ids) > 0:
            out_file, total_file = test_info.generate_output_html(ids, issue_dict, name)
            send_report(out_file, create_email(name), subject_missing)
            time.sleep(0.5)

    with open(final_items_ctr_html, "w", encoding="utf-8") as f:
        f.write(overview_text)

    with open("all_items_ctr.html", encoding="utf-8") as f:
        final_html = f.read()

    with open(final_items_ctr_html, "a", encoding="utf-8") as f:
        f.write(final_html)

    with open(final_items_ctr_html, "a", encoding="utf-8") as f:
        f.write("<br>Thanks.<br>")

    for recipient in recipient_list:
        recipient_address = recipient + "@vimec.nl"
        send_overview(final_items_ctr_html, recipient_address, subject_overview)


# ---------------------------------------------------------------------------
# @function create_gitLab_report: To create gitlab report in wiki page
# @comment: Using release brach by using command line args
# @comment: vic_tag e.g: 3.13.4.0 or 3.13.4.0-RC1
# @comment: until_tag e.g: 3.13.4.0 or 3.13.4.0-RC1
# ---------------------------------------------------------------------------


def create_gitlab_report():
    args = common.cmd_line_args()
    vic_tag = args.t1
    until_tag = args.untilTag
    branch = args.branch
    final_item_file = "final_items_ctr.txt"

    if common.check_tag(vic_tag):
        project = common.init_project()
    else:
        print(
            "Version incorrect tag format: 3.<major>.<minor>.<patch>[.RC<num>]\
               e.g: 3.13.4.0 or 3.13.4.0-RC1"
        )

    issue_dict, commits, final_branch = issue_details.get_issues_commit_details(
        project, vic_tag, until_tag, branch
    )
    is_info, need_test, test_stat, num = summery.output_to_file(
        issue_dict, commit_log_file
    )

    if until_tag:
        title = "Releases/{}_{}_{}".format(vic_tag, until_tag, final_branch)
    else:
        title = "Releases/{}_{}".format(vic_tag, final_branch)

    overview_text = ""
    if num == 0:
        print("No issues found!")
    else:
        overview_text = """
        Branch is: {}
        Start tag is: {}
        End tag is: {} 
        ----------------------------------------------------------
        Overview of test information and status for release items:
            All commits: {}
                ❓   No issue connected: {} ({})
                ❓   No info available: {} ({})
                ✅  Info available: {} ({})
                        ❎  No testing needed: {} ({})
                        🔎  Testing needed: {} ({})
                                ✅  Passed: {} ({})
                                ❌  Failed: {} ({})
                                ⛔  Blocked: {} ({})
                                ▶️  Ongoing: {} ({})
                                ❔   Not tested yet: {} ({})

            \n""".format(
            final_branch,
            vic_tag,
            until_tag,
            num,
            is_info["None"],
            str(round(is_info["None"] / num * 100)) + "%",
            is_info["No"],
            str(round(is_info["No"] / num * 100)) + "%",
            is_info["Yes"],
            str(round(is_info["Yes"] / num * 100)) + "%",
            need_test["No"],
            str(round(need_test["No"] / num * 100)) + "%",
            need_test["Yes"],
            str(round(need_test["Yes"] / num * 100)) + "%",
            test_stat["Pass"],
            str(round(test_stat["Pass"] / num * 100)) + "%",
            test_stat["Fail"],
            str(round(test_stat["Fail"] / num * 100)) + "%",
            test_stat["Blocked"],
            str(round(test_stat["Blocked"] / num * 100)) + "%",
            test_stat["Ongoing"],
            str(round(test_stat["Ongoing"] / num * 100)) + "%",
            test_stat["Not yet"],
            str(round(test_stat["Not yet"] / num * 100)) + "%",
        )

    with open(final_item_file, "w", encoding="utf-8") as f:
        f.write(overview_text)

    with open(commit_log_file, encoding="utf-8") as f:
        final_text = f.read()

    with open(final_item_file, "a", encoding="utf-8") as f:
        f.write(final_text)

    pages = project.wikis.list()
    l = len(pages)
    print("\n")
    for i in range(l):
        if pages[i].slug == title:
            page = project.wikis.get(title)
            page.delete()
            print(f"Page {title} is deleted!")

    project.wikis.create(
        {"title": title, "content": open(final_item_file, encoding="utf-8").read()}
    )
    print(f"Page {title} is created!")
    link = "{URL_CI}/myapp/wikis/" + title
    print("Page link:")
    print(link)
