import sys
import pandas as pd
import numpy as np
import pyper

from Utils import util


project_name_list = ["project name here"]
deleted_rate_list = [10, 20, 30, 40, 50]

BOOTSTRAP_SIZE = 100

target_data_list = ["evaluation_with_restriction"]

DISP_ILA_dict = {"1": "KE", "3": "TF",
            "4": "DF",
            "5": "TS", "7": "WA",
            "8": "GS", "9_1": "LO", "9_2": "PH",
            "10": "MT", "11": "PU",
            "14_1": "RF", "14_2": "SVM"}

ILA_list = ['3','5','7','8','9_1','9_2','10','11','14_1','14_2']

THRESHOLD = 0.7

def convert2list(data_dict, target_key, ILA):
    temp_list = []
    for bootstrap_idx in range(BOOTSTRAP_SIZE):
        temp_list.append(data_dict[bootstrap_idx][target_key][ILA])
    return temp_list


def compute_tp_rate(deleted_tp, deleted_fn):
    temp_list = []
    for bootstrap_idx in range(BOOTSTRAP_SIZE):
        temp_list.append(
            deleted_tp[bootstrap_idx]/(deleted_tp[bootstrap_idx] + deleted_fn[bootstrap_idx])
        )

    return temp_list

def compute_f1(precision, recall):
    temp_list = []
    for bootstrap_idx in range(BOOTSTRAP_SIZE):
        if (precision[bootstrap_idx] + recall[bootstrap_idx])==0:
            temp_list.append(0)
        else:
            temp_list.append(
                2 * (precision[bootstrap_idx] * recall[bootstrap_idx]) / (precision[bootstrap_idx] + recall[bootstrap_idx])
            )

    return temp_list

def ggplot2_SKESD(dat_dict, plot_name, xlabel, ylabel, rank1_list, rank_dict):
    df = pd.DataFrame(dat_dict)
    r = pyper.R(use_pandas=True)
    r('library(ggplot2)')
    r('library(reshape2)')
    r('set.seed(200)')

    r("source('./SKESD.R')")
    r.assign("plot_name", plot_name)
    r.assign("xlabel", xlabel)
    r.assign("ylabel", ylabel)

    r.assign("df", df)
    #print(r("print(df)"))

    print(r("sk = create_boxplot(df,plot_name,xlabel,ylabel)"))

    sk = r.get("sk")
    print(r("print(sk)"))
    for sk_rank, idx in zip(sk['groups'], sk['ord']):
        print("{0}: {1}".format(sk['nms'][idx-1], sk_rank))
        rank_dict[sk['nms'][idx-1]] = sk_rank
        if sk_rank==1:
            rank1_list.append(sk['nms'][idx-1])

    #print(sk['groups'])
    #print(sk['nms'])
    #print(sk['ord'])

def conduct_SKESD(result_dict):

    rank1_dict = {}
    rank_dict = {}
    for p_name in project_name_list:
        rank1_dict[p_name] = {}
        rank_dict[p_name] = {}
        print(p_name)
        for delete_rate in deleted_rate_list:

            rank_dict[p_name][delete_rate] = {}

            precision_dict = {}
            recall_dict = {}
            deleted_tp_rate_dict = {}
            f1_dict = {}

            for ILA in ILA_list:
                tmp = result_dict[p_name][delete_rate]

                precision = convert2list(tmp, 'precision', ILA)
                recall = convert2list(tmp, 'recall', ILA)
                deleted_tp = convert2list(tmp, 'deleted_tp', ILA)
                deleted_fn = convert2list(tmp, 'deleted_fn', ILA)
                deleted_tp_rate = compute_tp_rate(deleted_tp, deleted_fn)
                f1 = compute_f1(precision, recall)

                precision_dict[DISP_ILA_dict[ILA]] = precision
                recall_dict[DISP_ILA_dict[ILA]] = recall
                deleted_tp_rate_dict[DISP_ILA_dict[ILA]] = deleted_tp_rate
                f1_dict[DISP_ILA_dict[ILA]] = f1

            print("\n===\nprecision")
            rank1_dict[p_name]['precision'] = []
            rank_dict[p_name][delete_rate]['precision'] = {}
            ggplot2_SKESD(precision_dict, "./plot/{0}_{1}_precision.pdf".format(p_name, delete_rate),
                          "", "precision", rank1_dict[p_name]['precision'], rank_dict[p_name][delete_rate]['precision'])

            print("\n===\nrecall")
            rank1_dict[p_name]['recall'] = []
            rank_dict[p_name][delete_rate]['recall'] = {}
            ggplot2_SKESD(recall_dict, "./plot/{0}_{1}_recall.pdf".format(p_name, delete_rate),
                          "", "recall", rank1_dict[p_name]['recall'], rank_dict[p_name][delete_rate]['recall'])

            print("\n===\ndeleted_tp_rate")
            rank1_dict[p_name]['TP'] = []
            rank_dict[p_name][delete_rate]['TP'] = {}
            ggplot2_SKESD(deleted_tp_rate_dict, "./plot/{0}_{1}_tp_rate.pdf".format(p_name, delete_rate),
                          "", "TP rate", rank1_dict[p_name]['TP'], rank_dict[p_name][delete_rate]['TP'])

            print("\n===\nF1")
            rank1_dict[p_name]['F1'] = []
            rank_dict[p_name][delete_rate]['F1'] = {}
            ggplot2_SKESD(f1_dict, "./plot/{0}_{1}_f1.pdf".format(p_name, delete_rate),
                          "", "F1", rank1_dict[p_name]['F1'], rank_dict[p_name][delete_rate]['F1'])

    print(rank1_dict)
    util.dump_pickle("./result/SKESD_rank.pickle", rank_dict)



def main():
    for target_data in target_data_list:

        result_dict = util.load_pickle("./result/{0}.pickle".format(target_data))
        conduct_SKESD(result_dict)

if __name__=="__main__":

    main()


