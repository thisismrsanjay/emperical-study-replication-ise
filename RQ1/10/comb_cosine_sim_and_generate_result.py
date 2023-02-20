import sys
import numpy as np

from Utils import util

project_name_list = ["project name here"]
max_iteration = 25

def main():
    for p_name in project_name_list:

        count_num_issue = 0
        for num_ite in range(1, max_iteration+1):
            print("Number of iteration: {0}".format(num_ite))
            temp_dict = util.load_pickle("./pickle_{0}/cosine_similarity_dict_ite{1}.pickle".format(p_name, num_ite))
            count_num_issue += len(temp_dict)
            for cosine_sim in range(2, 10):
                THRESHOLD_COSINE_SIM = cosine_sim/10
                print("cosine sim: {0}".format(THRESHOLD_COSINE_SIM))

                issue2hash_dict = {}
                for idx_issue_id, issue_id in enumerate(temp_dict.keys()):
                    temp_list = []
                    for commit_hash in temp_dict[issue_id].keys():
                        if temp_dict[issue_id][commit_hash] >= THRESHOLD_COSINE_SIM:
                            temp_list.append(commit_hash)

                    if len(temp_list)>0:
                        issue2hash_dict[issue_id] = temp_list

                util.dump_pickle("./data/{0}_nsd_similarity_costh{1}_ite{2}.pickle".format(p_name, cosine_sim, num_ite), issue2hash_dict)

        print("number of processed issues: {0}".format(count_num_issue))





if __name__=="__main__":

    main()
