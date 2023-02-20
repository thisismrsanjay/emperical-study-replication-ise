
import argparse
import sys

from Utils import util
from MT import nsd_similarity

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



    #for cosine_sim_threshold in range(1,4):
    for cosine_sim_threshold in [1]:
    #for cosine_sim_threshold in [1, 2, 3, 8, 9, 95]:
        print("cosine sim: {0}".format(cosine_sim_threshold/10))
        nsd_similarity_obj = nsd_similarity.NSDSimilarity(repodir=repodir, THRESHOLD_COSINE_SIM=cosine_sim_threshold/10, verbose=1, parallel_iteration=num_iteration, output_dir_cosine_sim="./pickle_{0}".format(p_name))
        issue2hash_dict = nsd_similarity_obj.run(hash_list, issue_id_list,
                                  target_issue_id_list,
                                  dsc_issue_dict, comment_issue_dict)

        util.dump_pickle("./data/{0}_nsd_similarity_costh{1}_ite{2}.pickle".format(p_name, cosine_sim_threshold, num_iteration), issue2hash_dict)



if __name__=="__main__":

    main()
