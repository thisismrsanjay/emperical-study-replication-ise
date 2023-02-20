import sys
import pandas as pd
import numpy as np

from Utils import util


project_name_list = ["project name here"]
deleted_rate_list = [10, 20, 30, 40, 50]

BOOTSTRAP_SIZE = 100

table_column = ['Project', 'Precision', 'Recall', 'F1', 'TP rate (deleted)']

target_data_list = ["evaluation_with_restriction"]

ILA_dict = {"1": "keyword extraction", "3": "time filtering",
            "4": "dev. filtering with comments",
            "5": "ntext similarity", "7": "word association",
            "8": "comment", "9_1": "loner", "9_2": "phantom",
            "10": "nsd similarity", "11": "pu link",
            "14_1": "RF model", "14_2": "SVM model"}


DISP_ILA_dict = {"1": "KE", "3": "TF",
            "4": "DF",
            "5": "TS", "7": "WA",
            "8": "GS", "9_1": "LO", "9_2": "PH",
            "10": "MT", "11": "PU",
            "14_1": "RF", "14_2": "SVM"}

ILA_list = ['3','5','7','8','9_1','9_2','10','11','14_1','14_2']


def add_graybox(target, rank):
    if rank==1:
        value = '\\cellcolor{yellow}{%03.3f}' % target
    else:
        value = "%03.3f" % target
    return value + " ({0})".format(rank)


def compute_median(data_dict, target_key, ILA):
    temp_list = []
    for bootstrap_idx in range(BOOTSTRAP_SIZE):
        temp_list.append(data_dict[bootstrap_idx][target_key][ILA])
    return round(np.median(temp_list), 3)

def convert2list(data_dict, target_key, ILA):
    temp_list = []
    for bootstrap_idx in range(BOOTSTRAP_SIZE):
        temp_list.append(data_dict[bootstrap_idx][target_key][ILA])
    return temp_list

def compute_median_tp_rate(deleted_tp, deleted_fn):
    temp_list = []
    for bootstrap_idx in range(BOOTSTRAP_SIZE):
        temp_list.append(
            deleted_tp[bootstrap_idx]/(deleted_tp[bootstrap_idx] + deleted_fn[bootstrap_idx])
        )

    return round(np.median(temp_list), 3)

def compute_f1(precision, recall):
    temp_list = []
    for bootstrap_idx in range(BOOTSTRAP_SIZE):
        if (precision[bootstrap_idx] + recall[bootstrap_idx])==0:
            temp_list.append(0)
        else:
            temp_list.append(
                2 * (precision[bootstrap_idx] * recall[bootstrap_idx]) / (precision[bootstrap_idx] + recall[bootstrap_idx])
            )

    return round(np.median(temp_list), 3)

def make_table(target_data, result_dict, rank_dict):

    for p_name in project_name_list:
        for delete_rate in deleted_rate_list:

            TABLE = []

            for ILA in ILA_list:
                tmp = result_dict[p_name][delete_rate]

                precision = add_graybox(compute_median(tmp, 'precision', ILA), rank_dict[p_name][delete_rate]['precision'][DISP_ILA_dict[ILA]])
                recall = add_graybox(compute_median(tmp, 'recall', ILA), rank_dict[p_name][delete_rate]['recall'][DISP_ILA_dict[ILA]])
                deleted_tp = add_graybox(compute_median_tp_rate(convert2list(tmp, 'deleted_tp', ILA), convert2list(tmp, 'deleted_fn', ILA)), rank_dict[p_name][delete_rate]['TP'][DISP_ILA_dict[ILA]])
                #deleted_fn = add_graybox(round(compute_median(tmp, 'deleted_fn', ILA)/(compute_median(tmp, 'deleted_tp', ILA) + compute_median(tmp, 'deleted_fn', ILA)), 3))
                f1 = add_graybox(compute_f1(convert2list(tmp, 'precision', ILA), convert2list(tmp, 'recall', ILA)), rank_dict[p_name][delete_rate]['F1'][DISP_ILA_dict[ILA]])


                row = ["\\" + DISP_ILA_dict[ILA] + "{}",
                    "{0}".format(precision),
                    "{0}".format(recall),
                    "{0}".format(f1),
                    "{0}".format(deleted_tp)
                ]
                #for e_name in evaluation_measure_list:
                #    row.append("{0}".format(result_dict[p_name][delete_rate][e_name][ILA]))

                row[-1] = "{0}\\\\".format(row[-1])
                TABLE.append(row)

            TABLE = pd.DataFrame(TABLE,columns=table_column)
            TABLE.to_csv(path_or_buf='./tables/rank_{0}_{1}_{2}.csv'.format(target_data, p_name, delete_rate),index=False, sep="&")

def main():
    for target_data in target_data_list:

        result_dict = util.load_pickle("./result/{0}.pickle".format(target_data))
        rank_dict = util.load_pickle("./result/SKESD_rank.pickle")

        # HERE we need to compute the median across the bootstrap idx
        make_table(target_data, result_dict, rank_dict)

if __name__=="__main__":

    main()
