#!/usr/bin/env python3
# 
#  Copyright (c) 2024 Vimec Applied Vision Technology B.V.
# 

# nagaan: lege assignees worden momenteel niet geprint, is goed maar waarom?
# hyperlink stopt bij gitlab en niet naar issue..   https://docs.microsoft.com/nl-nl/office/troubleshoot/error-messages/cannot-locate-server-when-click-hyperlink
# timestamp in outputfilename

import re, sys, traceback, os, datetime, xlsxwriter
import gitlab_export


def keep_unique_entries(total_list):
    return list(set(total_list))


def get_assignees_and_milestones(issues_export):
    total_assignees = []
    total_milestones = []

    for issue in issues_export:
        for assignee in issue["assignees"]:
            assignee_name = assignee["name"].strip()
            if len(assignee_name):
                total_assignees.append(assignee_name)

        if issue["milestone"]:
            # for milestone in issue["milestone"]: #should become a list in gitlab 13.1?
            milestone_name = issue["milestone"]["title"].strip()
            if len(milestone_name):
                total_milestones.append(milestone_name)

    total_assignees = keep_unique_entries(total_assignees)
    total_milestones = keep_unique_entries(total_milestones)

    return total_assignees, total_milestones


def filter_planning_milestones(milestones, filter):
    filtered_milestones = []
    for milestone in milestones:
        if filter in milestone.lower():
            filtered_milestones.append(milestone)
    return filtered_milestones


def sort_milestones(milestones):
    sorted_milestones = []
    max_week_numbers =[]

    for milestone in milestones:
        digits_in_milestone = [int(i) for i in re.findall(r'\d+', milestone)]
        max_week_number = max(digits_in_milestone)
        sorted_milestones.append(milestone)
        max_week_numbers.append(max_week_number)

    # sort on week numbers
    sorted_milestones = [x for _, x in sorted(zip(max_week_numbers, sorted_milestones))]

    return sorted_milestones


def create_data_structure(milestones,assignees):
    data_structure={}
    for m in milestones:
        data_structure[m]={}
        for a in assignees:
            data_structure[m][a]=[]
    return data_structure


def populate(data_structure, issues_export):
    issues = data_structure
    for issue in issues_export:
        if not(issue["milestone"]):
            continue
        milestone_name = issue["milestone"]["title"].strip()
        if milestone_name not in data_structure:
            continue

        for assignee in issue["assignees"]:
            assignee_name = assignee["name"].strip()
            if assignee_name not in data_structure[milestone_name]:
                continue

            issues[milestone_name][assignee_name].append(issue)
    return issues


def wanted_info(issue, gitlab_projects):
    project = gitlab_projects[issue['project_id']]
    data = str(project['name']) + "-" + str(issue['iid']) + ":" + issue['title']
    return data


def create_excel_file(assignees, milestones, issues, output_folder, gitlab_projects):
    year_month_day = datetime.date.today()
    year, week_num, day_of_week = year_month_day.isocalendar()
    output_file = output_folder + "Week " + str(week_num) + " planning.xlsx"

    longest_assignee_name = max(assignees, key=len)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Create a workbook and add a worksheet.
    workbook = xlsxwriter.Workbook(output_file)
    worksheet = workbook.add_worksheet()

    cell_format_issue_closed = workbook.add_format()
    cell_format_issue_closed.set_bg_color('#92D050')         # light green
    cell_format_issue_open_overdue = workbook.add_format()
    cell_format_issue_open_overdue.set_bg_color('orange')

    column_index_assignee = 0                                # Rows and columns are zero indexed.
    column_index_overdue = 1
    column_index_milestone = column_index_overdue

    worksheet.write(0, column_index_assignee, 'Assignee')
    worksheet.set_column(column_index_assignee, column_index_assignee, len(longest_assignee_name))  # Column width
    worksheet.write(0, column_index_milestone, 'Overdue')
    worksheet.set_column(column_index_milestone, column_index_milestone, 80)
    row_index = 1

    for milestone in milestones:
        digits_in_milestone = [int(i) for i in re.findall(r'\d+', milestone)]
        max_week_number = max(digits_in_milestone)
        if max_week_number >= week_num:   # otherwise append to 'Overdue' column
            column_index_assignee += 3    # columns: assignee, issue and 1 blank column for spacing
            column_index_milestone += 3
            worksheet.write(0, column_index_assignee, 'Assignee')
            worksheet.set_column(column_index_assignee, column_index_assignee, len(longest_assignee_name))   # Column width
            worksheet.write(0, column_index_milestone, milestone)
            worksheet.set_column(column_index_milestone, column_index_milestone, 80)

            row_index = 1

        if milestone in issues:
            for assignee in issues[milestone]:
                for issue in issues[milestone][assignee]:
                    if column_index_milestone == column_index_overdue:
                        if issue['state'] == 'closed':
                            continue
                        else:
                            worksheet.write(row_index, column_index_assignee, assignee, cell_format_issue_open_overdue)
                    else:
                        if issue['state'] == 'closed':
                            worksheet.write(row_index, column_index_assignee, assignee, cell_format_issue_closed)
                        else:
                            worksheet.write(row_index, column_index_assignee, assignee)

                    worksheet.write_url(row_index, column_index_milestone, issue['web_url'], string=wanted_info(issue, gitlab_projects))
                    row_index += 1

    workbook.close()


def main():
    gitlab_groups = gitlab_export.get_groups()
    gitlab_projects = gitlab_export.get_projects()

    combinations = [
        {"output_folder": "Z:\\BuildServer\\Gitlab planning\\Agro & Food (Beltech SVC)\\",
         "gitlab_groups": ["Beltech", "SVC"]},
        {"output_folder": "Z:\\BuildServer\\Gitlab planning\\Internal (OOAKT)\\",
         "gitlab_groups": ["OOAKT"]},
        #{"output_folder": "Z:\\BuildServer\\Gitlab planning\\Pharma (Vimec)\\",
        # "gitlab_groups": ["Vimec"]}
    ]

    for combination in combinations:
        issues_export = []
        assignees = []
        milestones = []
        for gitlab_group_name in combination['gitlab_groups']:
            gitlab_group = gitlab_groups[gitlab_group_name]
            issues_export += gitlab_export.get_issues_by_group_id(gitlab_group['id'])

            group_assignees, group_milestones = get_assignees_and_milestones(issues_export)
            assignees += group_assignees
            milestones += group_milestones

        assignees = keep_unique_entries(assignees)
        milestones = keep_unique_entries(milestones)

        milestones = filter_planning_milestones(milestones, "week")
        milestones = sort_milestones(milestones)  # week 3-4, week 1-2 -> week 1-2, week 3-4

        data_structure = create_data_structure(milestones, assignees)
        issues = populate(data_structure, issues_export)

        create_excel_file(assignees, milestones, issues, combination['output_folder'], gitlab_projects)


if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        pass
    except Exception:
        traceback.print_exc(file=sys.stdout)
    sys.exit(1)


