import sys

from Utils import util

project_name_list = ["project name here"]
ml_model_list = ["RF", "SVM"]
#ml_model_list = ["RF"]
max_iteration = 10
delete_rate_list=[0, 10, 20, 30, 40, 50]
bootstrap_sample_iteration=100


def main():
    for bootstrap_idx in range(bootstrap_sample_iteration):
        for p_name in project_name_list:

            for m_name in ml_model_list:

                for delete_rate in delete_rate_list:

                    issue2hash_dict = {}
                    for num_ite in range(max_iteration):
                        print("Number of iteration: {0}".format(num_ite))
                        temp_dict = util.load_pickle("data/{0}_{1}_{2}_model_bi{3}_{4}.pickle".format(p_name, m_name, delete_rate, bootstrap_idx, num_ite))
                        for issue_id in temp_dict.keys():

                            if not issue_id in issue2hash_dict:
                                issue2hash_dict[issue_id] = []

                            for commit_hash in temp_dict[issue_id]:
                                issue2hash_dict[issue_id].append(commit_hash)



                    util.dump_pickle("./data/{0}_{1}_{2}_model_bi{3}.pickle".format(p_name, m_name, delete_rate, bootstrap_idx), issue2hash_dict)



if __name__=="__main__":

    main()
