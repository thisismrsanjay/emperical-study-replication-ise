import json
import sys

from Utils import util

PROJECT_NAME_LIST = ["AVRO", "TEZ", "ZOOKEEPER"]
NUM_ONE_ITE_ISSUES = 50 # number of processed issues at one session

BASE_DIR = "./../../prepare_data/extract_issues"
OUT_DIR = "./data"

def extract_issue_ids_types(p_name, num_total_issues):

    print("num total issues: {0}".format(num_total_issues))
    num_ite = int(num_total_issues/NUM_ONE_ITE_ISSUES) + 1
    issue_id_type_dict = {}
    issue_id_status_dict = {}
    for ite in range(num_ite):

        with open(BASE_DIR + "/issues_list/{0}_{1}_issue_list.txt".format(p_name, ite), 'r', encoding='utf-8') as f:
            temp_data = json.load(f)

        for issue_data in temp_data['issues']:

            if issue_data['key'] in issue_id_type_dict:
                print("DUPLICATED ERROR")
                sys.exit()
            issue_id_type_dict[issue_data['key']] = issue_data['fields']['issuetype']["name"]
            issue_id_status_dict[issue_data['key']] = issue_data['fields']['status']["name"]
    
    print("Number of extracted issues: {0}".format(len(issue_id_type_dict)))
    util.dump_pickle(OUT_DIR + "/{0}_issue_id_type.pickle".format(p_name), issue_id_type_dict)
    util.dump_pickle(OUT_DIR + "/{0}_issue_id_status.pickle".format(p_name), issue_id_status_dict)

def main(p_name):

    with open(BASE_DIR + "/issues_list/{0}_total.txt".format(p_name), 'r', encoding='utf-8') as f:
        temp_data = json.load(f)
    num_total_issues = int(temp_data['total'])

    extract_issue_ids_types(p_name, num_total_issues)

if __name__=="__main__":
    for p_name in PROJECT_NAME_LIST:
        main(p_name)

