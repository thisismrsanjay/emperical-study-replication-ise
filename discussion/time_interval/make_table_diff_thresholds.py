import sys
import pandas as pd
import numpy as np

from Utils import util

project_name_list = ["project name here"]
deleted_rate_list = [10, 20, 30, 40, 50]

BOOTSTRAP_SIZE = 100

table_column = ['Project', 'Precision', 'Recall', 'F1', 'TP rate (deleted)']

target_data_list = ["evaluation_with_restriction"]

ILA_dict = {"ntext": "ntext similarity", "comment": "comment", "time": "time filtering"}
ILA_list = ["time"]

THRESHOLD = 0.7

def add_graybox(target):
    if target>=THRESHOLD:
        #value = '\\cellcolor[gray]{0.85}{%03.3f}' % target
        value = '\\cellcolor{yellow}{%03.3f}' % target
    else:
        value = "%03.3f" % target
    return value

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


def make_table(target_data):
    rank_dict = util.load_pickle("./result_th/SKESD_rank.pickle")

    for p_name in project_name_list:
        for delete_rate in deleted_rate_list:

            for ILA in ILA_list:
                TABLE = []

                if ILA in ["ntext", "comment"]:
                    THRESHOLD_LIST = range(1,10)
                else:
                    THRESHOLD_LIST = [5, 10, 30, 60, 120]

                for cosine_th in THRESHOLD_LIST:

                    result_dict = util.load_pickle("./result_th/{0}_{1}_{2}.pickle".format(target_data, ILA, cosine_th))
                    tmp = result_dict[p_name][delete_rate]

                    #acc = add_graybox(tmp['acc'][ILA])
                    precision = add_graybox(compute_median(tmp, 'precision', ILA))
                    recall = add_graybox(compute_median(tmp, 'recall', ILA))
                    deleted_tp = add_graybox(compute_median_tp_rate(convert2list(tmp, 'deleted_tp', ILA), convert2list(tmp, 'deleted_fn', ILA)))
                    #deleted_fn = add_graybox(round(compute_median(tmp, 'deleted_fn', ILA)/(compute_median(tmp, 'deleted_tp', ILA) + compute_median(tmp, 'deleted_fn', ILA)), 3))
                    f1 = add_graybox(compute_f1(convert2list(tmp, 'precision', ILA), convert2list(tmp, 'recall', ILA)))

                    if ILA in ["ntext", "comment"]:
                        TEMP_THRESHOLD = "0.{0}".format(cosine_th)
                    else:
                        TEMP_THRESHOLD = "{0}".format(cosine_th)


                    #row = [TEMP_THRESHOLD,
                    #       "{0} ({1:,}/({2:,}+{3:,}))".format(precision, MT.compute_median(tmp, 'tp', ILA), MT.compute_median(tmp, 'tp', ILA), MT.compute_median(tmp, 'fp', ILA)),
                    #       "{0} ({1:,}/({2:,}+{3:,}))".format(recall, MT.compute_median(tmp, 'tp', ILA), MT.compute_median(tmp, 'tp', ILA), MT.compute_median(tmp, 'fn', ILA)),
                    #       "{0}".format(f1),
                    #       "{0} ({1:,}/{2:,})".format(deleted_tp, MT.compute_median(tmp, 'deleted_tp', ILA), MT.compute_median(tmp, 'deleted_tp', ILA)+ MT.compute_median(tmp, 'deleted_fn', ILA))
                    #]
                    row = [TEMP_THRESHOLD,
                           "{0} ({1})".format(precision, rank_dict[p_name][delete_rate][ILA]['precision']["X{0}".format(cosine_th)]),
                           "{0} ({1})".format(recall, rank_dict[p_name][delete_rate][ILA]['recall']["X{0}".format(cosine_th)]),
                           "{0} ({1})".format(f1, rank_dict[p_name][delete_rate][ILA]['F1']["X{0}".format(cosine_th)]),
                           "{0} ({1})".format(deleted_tp, rank_dict[p_name][delete_rate][ILA]['TP']["X{0}".format(cosine_th)])
                    ]
                    #for e_name in evaluation_measure_list:
                    #    row.append("{0}".format(result_dict[p_name][delete_rate][e_name][ILA]))

                    row[-1] = "{0}\\\\".format(row[-1])
                    TABLE.append(row)

                TABLE = pd.DataFrame(TABLE,columns=table_column)
                TABLE.to_csv(path_or_buf='./tables_th/diff_{0}_{1}_{2}_{3}.csv'.format(target_data, p_name, ILA, delete_rate),index=False, sep="&")

def main():
    for target_data in target_data_list:

        make_table(target_data)

if __name__=="__main__":

    main()

