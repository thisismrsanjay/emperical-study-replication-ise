import os
import requests
import sqlite3
import sys
import time
import json

from Utils import util

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


BASE_URL = "https://issues.apache.org/jira/rest/api/2/issue" # base url
PROJECT_NAME_LIST = ["your project here"]

def init_db(db_path):

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS basic_fields;")
    cur.execute("DROP TABLE IF EXISTS attached_files_info;")
    cur.execute("DROP TABLE IF EXISTS comments;")
    conn.commit()

    cur.execute("CREATE TABLE basic_fields(issue_id TEXT PRIMARY KEY, priority TEXT, created TEXT, updated TEXT, resolutiondate TEXT, description TEXT);")
    cur.execute("CREATE TABLE attached_files_info(issue_id TEXT, idx INTEGER, file_name TEXT, created TEXT, PRIMARY KEY(issue_id, idx));")
    cur.execute("CREATE TABLE comments(issue_id TEXT, idx INTEGER, created TEXT, body TEXT, PRIMARY KEY(issue_id, idx));")
    conn.commit()
    conn.close()


def insert_field_data(db_path, issue_id, con_dict):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
            INSERT INTO basic_fields(issue_id, priority, created, updated, resolutiondate, description)
            VALUES(?,?,?,?,?,?)""", (issue_id, con_dict['priority'], con_dict['created'], con_dict['updated'],
                con_dict['resolutiondate'], con_dict['description']))

    for idx in con_dict['attachments']:
        temp = con_dict['attachments'][idx]
        cur.execute("""
                INSERT INTO attached_files_info(issue_id, idx, file_name, created)
                VALUES(?,?,?,?)""", (issue_id, idx, temp['filename'], temp['created']))

    for idx in con_dict['comments']:
        temp = con_dict['comments'][idx]
        cur.execute("""
                INSERT INTO comments(issue_id, idx, created, body)
                VALUES(?,?,?,?)""", (issue_id, idx, temp['created'], temp['body']))

    conn.commit()
    conn.close()

def get_fields_from_issue(issue_id, issue_data_dict, df):

    issue_data_dict[issue_id] = {}

    issue_data_dict[issue_id]['created'] = df['fields']['created']
    issue_data_dict[issue_id]['updated'] = df['fields']['updated']
    issue_data_dict[issue_id]['resolutiondate'] = df['fields']['resolutiondate']
    if not df['fields']['priority'] is None:
        issue_data_dict[issue_id]['priority'] = df['fields']['priority']['name']
    else:
        issue_data_dict[issue_id]['priority'] = "None"

    issue_data_dict[issue_id]['description'] = df['fields']['description']
    issue_data_dict[issue_id]['summary'] = df['fields']['summary']

    
    # attachment
    issue_data_dict[issue_id]['attachments'] = {}
    for idx, attachment in enumerate(df['fields']['attachment']):
        issue_data_dict[issue_id]['attachments'][idx] = {}
        issue_data_dict[issue_id]['attachments'][idx]['filename'] = attachment['filename']
        issue_data_dict[issue_id]['attachments'][idx]['created'] = attachment['created']


    # comment
    issue_data_dict[issue_id]['comments'] = {}
    for idx, comment in enumerate(df['fields']['comment']['comments']):
        issue_data_dict[issue_id]['comments'][idx] = {}
        issue_data_dict[issue_id]['comments'][idx]['created'] = comment['created']
        issue_data_dict[issue_id]['comments'][idx]['body'] = comment['body']



def extract_issue(session=None, issue_num=None):
    """
    Extract issue content from a target issue id

    Arguments:
    session: [session object] -- session object to a target base url
    issue_num: [string] -- issue id

    Returns:
    content.text: [string] -- output to be stored
    """
    if session==None:
        return "@@@MASA CHECK@@@ No session"
    if issue_num==None:
        return "@@@MASA CHECK@@@ No target URL"

    r_obj = session.get(BASE_URL + "/" + issue_num, timeout=(10.0, 30.0))

    return r_obj


def run(issue_num_list, db_path, retries=3, backoff_factor=1, status_forcelist=(500, 502, 504)):
    issue_data_dict = {}

    with requests.Session() as s:
        output_file_dir = './data_{0}'.format(p_name)
        os.makedirs(output_file_dir)

        retry = Retry(total=retries, read=retries, connect=retries, backoff_factor=backoff_factor, status_forcelist=status_forcelist)
        adapter = HTTPAdapter(max_retries=retry)
        s.mount("https://", adapter)

        for issue_num in issue_num_list:
        #for issue_num in issue_num_list[:5]:
            print("issue num: {0}".format(issue_num))
            error_output_file_path = output_file_dir + "/error_{0}.txt".format(issue_num)

            try:
                r_obj = extract_issue(session=s, issue_num=issue_num)
            except Exception:
                print("it failed (exc): {0}".format(issue_num))
                with open(error_output_file_path, "w") as f:
                    f.write("It failed")
                time.sleep(6)
                continue

            if r_obj.status_code==requests.codes.ok:
                tmp_obj = json.loads(r_obj.text)
                tmp_obj['fields']['assignee'] = "Anonymous"
                tmp_obj['fields']['reporter'] = "Anonymous"
                tmp_obj['fields']['creator'] = "Anonymous"
                for idx, _ in enumerate(tmp_obj['fields']['attachment']):
                    if 'author' in tmp_obj['fields']['attachment'][idx]:
                        tmp_obj['fields']['attachment'][idx]['author'] = "Anonymous"

                for idx, _ in enumerate(tmp_obj['fields']['comment']['comments']):
                    if 'author' in tmp_obj['fields']['comment']['comments'][idx]:
                        tmp_obj['fields']['comment']['comments'][idx]['author'] = "Anonymous"
                
                get_fields_from_issue(issue_num, issue_data_dict, tmp_obj)


            else:
                print("it failed (stat): {0}".format(issue_num))
                with open(error_output_file_path, "w") as f:
                    f.write("It failed")
            time.sleep(6)

    for issue_id in issue_data_dict:
        insert_field_data(db_path, issue_id, issue_data_dict[issue_id])



def main(p_name, db_path):
    """
    The main script. For each session, we process NUM_ONE_ITE_URL issue ids and
    wait 10 seconds

    Arguments:
    p_name [string] -- project name
    """
    issue_num_list = util.load_pickle("./issues_list/{0}_issue_list.pickle".format(p_name))

    run(issue_num_list, db_path)

if __name__=="__main__":
    for p_name in PROJECT_NAME_LIST:
        db_path = "./db/{0}_issue_field_data.db".format(p_name.lower())
        init_db(db_path)

        main(p_name, db_path)
