import sys
import csv
import pandas as pd
import numpy as np

from Utils import util

import time_restriction


project_name_list = ["project name here"]

BOOTSTRAP_SIZE = 100

def return_issue2hash_dict(p_name, ILA_dict):
    return_dict = {}
    for issue_dir in ILA_dict.keys():

        if issue_dir=="14_1" or issue_dir=="14_2":
            temp_dir = "14"
        else:
            temp_dir = issue_dir

        exp40_ILA_set = set(["7", "9", "11", "14"])
        if temp_dir=="1":
            data_dict = util.load_pickle("./../../RQ1/deleted_data/{0}.pickle".format(ILA_dict[issue_dir]))
        elif temp_dir in exp40_ILA_set:
            #print("{0}, {1}".format(temp_dir, issue_dir))
            data_dict = util.load_pickle("./../../RQ1/{0}/data/{1}.pickle".format(temp_dir, ILA_dict[issue_dir]))
        else:
            print("ERROR")
            sys.exit()

        util.dump_pickle("./data/{0}.pickle".format(ILA_dict[issue_dir]), data_dict)

        TimeRestriction = time_restriction.TimeRestriction(LINK_DATA_PATH="./data/{0}.pickle".format(ILA_dict[issue_dir]), verbose=1)
        issue2hash_dict = TimeRestriction.run(p_name)

        #util.dump_pickle("./data/{0}_with_restriction.pickle".format(ILA_dict[issue_dir]), issue2hash_dict)
        return_dict[issue_dir] = issue2hash_dict

    return return_dict

def compute_diff(p_name, delete_rate, repo_dir, ke_issue2hash_dict, target_issue2hash_dict):
    new_linke = {}
    for issue_id in target_issue2hash_dict.keys():
        if not issue_id in ke_issue2hash_dict:
            new_linke[issue_id] = target_issue2hash_dict[issue_id]
            continue

    print(new_linke)

    tmp_table = []
    sort_idx_list = []
    cnt = 0
    for issue_id in sorted(new_linke.keys()):
        for commit_hash in new_linke[issue_id]:
            row = [p_name]
            row.append("https://issues.apache.org/jira/browse/{0}".format(issue_id))
            row.append("https://github.com/apache/{0}/commit/{1}".format(p_name, commit_hash))

            tmp_table.append(row)

            sort_idx_list.append(int(issue_id.split("-")[-1]))

    TABLE = []
    arg_idx = np.argsort(sort_idx_list)
    for row in np.array(tmp_table)[arg_idx]:
        TABLE.append(row)


    columns = ["Project", "Issue URL", "Commit URL"]
    output = pd.DataFrame(TABLE, columns=columns)
    output.to_csv("./result/{0}_{1}.csv".format(p_name, delete_rate), index=False)

def combine_two_dict(dict_1, dict_2):

    new_dict = {}
    for issue_id in dict_1.keys():
        if not issue_id in dict_2:
            continue

        temp_set = set(dict_1[issue_id]) & set(dict_2[issue_id])

        if len(temp_set)!=0:
            new_dict[issue_id] = temp_set

    return new_dict


def main():
    for p_name in project_name_list:
        repo_dir = "./../../prepare_data/repository/{0}".format(p_name)
        print(p_name)

        ILA_dict = {"1": "{0}_keyword_extraction_0_0".format(p_name)}
        ke_issue2hash_dict = return_issue2hash_dict(p_name, ILA_dict)["1"]

        deleted_rate_list = [0]
        for delete_rate in deleted_rate_list:

            target_issue2hash_dict = {}
            for bootstrap_idx in range(BOOTSTRAP_SIZE):
            #for bootstrap_idx in range(2):
                #print("bootstrap idx: {0}".format(bootstrap_idx))

                ILA_dict = {"14_1": "{0}_RF_{1}_model_bi{2}".format(p_name, delete_rate, bootstrap_idx)}

                return_dict = return_issue2hash_dict(p_name, ILA_dict)
                temp_target_issue2hash_dict = return_dict["14_1"]

                if bootstrap_idx==0:
                    for issue_id in temp_target_issue2hash_dict.keys():
                        target_issue2hash_dict[issue_id] = set(temp_target_issue2hash_dict[issue_id])

                target_issue2hash_dict = combine_two_dict(target_issue2hash_dict, temp_target_issue2hash_dict)

            #print(target_issue2hash_dict)

            compute_diff(p_name, delete_rate, repo_dir, ke_issue2hash_dict, target_issue2hash_dict)
            #sys.exit()

if __name__=="__main__":

    main()
