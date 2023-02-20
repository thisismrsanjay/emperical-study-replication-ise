import re
import subprocess

from Utils import util

project_name_list = ["your project here (lower case)"]
project_name_dict_for_issue_display = {"avro": "AVRO",
                                       "zookeeper": "ZOOKEEPER", "tez": "TEZ",
                                       "chukwa": "CHUKWA", "knox": "KNOX"}

def match_basic_regexp(text, regexp):
    match = re.match(regexp, text)
    info = None
    if match:
        info = match.group(1)
    return info

def parse_log(log, p_name):
    re_commit = r'^commit ([0-9a-f]{5,40})$'
    re_msg = r'^\s+(.*)$'
    re_issue_id = r'{0}-[0-9]*'.format(project_name_dict_for_issue_display[p_name])

    
    return_dict = {}
    return_dict_without_issueid = {}
    cur_commit_hash = None
    for row in log.splitlines():
        commit_hash = match_basic_regexp(row, re_commit)
        if commit_hash:
            cur_commit_hash = commit_hash
            if not cur_commit_hash in return_dict:
                return_dict[cur_commit_hash] = ""
                return_dict_without_issueid[cur_commit_hash] = ""

        match = re.match(re_msg, row)
        if match:
            return_dict[cur_commit_hash] += match.group(0) + "\n"
            return_dict_without_issueid[cur_commit_hash] += re.sub(re_issue_id, "ISSUE_ID", match.group(0) + "\n")


    return return_dict, return_dict_without_issueid

def git_log_all(dirname):
    log = subprocess.check_output(
            ['git', '-C', '{}'.format(dirname), 'log', '--all', '--pretty=fuller'],
            universal_newlines=True
            )
    return log

def process_log(p_name):
    log = git_log_all("./../repository/{0}".format(p_name))
    #print(log)

    parsed_log_dict, parsed_log_dict_without_issueid = parse_log(log, p_name)
    util.dump_pickle("./data_{0}/{1}_log_message.pickle".format(project_name_dict_for_issue_display[p_name], p_name), parsed_log_dict)
    util.dump_pickle("./data_{0}/{1}_log_message_without_issueid.pickle".format(project_name_dict_for_issue_display[p_name], p_name), parsed_log_dict_without_issueid)

def main():
    for p_name in project_name_list:
        process_log(p_name)



if __name__=="__main__":
    main()
