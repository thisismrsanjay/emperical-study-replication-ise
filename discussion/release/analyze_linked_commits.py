import sys
import re
from datetime import datetime

project_name_list = ["avro", "tez", "zookeeper"]

project_name_dict_for_issue_display = {"avro": "AVRO", "zookeeper": "ZOOKEEPER", "tez": "TEZ"}

def initialize_dict(dic):
    dic['issue_id'] = set()
    dic['PR_id'] = set()
    dic['fix_term'] = False
    dic['release_term'] = False
    dic['add_term'] = False
    dic['author_date'] = None
    dic['commit_date'] = None

    dic['author'] = {'name': None, 'email': None}
    dic['committer'] = {'name': None, 'email': None}

def match_basic_regexp(text, regexp):
    match = re.match(regexp, text)
    info = None
    if match:
        info = match.group(1)
    return info

def extract_datetime_from_string(target):
    return datetime.strptime(target, "%a %b %d %H:%M:%S %Y %z")

def insert_basicdate_info(text, regexp, dic, key):
    data = match_basic_regexp(text, regexp)
    if data:
        dic[key] = extract_datetime_from_string(data)

def extract_author_from_string(target):
    re_str = "^(.*) <(.*)>$"
    author_info = re.search(re_str, target)
    if author_info:
        return author_info.group(1), author_info.group(2)
    else:
        return None, None

def insert_basicauthor_info(text, regexp, dic, key):
    data = match_basic_regexp(text, regexp)
    if data:
        name, email = extract_author_from_string(data)
        dic[key]['name'] = name
        dic[key]['email'] = email

def match_regexp(text, regexp_msg, regexp_target):
    match_msg = re.match(regexp_msg, text)
    target_list =[]
    if match_msg:
        target_list = re.findall(regexp_target, match_msg.group(1))
        #if len(issue_ids)==0:
        #    issue_ids=[]

    return target_list


def parse_log(log, p_name):
    """
    Returns:
    return_dict [dict<commit hash, dict<key name, data>>] -- key name list: author_date, commit_date, author, committer, issue_id
    """
    re_commit = r'^commit ([0-9a-f]{5,40})$'
    re_commitauthor = r'^Commit:\s+(.*)$'
    re_authordate = r'^AuthorDate:\s+(.*)$'
    re_commitdate = r'^CommitDate:\s+(.*)$'
    re_msg = r'^\s+(.*)$'
    re_issue_id = r'{0}-[0-9]+'.format(project_name_dict_for_issue_display[p_name])
    re_PR_id = r'#[0-9]+'
    re_fix = r'(fix|error)'
    re_release = "(Prepare|Preparing)" # preparing for relase
    re_add = "(upgrade|update|add|merge)"

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

        insert_basicauthor_info(row, re_commitauthor, return_dict[cur_commit_hash], 'committer')

        issue_ids = match_regexp(row, re_msg, re_issue_id)
        for issue_id in issue_ids:
            return_dict[cur_commit_hash]['issue_id'].add(issue_id)

        PR_ids = match_regexp(row, re_msg, re_PR_id)
        for PR_id in PR_ids:
            return_dict[cur_commit_hash]['PR_id'].add(PR_id)

        fix_terms = match_regexp(row, re_msg, re_fix)
        if len(fix_terms)!=0:
            return_dict[cur_commit_hash]['fix_term'] = True

        release_terms = match_regexp(row, re_msg, re_release)
        if len(release_terms)!=0:
            return_dict[cur_commit_hash]['release_term'] = True

        add_terms = match_regexp(row, re_msg, re_add)
        if len(add_terms)!=0:
            return_dict[cur_commit_hash]['add_term'] = True

    return return_dict

