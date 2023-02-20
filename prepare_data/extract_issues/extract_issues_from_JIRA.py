import os
import requests
import sys
import time
import json

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import extract_num_issues_from_JIRA


NUM_ONE_ITE_ISSUES = 50 # number of processed issues at one session
BASE_URL = "https://issues.apache.org/jira/rest/api/2/search" # base url
PROJECT_NAME_LIST = ["your project here"]

def extract_issue(session=None, query=None):
    """
    Extract issue content from a target issue id

    Arguments:
    session: [session object] -- session object to a target base url
    query: [string] -- query

    Returns:
    content.text: [string] -- output to be stored
    """
    if session==None:
        return "@@@MASA CHECK@@@ No session"
    if query==None:
        return "@@@MASA CHECK@@@ No target URL"

    r_obj = session.get(BASE_URL + "/" + query, timeout=(10.0, 30.0))

    return r_obj


def run(p_name, num_total_issues, retries=3, backoff_factor=1, status_forcelist=(500, 502, 504)):
    """
    Extract issue information from JIRA and store it to local disc.
    The interval for each execution is 5 seconds

    Arguments:
    retries [int] -- number of retries
    backoff_factor [int] -- the base of interval for each retry
    status_forcelist [tuple<int>] -- HTTP error code that we need to rerun
    """
    print("process project (extract issues): {0}".format(p_name))

    with requests.Session() as s:
        output_file_dir = './issues_list'

        retry = Retry(total=retries, read=retries, connect=retries, backoff_factor=backoff_factor, status_forcelist=status_forcelist)
        adapter = HTTPAdapter(max_retries=retry)
        s.mount("https://", adapter)


        print("num total issues: {0}".format(num_total_issues))
        num_ite = int(num_total_issues/NUM_ONE_ITE_ISSUES) + 1
        for ite in range(num_ite):
            print("ite: {0}".format(ite))

            query = "?fields=key,status,issuetype&jql=PROJECT={0}&startAt={1}".format(p_name, ite*50)
            output_file_path = output_file_dir + "/{0}_{1}_issue_list.txt".format(p_name, ite)
            error_output_file_path = output_file_dir + "/error_{0}_{1}_issue_list.txt".format(p_name, ite)

            content = ""

            try:
                r_obj = extract_issue(session=s, query=query)
            except Exception:
                print("it failed: {0}".format(ite))
                with open(error_output_file_path, "w") as f:
                    f.write("It failed: {0}".format(ite))
                time.sleep(6)
                continue

            if r_obj.status_code==requests.codes.ok:
                content = r_obj.text
                with open(output_file_path, "w") as f:
                    f.write(content)
            else:
                print("it failed (read): {0}".format(ite))
                with open(error_output_file_path, "w") as f:
                    f.write("It failed")
            time.sleep(6)



def main(p_name):
    """
    The main script. For each session, we process NUM_ONE_ITE_URL issue ids and
    wait 10 seconds

    Arguments:
    p_name [string] -- project name
    """

    extract_num_issues_from_JIRA.run(p_name)

    with open("issues_list/{0}_total.txt".format(p_name), 'r', encoding='utf-8') as f:
        temp_data = json.load(f)
    num_total_issues = int(temp_data['total'])

    run(p_name, num_total_issues)

if __name__=="__main__":
    for p_name in PROJECT_NAME_LIST:
        main(p_name)

