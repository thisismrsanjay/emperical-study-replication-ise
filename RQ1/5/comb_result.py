import sys
import numpy as np

from Utils import util

project_name_list = ["project name here"]
max_iteration = 25


def combine_dict(target_dict, temp_dict):

    for issue_id in temp_dict:

        if issue_id in target_dict:
            print("SOMETHING BUT THING HAPPEND")
            sys.exit()

        target_dict[issue_id] = temp_dict[issue_id]


def main():
    for p_name in project_name_list:

        #for cosine_sim_threshold in range(1, 10):
        for cosine_sim_threshold in [3]:

            print("cosine sim: {0}".format(cosine_sim_threshold/10))

            issue2hash_dict = {}
            count_num_issue = 0
            for num_ite in range(1, max_iteration+1):

                temp_dict = util.load_pickle("./data/{0}_ntext_similarity_costh{1}_ite{2}.pickle".format(p_name, cosine_sim_threshold, num_ite))
                count_num_issue += len(temp_dict)

                combine_dict(issue2hash_dict, temp_dict)

            print("# linked issues (combine dict): {0:,}, # linked issues (sum of each dict): {1:,}".format(len(issue2hash_dict), count_num_issue))
            assert len(issue2hash_dict)==count_num_issue, "different length, len result: {0:,}, len counter: {1:,}".format(len(issue2hash_dict), count_num_issue)

            util.dump_pickle("./data/{0}_ntext_similarity_costh{1}.pickle".format(p_name, cosine_sim_threshold), issue2hash_dict)





if __name__=="__main__":

    main()
