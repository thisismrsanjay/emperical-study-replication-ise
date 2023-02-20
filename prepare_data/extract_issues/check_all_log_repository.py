import re
import subprocess
from datetime import datetime
from collections import Counter

import sys
from Utils import util

project_name_list = ["your project here (lower case)"]
project_name_dict_for_issue_display = {"avro": "AVRO",
                                       "zookeeper": "ZOOKEEPER", "tez": "TEZ",
                                       "chukwa": "CHUKWA", "knox": "KNOX"}

def initialize_dict(dic):
    dic['issue_id'] = set()
    dic['author_date'] = None
    dic['commit_date'] = None

def match_basic_regexp(text, regexp):
    match = re.match(regexp, text)
    info = None
    if match:
        info = match.group(1)
    return info

def match_issue_regexp(text, regexp_msg, regexp_issue):
    match_msg = re.match(regexp_msg, text)
    issue_ids=[]
    if match_msg:
        issue_ids = re.findall(regexp_issue, match_msg.group(1))
        #if len(issue_ids)==0:
        #    issue_ids=[]

    return issue_ids

def extract_datetime_from_string(target):
    return datetime.strptime(target, "%a %b %d %H:%M:%S %Y %z")

def insert_basicdate_info(text, regexp, dic, key):
    data = match_basic_regexp(text, regexp)
    if data:
        dic[key] = extract_datetime_from_string(data)

def parse_log(log, p_name):
    """
    Returns:
    return_dict [dict<commit hash, dict<key name, data>>] -- key name list: author_date, commit_date, issue_id
    """
    re_commit = r'^commit ([0-9a-f]{5,40})$'
    re_authordate = r'^AuthorDate:\s+(.*)$'
    re_commitdate = r'^CommitDate:\s+(.*)$'
    re_msg = r'^\s+(.*)$'
    re_issue_id = r'{0}-[0-9]*'.format(project_name_dict_for_issue_display[p_name])

    return_dict = {}
    cur_commit_hash = None
    for row in log.splitlines():
        #for regexp in re_list:
        #    info = match_basic_regexp(row, regexp)
        commit_hash = match_basic_regexp(row, re_commit)
        if commit_hash:
            cur_commit_hash = commit_hash
            if not commit_hash in return_dict:
                return_dict[commit_hash] = {}
                initialize_dict(return_dict[commit_hash])

        insert_basicdate_info(row, re_authordate, return_dict[cur_commit_hash], 'author_date')
        insert_basicdate_info(row, re_commitdate, return_dict[cur_commit_hash], 'commit_date')

        issue_ids = match_issue_regexp(row, re_msg, re_issue_id)
        for issue_id in issue_ids:
            return_dict[cur_commit_hash]['issue_id'].add(issue_id)

    return return_dict


def count_issue(parsed_log_dict, p_name):
    issue_id_list = []
    for commit_hash in parsed_log_dict.keys():
        for issue_id in parsed_log_dict[commit_hash]['issue_id']:
            issue_id_list.append(issue_id)

    issue_id_set = set(issue_id_list)
    print("number of issue: {0}".format(len(issue_id_list)))
    print("number of unique issue: {0}".format(len(issue_id_set)))
    #print("Count issue:")
    #cnt = Counter(issue_id_list)
    #print(cnt)

    all_target_issue_set = set(util.load_pickle("./issues_list/{0}_issue_list.pickle".format(project_name_dict_for_issue_display[p_name])))
    print("number of all target issues: {0}".format(len(all_target_issue_set)))
    diff_all2log = len(all_target_issue_set - issue_id_set)
    print("proportion of detected issues by log message (all - log): {0}({1:,}/{2:,})".format(round(1-(diff_all2log/len(all_target_issue_set)), 3), len(all_target_issue_set) - diff_all2log, len(all_target_issue_set)))
            
def git_log_all(dirname):
    log = subprocess.check_output(
            ['git', '-C', '{}'.format(dirname), 'log', '--all', '--pretty=fuller'],
            universal_newlines=True
            )
    return log


def process_log(p_name):
    log = git_log_all("./../repository/{0}".format(p_name))
    #print(log)

    parsed_log_dict = parse_log(log, p_name)
    util.dump_pickle("./data_{0}/{1}_log_message_info.pickle".format(project_name_dict_for_issue_display[p_name], p_name), parsed_log_dict)
    count_issue(parsed_log_dict, p_name)

def main():
    for p_name in project_name_list:
        process_log(p_name)



if __name__=="__main__":
    main()
