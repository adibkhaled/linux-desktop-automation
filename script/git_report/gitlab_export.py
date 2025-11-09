#!/usr/bin/env python3
#
#  Copyright (c) 2024 Vimec Applied Vision Technology B.V.
#
"""
Export issues from Gitlab into a CSV, using private token authentication.
 - uses private token authentication
 - uses Gitlab API v4
 - uses python3
"""

import csv, requests
import os, sys, traceback


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def sprint(*args, **kwargs):
    print(*args, file=sys.stdout, **kwargs)


def show_usage():
    eprint("Usage: " + os.path.basename(__file__) + " <option>")
    eprint("   description of the script operations")


def get_json(response):
    if not response.status_code == 200:
        raise Exception(response.status_code)
    return response.json()


def get_pages(response):
    pages = dict(
        [
            (rel[6:-1], url[url.index("<") + 1 : -1])
            for url, rel in [
                link.split(";") for link in response.headers["link"].split(",")
            ]
        ]
    )
    return pages


def https_query(url):
    return requests.get(
        url, headers={"PRIVATE-TOKEN": PRIVATE_TOKEN}, verify=False
    )


def gitlab_query(url):
    result = []
    response = https_query(url)
    result += get_json(response)

    # more pages? examine the 'link' header
    if not "link" in response.headers:
        return

    pages = get_pages(response)
    currentpage = ""
    while "last" in pages and "next" in pages:
        currentpage = pages["next"]
        response = https_query(currentpage)
        pages = get_pages(response)
        result += get_json(response)

        if currentpage == pages["last"]:
            break
    return result


def write_issue(issue):
    print(issue["title"], issue["state"])
    labels = issue["labels"]
    print("labels:", labels)


server_url = "{URL_CI}/api/v4"


def get_groups():
    result = dict()
    groups = gitlab_query("{}/groups?scope=all".format(server_url))
    for group in groups:
        result[group["name"]] = group
    return result


def get_projects():
    result = dict()
    projects = gitlab_query("{}/projects?scope=all".format(server_url))
    for project in projects:
        result[project["id"]] = project
    return result


def get_issues_by_group_id(group_id):
    return gitlab_query("{}/groups/{}/issues?scope=all".format(server_url, group_id))


def main():
    if len(sys.argv) != 1:
        eprint("error: invalid argument(s)\n")
        show_usage()
        return 1

    # csvfile = 'issues.csv'
    # print("file: ", csvfile)
    # csvout = csv.writer(open(csvfile, 'wb'))
    # csvout.writerow(('id', 'Title', 'Body', 'Created At', 'Updated At'))

    groups = get_groups()
    ooakt_group = groups["OOAKT"]
    issues = get_issues_by_group_id(ooakt_group["id"])
    for issue in issues:
        print(issue)

    groups = get_groups()
    for group in groups:
        print(group)

    print("done.")
    print(len(issues), "issues.")
    print(len(groups), "groups.")
    print("ooakt_group['id']: ", ooakt_group["id"])


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc(file=sys.stdout)
    show_usage()
    sys.exit(1)
