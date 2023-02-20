import sys
from collections import Counter

import time_restriction

from Utils import util


project_name_list = ["project name here"]
deleted_rate_list = [0, 10, 20, 30, 40, 50]

def _compare_org_update(keyword_extraction_dict, issue2hash_dict, TimeRestriction):
    print("===")
    print("num issue ids -- keyword only: {0:,}, with restriction: {1:,}, diff: {2:,} ({3}%)".format(len(keyword_extraction_dict), len(issue2hash_dict), len(keyword_extraction_dict) - len(issue2hash_dict), 100*round((len(keyword_extraction_dict)-len(issue2hash_dict))/len(keyword_extraction_dict), 3)))

    keyword_commit_set = set()
    restriction_commit_set = set()
    for issue_id in keyword_extraction_dict.keys():
        keyword_commit_set = keyword_commit_set | set(keyword_extraction_dict[issue_id])

    for issue_id in issue2hash_dict.keys():
        restriction_commit_set = restriction_commit_set | set(issue2hash_dict[issue_id])

    print("num commit hashes -- keyword only: {0:,}, with restriction: {1:,}, diff: {2:,} ({3}%)".format(len(keyword_commit_set), len(restriction_commit_set), len(keyword_commit_set) - len(restriction_commit_set), 100*round((len(keyword_commit_set)-len(restriction_commit_set))/len(keyword_commit_set), 3)))


def main():
    for p_name in project_name_list:

        print("============")
        print(p_name)
        print("============")
        in_f_path = "./../1/data/{0}_keyword_extraction.pickle".format(p_name)
        out_f_path = "./../1/data/{0}_keyword_with_restriction.pickle".format(p_name)
        # issue2hash_dict [dict<issue id, list<commit hash>>] -- issue id to list of commit hashes. these commit hashes include issue id in their log message
        keyword_extraction_dict = util.load_pickle(in_f_path)

        TimeRestriction = time_restriction.TimeRestriction(LINK_DATA_PATH=in_f_path, verbose=1)
        issue2hash_dict = TimeRestriction.run(p_name)
        util.dump_pickle(out_f_path, issue2hash_dict)

        _compare_org_update(keyword_extraction_dict, issue2hash_dict, TimeRestriction)

        print("")

        for bootstrap_sample_idx in range(100):
            for delete_rate in deleted_rate_list:
                in_f_path = "./../deleted_data/{0}_keyword_extraction_{1}_{2}.pickle".format(p_name, delete_rate, bootstrap_sample_idx)
                out_f_path = "./../deleted_data/{0}_keyword_with_restriction_{1}_{2}.pickle".format(p_name, delete_rate, bootstrap_sample_idx)
                # issue2hash_dict [dict<issue id, list<commit hash>>] -- issue id to list of commit hashes. these commit hashes include issue id in their log message
                keyword_extraction_dict = util.load_pickle(in_f_path)

                TimeRestriction = time_restriction.TimeRestriction(LINK_DATA_PATH=in_f_path, verbose=1)
                issue2hash_dict = TimeRestriction.run(p_name)
                util.dump_pickle(out_f_path, issue2hash_dict)

                _compare_org_update(keyword_extraction_dict, issue2hash_dict, TimeRestriction)

        print("============")
        print("")
if __name__=="__main__":

    main()
