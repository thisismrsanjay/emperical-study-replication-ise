
import sqlite3
import argparse
import sys

from TS import ntext_similarity
from Utils import util
sys.path.append("./../common")
import git_reader
import issue_db_reader
import common


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--project', '-p', type=str, required=True,
                        help='project name')
    parser.add_argument('--iteration', '-i', type=int, required=True,
                        help='iteration number')
    parser.add_argument('--max_iteration', '-mi', type=int, required=True,
                        help='max iteration number')
    args = parser.parse_args()
    p_name = args.project
    num_iteration = args.iteration
    max_iteration = args.max_iteration

    repodir = "./../../prepare_data/repository/{0}".format(p_name)
    db_path = "./../../prepare_data/extract_issues/db/{0}_issue_field_data.db".format(p_name)

    print(p_name)
    print(num_iteration)
    print(max_iteration)
    issue_id_list = issue_db_reader.read_issue_id_list(db_path)
    len_issue_id_list = len(issue_id_list)
    unit = int(len_issue_id_list/max_iteration)

    if max_iteration==num_iteration:
        print("{0}:".format((num_iteration-1)*unit))
        target_issue_id_list = issue_id_list[(num_iteration-1)*unit:]
    else:
        print("{0}:{1}".format((num_iteration-1)*unit, num_iteration*unit))
        target_issue_id_list = issue_id_list[(num_iteration-1)*unit:num_iteration*unit]


    hash_list = git_reader.get_all_hash_without_merge(repodir)
    dsc_issue_dict = common.extract_description(db_path)
    comment_issue_dict = common.extract_comment(db_path)
    log_message_without_issueid_path = "./../../prepare_data/extract_issues/data_{0}/{1}_log_message_without_issueid.pickle".format(p_name.upper(), p_name)

    ins = ntext_similarity.NtextSimilarity(parallel_iteration=num_iteration)
    issue2hash_dict = ins.run(hash_list, issue_id_list, target_issue_id_list, dsc_issue_dict,
                   comment_issue_dict, log_message_without_issueid_path,
                   "./pickle_{0}".format(p_name))

    util.dump_pickle("./data/{0}_ntext_similarity_costh{1}_ite{2}.pickle".format(p_name, 3, num_iteration), issue2hash_dict)



if __name__=="__main__":

    main()
