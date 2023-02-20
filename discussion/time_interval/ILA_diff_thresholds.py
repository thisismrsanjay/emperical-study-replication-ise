import sys
from collections import Counter
import pytz


from Utils import util

sys.path.append("./../../RQ1/random_delete")
import time_restriction

project_name_list = ["project name here"]
deleted_rate_list = [10, 20, 30, 40, 50]


def add_restrictions(p_name, ILA_num, ILA_dict, diff_th_approach):

    issue_dir = diff_th_approach

    # issue2hash_dict [dict<issue id, list<commit hash>>] -- issue id to list of commit hashes. these commit hashes include issue id in their log message
    data_dict = util.load_pickle("./../../RQ1/{0}/data/{1}.pickle".format(ILA_num[diff_th_approach], ILA_dict[issue_dir]))
    util.dump_pickle("./data_th/{0}.pickle".format(ILA_dict[issue_dir]), data_dict)

    TimeRestriction = time_restriction.TimeRestriction(LINK_DATA_PATH="./data_th/{0}.pickle".format(ILA_dict[issue_dir]), verbose=1)
    issue2hash_dict = TimeRestriction.run(p_name)
    util.dump_pickle("./data_th/{0}_with_restriction.pickle".format(ILA_dict[issue_dir]), issue2hash_dict)


def main(diff_th_approach, cosine_th):
    for p_name in project_name_list:
        print("===========")
        print(p_name)

        ILA_dict = {"ntext": "{0}_ntext_similarity_costh{1}".format(p_name, cosine_th),
                "comment": "{0}_comment_costh{1}".format(p_name, cosine_th),
                "time": "{0}_time_filtering_min_af{1}".format(p_name, cosine_th)}
        ILA_num = {"ntext": "5",
                "comment": "8",
                "time": "3"}


        add_restrictions(p_name, ILA_num, ILA_dict, diff_th_approach)


if __name__=="__main__":

    diff_th_approach_list = ["time"]
    for diff_th_approach in diff_th_approach_list:
        for cosine_th in [5, 10, 30, 60, 120]:
            main(diff_th_approach, cosine_th)
