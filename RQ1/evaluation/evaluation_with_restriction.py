import sys

from Utils import util

project_name_list = ["project name here"]
deleted_rate_list = [10, 20, 30, 40, 50]

evaluation_measure_list = ['acc', 'precision', 'recall', 'tp', 'fp', 'fn', 'deleted_tp', 'deleted_fn', 'target_sum_commit', 'num_sum_commit']

BOOTSTRAP_SIZE = 100
TIME_FILTERING_MIN = 10
NTEXT_TH = 3
WORD_ASSOC_TH = 5
COMMENT_COS_TH = 4
NSD_SIM_COS_TH = 2

def evaluate(ground_truth_dict, target_dict, issue_dir, p_name, delete_rate, bootstrap_idx, result_dict):
    num_sum_commit = 0
    target_sum_commit = 0
    fp = 0
    tp = 0
    fn = 0

    for issue_id in ground_truth_dict:
        num_sum_commit += len(ground_truth_dict[issue_id])
        if not issue_id in target_dict:
            #num_sum_commit += len(ground_truth_dict[issue_id])
            fn += len(ground_truth_dict[issue_id])
            continue

        temp_set = set(target_dict[issue_id]) & set(ground_truth_dict[issue_id])

        #num_sum_commit += len(temp_set)
        target_sum_commit += len(temp_set)
        tp += len(temp_set)
        fp += len(set(target_dict[issue_id]) - temp_set)
        fn += len(set(ground_truth_dict[issue_id]) - temp_set)

    for issue_id in target_dict:
        if issue_id in ground_truth_dict:
            continue

        fp += len(target_dict[issue_id])


    if (tp+fp)==0:
        result_dict[p_name][delete_rate][bootstrap_idx]['precision'][issue_dir] = 0
    else:
        result_dict[p_name][delete_rate][bootstrap_idx]['precision'][issue_dir] = tp/(tp+fp)
    if (tp+fn)==0:
        result_dict[p_name][delete_rate][bootstrap_idx]['recall'][issue_dir] = 0
    else:
        result_dict[p_name][delete_rate][bootstrap_idx]['recall'][issue_dir] = tp/(tp+fn)

    result_dict[p_name][delete_rate][bootstrap_idx]['acc'][issue_dir] = target_sum_commit/num_sum_commit
    result_dict[p_name][delete_rate][bootstrap_idx]['tp'][issue_dir] = tp
    result_dict[p_name][delete_rate][bootstrap_idx]['fp'][issue_dir] = fp
    result_dict[p_name][delete_rate][bootstrap_idx]['fn'][issue_dir] = fn
    result_dict[p_name][delete_rate][bootstrap_idx]['target_sum_commit'][issue_dir] = target_sum_commit
    result_dict[p_name][delete_rate][bootstrap_idx]['num_sum_commit'][issue_dir] = num_sum_commit


def evaluate_deleted(deleted_ground_truth_dict, target_dict, p_name, delete_rate, bootstrap_idx, issue_dir, result_dict):
    tp = 0
    fn = 0
    num_sum_commit = 0

    for issue_id in deleted_ground_truth_dict:
        num_sum_commit += len(deleted_ground_truth_dict[issue_id])
        if not issue_id in target_dict:
            fn += len(deleted_ground_truth_dict[issue_id])
            continue

        temp_set = set(target_dict[issue_id]) & set(deleted_ground_truth_dict[issue_id])

        tp += len(temp_set)
        fn += len(set(deleted_ground_truth_dict[issue_id]) - set(target_dict[issue_id]))

    result_dict[p_name][delete_rate][bootstrap_idx]['deleted_tp'][issue_dir] = tp
    result_dict[p_name][delete_rate][bootstrap_idx]['deleted_fn'][issue_dir] = fn


def take_diff_issue2hash_dict(dict_1, dict_2):

    return_dict = {}
    for key_1 in dict_1.keys():
        if not key_1 in dict_2:
            return_dict[key_1] = dict_1[key_1]
            continue
        
        temp_list = []
        temp_set = set(dict_2[key_1])
        for value_1 in dict_1[key_1]:
            if value_1 in temp_set:
                continue    

            temp_list.append(value_1)

        if len(temp_list)>0:
            return_dict[key_1] = temp_list

    return return_dict



def evaluate_ILA(p_name, delete_rate, bootstrap_idx, result_dict):
    ground_truth_dict = util.load_pickle("./data/{0}_keyword_extraction_0_{1}_with_restriction.pickle".format(p_name, bootstrap_idx))
    deleted_ground_truth_dict = util.load_pickle("./data/{0}_keyword_extraction_{1}_{2}_with_restriction.pickle".format(p_name, delete_rate, bootstrap_idx))

    deleted_issue2hash_dict = take_diff_issue2hash_dict(ground_truth_dict, deleted_ground_truth_dict)

    # test script
    #_test(deleted_issue2hash_dict, delete_rate)
    #return 0

    ILA_dict = {"1": "{0}_keyword_extraction_0_{1}_with_restriction".format(p_name, bootstrap_idx),
                "3": "{0}_time_filtering_min_af{1}_with_restriction".format(p_name, TIME_FILTERING_MIN),
                "5": "{0}_ntext_similarity_costh{1}_with_restriction".format(p_name, NTEXT_TH),
                "7": "{0}_{1}_word_association_th{2}_bi{3}_with_restriction".format(p_name, delete_rate, WORD_ASSOC_TH, bootstrap_idx),
                "8": "{0}_comment_costh0.{1}_ite1_with_restriction".format(p_name, COMMENT_COS_TH),
                "9_1": "{0}_{1}_loner_bi{2}_with_restriction".format(p_name, delete_rate, bootstrap_idx),
                "9_2": "{0}_{1}_phantom_bi{2}_with_restriction".format(p_name, delete_rate, bootstrap_idx),
                "10": "{0}_nsd_similarity_costh{1}_with_restriction".format(p_name, NSD_SIM_COS_TH),
                "11": "{0}_{1}_pu_link_bi{2}_with_restriction".format(p_name, delete_rate, bootstrap_idx),
                "14_1": "{0}_RF_{1}_model_bi{2}_with_restriction".format(p_name, delete_rate, bootstrap_idx),
                "14_2": "{0}_SVM_{1}_model_bi{2}_with_restriction".format(p_name, delete_rate, bootstrap_idx)}


    for issue_dir in ILA_dict.keys():
        
        #print(ILA_dict[issue_dir])

        target_dict = util.load_pickle("./data/{0}.pickle".format(ILA_dict[issue_dir]))

        evaluate(ground_truth_dict, target_dict, issue_dir, p_name, delete_rate, bootstrap_idx, result_dict)

        #print("-------")
        #print("for deleted data")
        evaluate_deleted(deleted_issue2hash_dict, target_dict, p_name, delete_rate, bootstrap_idx, issue_dir, result_dict)

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

def main():

    result_dict = initialize_table_dict()

    for p_name in project_name_list:
        print("================")
        print(p_name)
        print("================")

        for delete_rate in deleted_rate_list:
            print("-------")
            print("deleted rate: {0}".format(delete_rate))

            for bootstrap_idx in range(BOOTSTRAP_SIZE):

                evaluate_ILA(p_name, delete_rate, bootstrap_idx, result_dict)

    print("")
    util.dump_pickle("./result/evaluation_with_restriction.pickle", result_dict)

if __name__=="__main__":

    main()
