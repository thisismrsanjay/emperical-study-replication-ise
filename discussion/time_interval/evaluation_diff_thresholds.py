import sys

from Utils import util

sys.path.append("./../../RQ1/evaluation")
import evaluation_with_restriction

project_name_list = ["project name here"]
deleted_rate_list = [10, 20, 30, 40, 50]

evaluation_measure_list = ['acc', 'precision', 'recall', 'tp', 'fp', 'fn', 'deleted_tp', 'deleted_fn', 'target_sum_commit', 'num_sum_commit']

BOOTSTRAP_SIZE = 100


def evaluate_ILA(p_name, delete_rate, bootstrap_idx, result_dict, diff_th_approach, cosine_th):

    BASE_DIR = "./../../RQ1"
    ground_truth_dict = util.load_pickle(BASE_DIR +
                        "/evaluation/data/{0}_keyword_extraction_0_{1}_with_restriction.pickle".format(p_name, bootstrap_idx))
    deleted_ground_truth_dict = util.load_pickle(BASE_DIR +
                        "/evaluation/data/{0}_keyword_extraction_{1}_{2}_with_restriction.pickle".format(p_name, delete_rate, bootstrap_idx))

    deleted_issue2hash_dict = evaluation_with_restriction.take_diff_issue2hash_dict(ground_truth_dict, deleted_ground_truth_dict)

    # test script
    #_test(deleted_issue2hash_dict, delete_rate)
    #return 0


    ILA_dict = {"time": "{0}_time_filtering_min_af{1}_with_restriction".format(p_name, cosine_th)}

        
    #print(ILA_dict[diff_th_approach])

    target_dict = util.load_pickle("./data_th/{0}.pickle".format(ILA_dict[diff_th_approach]))

    evaluation_with_restriction.evaluate(ground_truth_dict, target_dict, diff_th_approach, p_name, delete_rate, bootstrap_idx, result_dict)

    #print("-------")
    #print("for deleted data")
    evaluation_with_restriction.evaluate_deleted(deleted_issue2hash_dict, target_dict, p_name, delete_rate, bootstrap_idx, diff_th_approach, result_dict)

    #print("===")


def initialize_table_dict():
    return_dict = {}
    for p_name in project_name_list:
        return_dict[p_name] = {}
        for delete_rate in deleted_rate_list:
            return_dict[p_name][delete_rate] = {}

            for bootstrap_idx in range(BOOTSTRAP_SIZE):
                return_dict[p_name][delete_rate][bootstrap_idx] = {}

                for evaluation_measure in evaluation_measure_list:
                    return_dict[p_name][delete_rate][bootstrap_idx][evaluation_measure] = {}

    return return_dict


def main(diff_th_approach, cosine_th):
    result_dict = initialize_table_dict()

    for p_name in project_name_list:
        print("================")
        print(p_name)
        print("================")

        for delete_rate in deleted_rate_list:
            print("-------")
            print("deleted rate: {0}".format(delete_rate))

            for bootstrap_idx in range(BOOTSTRAP_SIZE):

                evaluate_ILA(p_name, delete_rate, bootstrap_idx, result_dict, diff_th_approach, cosine_th)

    print("")

    util.dump_pickle("./result_th/evaluation_with_restriction_{0}_{1}.pickle".format(diff_th_approach, cosine_th), result_dict)

if __name__=="__main__":

    diff_th_approach_list = ["time"]
    for diff_th_approach in diff_th_approach_list:
        for cosine_th in [5, 10, 30, 60, 120]:
            main(diff_th_approach, cosine_th)

