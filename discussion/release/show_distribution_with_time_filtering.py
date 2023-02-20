import json
import sys
import pandas as pd

from Utils import util

sys.path.append("./../../RQ1/common")
import git_reader

import analyze_linked_commits

PROJECT_NAME_LIST = ["AVRO", "TEZ", "ZOOKEEPER"]

RELEASE_DICT = {"AVRO": {2009: [4, 7, 9, 10], 
    2010: [2, 3, 6, 9, 10], 2011: [3, 5, 8, 9, 11],
    2012: [2, 3, 6, 7, 9, 12], 2013: [2, 8],
    2014: [1, 7], 2016: [1, 5], 2017: [5],
    2019: [5, 9], 2020: [2]
    },
    "TEZ": {2014: [9, 10, 11, 12],
        2015: [1, 5, 6, 8, 9, 10], 2016: [1, 4, 5, 7],
        2017: [3, 7], 2018: [1], 2019: [3]
        },
    "ZOOKEEPER": {2008: [10, 12], 2009: [2, 3, 7, 9, 12],
        2010: [3, 5, 11], 2011: [2, 11, 12],
        2012: [2, 3, 4, 9, 11], 2014: [3, 8], 2015: [4],
        2016: [2, 7, 9], 2017: [3, 4, 11], 2018: [5, 7],
        2019: [4, 5, 10], 2020: [2, 3]
        }
    }

IN_DIR = "./data"

def write_csv(p_name, data_dict, column_index_set):

    min_year = min(data_dict.keys())
    min_month = min(data_dict[min_year].keys())
    max_year = max(data_dict.keys())
    max_month = max(data_dict[max_year].keys())

    print("min: {0}, {1}".format(min_year, min_month))
    print("max: {0}, {1}".format(max_year, max_month))

    TABLE = []
    column_index = sorted(list(column_index_set))
    column_index.append("date")

    for tmp_year in range(min_year, max_year+1):
        if tmp_year == min_year:
            start_month = min_month 
            end_month = 12
        elif tmp_year == max_year:
            start_month = 1
            end_month = max_month
        else:
            start_month = 1
            end_month = 12

        for tmp_month in range(start_month, end_month+1):
            #print("year {0}, month {1}".format(tmp_year, tmp_month))

            row = []
            if not tmp_month in data_dict[tmp_year]:
                for column in column_index:
                    if column=="date":
                        row.append("{0}-{1}".format(tmp_year, tmp_month))
                    else:
                        row.append(0)

            else:
                for column in column_index:
                    if column=="date":
                        row.append("{0}-{1}".format(tmp_year, tmp_month))
                    elif not column in data_dict[tmp_year][tmp_month]:
                        row.append(0)
                    else:
                        row.append(data_dict[tmp_year][tmp_month][column])

                if (data_dict[tmp_year][tmp_month]['tp']+data_dict[tmp_year][tmp_month]['fp'])==0:
                    row.append(0)
                else:
                    row.append(data_dict[tmp_year][tmp_month]['tp']/(data_dict[tmp_year][tmp_month]['tp']+data_dict[tmp_year][tmp_month]['fp']))

                if (data_dict[tmp_year][tmp_month]['tp']+data_dict[tmp_year][tmp_month]['fn'])==0:
                    row.append(0)
                else:
                    row.append(data_dict[tmp_year][tmp_month]['tp']/(data_dict[tmp_year][tmp_month]['tp']+data_dict[tmp_year][tmp_month]['fn']))
                #if data_dict[tmp_year][tmp_month]['denominator']==0:
                #    row.append(1)
                #else:
                #    row.append(data_dict[tmp_year][tmp_month]['numerator']/data_dict[tmp_year][tmp_month]['denominator'])

            TABLE.append(row)

    column_index.append("Precision")
    column_index.append("Recall")
    #print(column_index)
    #print(TABLE)
    TABLE = pd.DataFrame(TABLE,columns=column_index)
    TABLE.to_csv(path_or_buf='./tables/{0}_dist_with_time_filtering.csv'.format(p_name),index=False, sep=",")


def reverse_issue_hash(issue2hash_dict):

    hash2issue_dict = {}
    for issue_id in issue2hash_dict.keys():

        for commit_hash in issue2hash_dict[issue_id]:

            if not commit_hash in hash2issue_dict:
                hash2issue_dict[commit_hash] = set()

            hash2issue_dict[commit_hash].add(issue_id)

    return hash2issue_dict

def extract_hash2issue_dict(p_name):

    issue2hash_dict_key = util.load_pickle("./../../RQ1/evaluation/data/{0}_keyword_extraction_0_0_with_restriction.pickle".format(p_name.lower()))
    issue2hash_dict_time = util.load_pickle("./../../RQ1/evaluation/data/{0}_time_filtering_min_af10_with_restriction.pickle".format(p_name.lower()))

    hash2issue_dict_key = reverse_issue_hash(issue2hash_dict_key)
    hash2issue_dict_time = reverse_issue_hash(issue2hash_dict_time)

    return hash2issue_dict_key, hash2issue_dict_time

def make_csv(p_name):

    repodir = "./../../prepare_data/repository/{0}".format(p_name.lower())
    issue_id_type_dict = util.load_pickle(IN_DIR + "/{0}_issue_id_type.pickle".format(p_name))

    log = git_reader.git_log_all_without_merge(repodir)
    parsed_log_dict = analyze_linked_commits.parse_log(log, p_name.lower())

    pickle_path = "./../../prepare_data/extract_issues/data_{0}/{1}_log_message_info.pickle".format(p_name, p_name.lower())
    date_repo_dict = util.load_pickle(pickle_path) # 



    hash2issue_dict_key, hash2issue_dict_time = extract_hash2issue_dict(p_name)

    # data_dict [dict<year, dict<month, dict<index, value>>>] -- index = [num_commit, Bug, Improve, etc]
    data_dict = {}
    column_index_set = set(['num_commit'])

    for commit_hash in parsed_log_dict.keys():
        #print("===")
        #print("hash: {0}, commit date: {1}".format(commit_hash, date_repo_dict[commit_hash]['commit_date']))

        tmp_year = date_repo_dict[commit_hash]['commit_date'].year
        tmp_month = date_repo_dict[commit_hash]['commit_date'].month

        if not tmp_year in data_dict:
            data_dict[tmp_year] = {}

        if not tmp_month in data_dict[tmp_year]:
            data_dict[tmp_year][tmp_month] = {'num_commit': 0, 'tp': 0, 'fp': 0, 'fn': 0}

        data_dict[tmp_year][tmp_month]['num_commit'] += 1

        for issue_id in parsed_log_dict[commit_hash]["issue_id"]:
            if not issue_id in issue_id_type_dict:
                continue
            #print("issue id: {0}, type: {1}".format(issue_id, issue_id_type_dict[issue_id]))

            tmp_issue_type = issue_id_type_dict[issue_id]
            column_index_set.add(tmp_issue_type)

            if not tmp_issue_type in data_dict[tmp_year][tmp_month]:
                data_dict[tmp_year][tmp_month][tmp_issue_type] = 0

            data_dict[tmp_year][tmp_month][tmp_issue_type] += 1

        # for accuracy of time filtering
        tmp_key = set()
        tmp_time = set()
        try:
            tmp_key = hash2issue_dict_key[commit_hash]
        except KeyError:
            tmp_key = set([])

        try:
            tmp_time = hash2issue_dict_time[commit_hash]
        except KeyError:
            tmp_time = set([])

        tmp_set = tmp_key & tmp_time

        data_dict[tmp_year][tmp_month]['tp'] += len(tmp_set)
        data_dict[tmp_year][tmp_month]['fp'] += len(tmp_time - tmp_set)
        data_dict[tmp_year][tmp_month]['fn'] += len(tmp_key - tmp_set)


    write_csv(p_name, data_dict, column_index_set)


def main(p_name):
    print("{0}".format(p_name))

    make_csv(p_name)


if __name__=="__main__":
    for p_name in PROJECT_NAME_LIST:
        main(p_name)


