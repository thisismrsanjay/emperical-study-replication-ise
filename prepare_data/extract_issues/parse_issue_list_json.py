import glob
import json
import os
import sqlite3
import sys

from Utils import util

PROJECT_NAME_LIST = ["your project here"]
NUM_ONE_ITE_ISSUES = 50 # number of processed issues at one session

issuetype_categories_set = set(["Bug"])
status_categories_set = set(["Resolved", "Closed"])

def extract_issue_ids(p_name, num_total_issues):

    print("num total issues: {0}".format(num_total_issues))
    num_ite = int(num_total_issues/NUM_ONE_ITE_ISSUES) + 1
    issue_id_list = []
    for ite in range(num_ite):

        with open("issues_list/{0}_{1}_issue_list.txt".format(p_name, ite), 'r', encoding='utf-8') as f:
            temp_data = json.load(f)

        for issue_data in temp_data['issues']:

            if not issue_data['fields']['issuetype']["name"] in issuetype_categories_set:
                continue
            if not issue_data['fields']['status']["name"] in status_categories_set:
                continue

            issue_id_list.append(issue_data['key'])
    
    print("Number of extracted issues: {0}".format(len(issue_id_list)))
    util.dump_pickle("issues_list/{0}_issue_list.pickle".format(p_name), issue_id_list)

def main(p_name):

    with open("issues_list/{0}_total.txt".format(p_name), 'r', encoding='utf-8') as f:
        temp_data = json.load(f)
    num_total_issues = int(temp_data['total'])

    extract_issue_ids(p_name, num_total_issues)

if __name__=="__main__":
    for p_name in PROJECT_NAME_LIST:
        main(p_name)

