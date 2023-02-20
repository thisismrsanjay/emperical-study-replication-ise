from extract_data_from_JIRA import PROJECT_NAME_LIST
import os
import requests
import sys
import time

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


NUM_ONE_ITE_URL = 100 # number of processed issues at one session
BASE_URL = "https://issues.apache.org/jira/rest/api/2/search" # base url
#PROJECT_NAME_LIST = []

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


def run(p_name, retries=3, backoff_factor=1, status_forcelist=(500, 502, 504)):
    """
    Extract issue information from JIRA and store it to local disc.
    The interval for each execution is 5 seconds

    Arguments:
    retries [int] -- number of retries
    backoff_factor [int] -- the base of interval for each retry
    status_forcelist [tuple<int>] -- HTTP error code that we need to rerun
    """
    print("process project: {0}".format(p_name))

    with requests.Session() as s:
        output_file_dir = './issues_list'

        retry = Retry(total=retries, read=retries, connect=retries, backoff_factor=backoff_factor, status_forcelist=status_forcelist)
        adapter = HTTPAdapter(max_retries=retry)
        s.mount("https://", adapter)

        query = "?fields=total&jql=PROJECT={0}".format(p_name)
        output_file_path = output_file_dir + "/{0}_total.txt".format(p_name)
        error_output_file_path = output_file_dir + "/error_{0}_total.txt".format(p_name)

        try:
            r_obj = extract_issue(session=s, query=query)
        except Exception:
            print("it failed first execution")
            time.sleep(5)

        if r_obj.status_code==requests.codes.ok:
            content = r_obj.text
            with open(output_file_path, "w") as f:
                f.write(content)
        else:
            print("it failed (read): {0}".format(p_name))
            with open(error_output_file_path, "w") as f:
                f.write("It failed")
        time.sleep(5)



def main(p_name):
    """
    The main script. For each session, we process NUM_ONE_ITE_URL issue ids and
    wait 10 seconds

    Arguments:
    p_name [string] -- project name
    """

    run(p_name)

if __name__=="__main__":
    for p_name in PROJECT_NAME_LIST:
        main(p_name)

