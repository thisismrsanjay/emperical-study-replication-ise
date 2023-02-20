import csv
import numpy as np
import sys
import pandas as pd
import pyper
import sqlite3

from Utils import util

sys.path.append("./../../RQ2/DP")
import evaluation

import warnings
warnings.simplefilter('ignore')


projectName = [
    "project name here"
    ]

ila_list = ["1", "3", "5", "9_2", "14_1", "14_2", "3,5", "3,9_2", "3,14_1", "3,14_2",
            "5,9_2", "5,14_1", "5,14_2", "9_2,14_1", "9_2,14_2", "14_1,14_2",
            "3,5,9_2", "3,5,14_1", "3,5,14_2", "3,9_2,14_1", "3,9_2,14_2", "3,14_1,14_2",
            "5,9_2,14_1", "5,9_2,14_2", "5,14_1,14_2", "9_2,14_1,14_2",
            "3,5,9_2,14_1", "3,5,9_2,14_2", "3,5,14_1,14_2",
            "3,9_2,14_1,14_2", "5,9_2,14_1,14_2",
            "3,5,9_2,14_1,14_2"]

delete_rate_list = ["0", "10", "20", "30", "40", "50"]
#delete_rate_list = ["10", "20", "30", "40", "50"]
#delete_rate_list = ["0"]

ILA_dict = {"1": "KE", "3": "TF",
            "5": "TS", "7": "WA",
            "8": "GS", "9_1": "LO", "9_2": "PH",
            "10": "MT", "11": "PU",
            "14_1": "RF", "14_2": "SVM"}

modelName = ['LR']

BOOTSTRAP_SIZE = 20

def read_commit_size(db_path):
    """Extract snippet data from database"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    command = """SELECT commit_hash,la,ld
                 FROM data;"""
    cur.execute(command)

    size_dict = {}
    for row in cur.fetchall():
        size_dict[row[0]] = float(row[1]) + float(row[2])

    conn.close()

    return size_dict

def compute_effort_measures(effort_ins, ground_truth_effort_ins, result_dict):
    result_dict['IFA'].append(abs(ground_truth_effort_ins.IFA() - effort_ins.IFA()))
    result_dict['PII20%'].append(abs(ground_truth_effort_ins.PII(20, prob=True) - effort_ins.PII(20, prob=True)))
    result_dict['PII1000'].append(abs(ground_truth_effort_ins.PII(1000) - effort_ins.PII(1000)))
    result_dict['PII2000'].append(abs(ground_truth_effort_ins.PII(2000) - effort_ins.PII(2000)))
    result_dict["CostEffort20%"].append(abs(ground_truth_effort_ins.CostEffort(20, prob=True) - effort_ins.CostEffort(20, prob=True)))
    result_dict["CostEffort1000"].append(abs(ground_truth_effort_ins.CostEffort(1000) - effort_ins.CostEffort(1000)))
    result_dict["CostEffort2000"].append(abs(ground_truth_effort_ins.CostEffort(2000) - effort_ins.CostEffort(2000)))
    result_dict["NPopt"].append(abs(ground_truth_effort_ins.norm_popt(L=20) - effort_ins.norm_popt(L=20)))


def read_evaluation_one_ground_truth_for_all_iterations(delete_rate, m_name, p_name, ILA_num):
    """
    Read the results on all the iterations (even if at least one positive example (defective commit) does not exist).
    This positive label is decided by the keyword extraction.
    Hence, we need to recompute the evaluation measures for each ILA.
    Finally, return the result_dict

    Arguments:
    delete_rate: [string] -- deleted rate
    m_name: [string] -- model name
    p_name: [string] -- project name
    ILA_num: [string] -- ILA number

    Returns:
    result_dict [dict<string, list<float>>] -- key is evaluation name (e.g., AUC), value is a list of evaluation values
    """

    size_dict = read_commit_size("./../../RQ2/commitguru_data/{0}.db".format(p_name))

    result_dict = {'IFA': [], 'PII20%': [], 'PII1000': [], 'PII2000': [],
                   'CostEffort20%': [], 'CostEffort1000': [], 'CostEffort2000': [],
                   'NPopt': []}
    for bootstrap_idx in range(BOOTSTRAP_SIZE):

        ground_truth_label = {}
        with open("./../../RQ2/DP/results/delete0/bi{0}/label_{1}_{2}_1.csv".format(bootstrap_idx, p_name, m_name)) as f:
            reader = csv.reader(f)
            for ite, row in enumerate(reader):
                ground_truth_label[ite] = list(map(int, row))

        ground_truth_prob = {}
        with open("./../../RQ2/DP/results/delete0/bi{0}/prob_{1}_{2}_1.csv".format(bootstrap_idx, p_name, m_name)) as f:
            reader = csv.reader(f)
            for ite, row in enumerate(reader):
                ground_truth_prob[ite] = list(map(float, row))

        test_commits = util.load_pickle("./../../RQ2/DP/results/delete0/bi{0}/test_commits_{1}_{2}_1.pickle".format(bootstrap_idx, p_name, m_name))

        # evaluation order: AUC (0), F1 (1), Precision (2), Recall (3), MCC (4), Brier (5)
        all_prob_list = []
        all_ground_truth_prob = []
        all_ground_truth_label = []
        all_size_list = []
        with open("./../../RQ2/DP/results/delete{0}/bi{1}/prob_{2}_{3}_{4}.csv".format(delete_rate, bootstrap_idx, p_name, m_name, ILA_num)) as f:
            reader = csv.reader(f)
            for ite, prob_list in enumerate(reader):

                all_prob_list.extend(list(map(float, prob_list)))
                all_ground_truth_prob.extend(ground_truth_prob[ite])
                all_ground_truth_label.extend(ground_truth_label[ite])

                for commit_hash in test_commits[ite]:
                    all_size_list.append(size_dict[commit_hash])

        effort_ins = evaluation.EffortAwareEvaluation(all_prob_list, all_ground_truth_label, all_size_list)
        ground_truth_effort_ins = evaluation.EffortAwareEvaluation(all_ground_truth_prob, all_ground_truth_label, all_size_list)

        compute_effort_measures(effort_ins, ground_truth_effort_ins, result_dict)

    return result_dict


def display_all_ite(delete_rate, p_name, ILA_num, evaluation_data_dict):
    print("delete Rate: {0}, Project: {1}, ILA: {2}, IFA: {3}, PII20%: {4}, PII1000: {5}, PII2000: {6}, CostEffort20%: {7}, CostEffort1000: {8}, CostEffort2000: {9}, Normalized(Popt): {10}".format(
        delete_rate, p_name, ILA_num,
        round(np.median(evaluation_data_dict['IFA']), 3),
        round(np.median(evaluation_data_dict['PII20%']), 3),
        round(np.median(evaluation_data_dict['PII1000']), 3),
        round(np.median(evaluation_data_dict['PII2000']), 3),
        round(np.median(evaluation_data_dict['CostEffort20%']), 3),
        round(np.median(evaluation_data_dict['CostEffort1000']), 3),
        round(np.median(evaluation_data_dict['CostEffort2000']), 3),
        round(np.median(evaluation_data_dict['NPopt']), 3),
        ))

def ggplot2_Brier_SKESD(dat_dict, plot_name, xlabel, ylabel, rank_dict):
    df = pd.DataFrame(dat_dict)
    r = pyper.R(use_pandas=True)
    r('library(ggplot2)')
    r('library(reshape2)')
    r('set.seed(200)')

    r("source('./../../RQ2/evaluation/diff_SKESD.R')")
    r.assign("plot_name", plot_name)
    r.assign("xlabel", xlabel)
    r.assign("ylabel", ylabel)

    r.assign("df", df)
    #print(r("print(df)"))

    print(r("sk = create_boxplot(df,plot_name,xlabel,ylabel)"))

    sk = r.get("sk")

    rank_list = []
    for sk_rank in sk['groups']:
        rank_list.append(sk_rank)
    max_rank = max(rank_list)

    for sk_rank, idx in zip(sk['groups'], sk['ord']):
        #rank_dict[sk['nms'][idx-1]] = sk_rank
        rank_dict[sk['nms'][idx-1]] = (max_rank + 1) - sk_rank



def main(delete_rate, m_name, p_name, ILA_num, table_dict, result_dict):

    evaluation_data_dict = read_evaluation_one_ground_truth_for_all_iterations(delete_rate, m_name, p_name, ILA_num)
    display_all_ite(delete_rate, p_name, ILA_num, evaluation_data_dict)

    result_dict[delete_rate][m_name][p_name][ILA_num] = evaluation_data_dict

    for e_name in evaluation_data_dict.keys():
        if not e_name in table_dict[p_name]:
            table_dict[p_name][e_name] = {}

        ILA_str_list = []
        for temp in ILA_num.split(","):
            ILA_str_list.append(ILA_dict[temp])
        table_dict[p_name][e_name][",".join(ILA_str_list)] = evaluation_data_dict[e_name]

if __name__=="__main__":


    rank_dict = {}
    result_dict = {}
    for delete_rate in delete_rate_list:
        rank_dict[delete_rate] = {}
        result_dict[delete_rate] = {}
        for m_name in modelName:
            rank_dict[delete_rate][m_name] = {}
            result_dict[delete_rate][m_name] = {}
            table_dict = {}
            for p_name in projectName:
                rank_dict[delete_rate][m_name][p_name] = {}
                result_dict[delete_rate][m_name][p_name] = {}
                table_dict[p_name] = {}
                print("---")
                for ILA_num in ila_list:
                    main(delete_rate, m_name, p_name, ILA_num, table_dict, result_dict)

                print("")

                for e_name in table_dict[p_name].keys():
                    rank_dict[delete_rate][m_name][p_name][e_name] = {}

                    ggplot2_Brier_SKESD(table_dict[p_name][e_name], "./effort_plot/diff_{0}_{1}_{2}_{3}.pdf".format(p_name, delete_rate, m_name, e_name.replace("%","")),
                                  "", e_name, rank_dict[delete_rate][m_name][p_name][e_name])

    util.dump_pickle("results/effort_diff_rank_data.pickle", rank_dict)
    util.dump_pickle("results/effort_diff_result_data.pickle", result_dict)







