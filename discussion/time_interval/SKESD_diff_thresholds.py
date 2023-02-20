import sys
import pandas as pd
import numpy as np
import pyper

from Utils import util


project_name_list = ["project name here"]
deleted_rate_list = [10, 20, 30, 40, 50]

BOOTSTRAP_SIZE = 100



ILA_list = ["time"]


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

def ggplot2_SKESD(dat_dict, plot_name, xlabel, ylabel, rank_dict):
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

    #print(sk['groups'])
    #print(sk['nms'])
    #print(sk['ord'])

def conduct_SKESD():

    rank_dict = {}
    for p_name in project_name_list:
        rank_dict[p_name] = {}
        print(p_name)
        for delete_rate in deleted_rate_list:

            rank_dict[p_name][delete_rate] = {}

            for ILA in ILA_list:
                rank_dict[p_name][delete_rate][ILA] = {}

                precision_dict = {}
                recall_dict = {}
                deleted_tp_rate_dict = {}
                f1_dict = {}

                if ILA in ["ntext", "comment"]:
                    THRESHOLD_LIST = range(1,10)
                else:
                    THRESHOLD_LIST = [5, 10, 30, 60, 120]

                for cosine_th in THRESHOLD_LIST:

                    result_dict = util.load_pickle("./result_th/evaluation_with_restriction_{0}_{1}.pickle".format(ILA, cosine_th))
                    tmp = result_dict[p_name][delete_rate]

                    precision = convert2list(tmp, 'precision', ILA)
                    recall = convert2list(tmp, 'recall', ILA)
                    deleted_tp = convert2list(tmp, 'deleted_tp', ILA)
                    deleted_fn = convert2list(tmp, 'deleted_fn', ILA)
                    deleted_tp_rate = compute_tp_rate(deleted_tp, deleted_fn)
                    f1 = compute_f1(precision, recall)

                    precision_dict[cosine_th] = precision
                    recall_dict[cosine_th] = recall
                    deleted_tp_rate_dict[cosine_th] = deleted_tp_rate
                    f1_dict[cosine_th] = f1

                print("\n===\nprecision")
                rank_dict[p_name][delete_rate][ILA]['precision'] = {}
                ggplot2_SKESD(precision_dict, "./plot_th/{0}_{1}_{2}_precision.pdf".format(p_name, delete_rate, ILA),
                              "", "precision", rank_dict[p_name][delete_rate][ILA]['precision'])

                print("\n===\nrecall")
                rank_dict[p_name][delete_rate][ILA]['recall'] = {}
                ggplot2_SKESD(recall_dict, "./plot_th/{0}_{1}_{2}_recall.pdf".format(p_name, delete_rate, ILA),
                              "", "recall", rank_dict[p_name][delete_rate][ILA]['recall'])

                print("\n===\ndeleted_tp_rate")
                rank_dict[p_name][delete_rate][ILA]['TP'] = {}
                ggplot2_SKESD(deleted_tp_rate_dict, "./plot_th/{0}_{1}_{2}_tp_rate.pdf".format(p_name, delete_rate, ILA),
                              "", "TP rate", rank_dict[p_name][delete_rate][ILA]['TP'])

                print("\n===\nF1")
                rank_dict[p_name][delete_rate][ILA]['F1'] = {}
                ggplot2_SKESD(f1_dict, "./plot_th/{0}_{1}_{2}_f1.pdf".format(p_name, delete_rate, ILA),
                              "", "F1", rank_dict[p_name][delete_rate][ILA]['F1'])

    util.dump_pickle("./result_th/SKESD_rank.pickle", rank_dict)



def main():

    conduct_SKESD()

if __name__=="__main__":

    main()

    # unit test
    #precision = [0.3, 1.0, 0.5]
    #recall = [1.0, 0.33, 0.67]
    #print(compute_f1(precision, recall))

