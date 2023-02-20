import sys
import pandas as pd
import numpy as np

from scipy.stats import spearmanr
from collections import Counter

from Utils import util


project_name_list = [
    "project name here"
    ]

deleted_rate_list = ["0", "10", "20", "30", "40", "50"]

ILA_dict = {"1": "keyword extraction", "3": "time filtering",
            "4": "dev. filtering with comments",
            "5": "ntext similarity", "7": "word association",
            "8": "comment", "9_1": "loner", "9_2": "phantom",
            "10": "nsd similarity", "11": "pu link",
            "14_1": "RF model", "14_2": "SVM model"}

modelName = ['LR']

DISP_ILA_dict = {"1": "KE", "3": "TF",
                 "4": "DF",
                 "5": "TS", "7": "WA",
                 "8": "GS", "9_1": "LO", "9_2": "PH",
                 "10": "MT", "11": "PU",
                 "14_1": "RF", "14_2": "SVM"}

ILA_list = ["1", "3", "5", "9_2", "14_1", "14_2", "3,5", "3,9_2", "3,14_1", "3,14_2",
            "5,9_2", "5,14_1", "5,14_2", "9_2,14_1", "9_2,14_2", "14_1,14_2",
            "3,5,9_2", "3,5,14_1", "3,5,14_2", "3,9_2,14_1", "3,9_2,14_2", "3,14_1,14_2",
            "5,9_2,14_1", "5,9_2,14_2", "5,14_1,14_2", "9_2,14_1,14_2",
            "3,5,9_2,14_1", "3,5,9_2,14_2", "3,5,14_1,14_2",
            "3,9_2,14_1,14_2", "5,9_2,14_1,14_2",
            "3,5,9_2,14_1,14_2"]

evaluation_name_list = [
                'IFA',
                'PII20%',
                'PII1000',
                'PII2000',
                'CostEffort20%',
                'CostEffort1000',
                'CostEffort2000',
                'NPopt',
                ]

table_column = ['Project', 
                'IFA',
                'PII@20\\%',
                'PII@1000',
                'PII@2000',
                'CostEffort@20\\%',
                'CostEffort@1000',
                'CostEffort@2000',
                '$P_{opt}$',
                'COUNT'
                ]

def add_graybox(target, rank, ke_rank):
    yellow_cnt = 0
    all_cnt = 0
    if rank==1:
        value = '\\cellcolor{yellow}{%03.3f}' % target
        yellow_cnt = 1
        all_cnt = 1
    elif rank<ke_rank:
        value = '\\cellcolor{cyan}{%03.3f}' % target
        all_cnt = 1
    else:
        value = "%03.3f" % target
    return value + " ({0})".format(rank), yellow_cnt, all_cnt


def make_table(result_dict, rank_dict):

    temp_all_ILA_list = []
    cnt_ILA_better_rank = {}
    for m_name in modelName:
        for delete_rate in deleted_rate_list:

            for p_name in project_name_list:
                TABLE = []
                temp_ILA_list = []

                for ILA in ILA_list:

                    ILA_str_list = []
                    for temp in ILA.split(","):
                        ILA_str_list.append("\\" + DISP_ILA_dict[temp] + "{}")
                    ILA_name = ",".join(ILA_str_list)
                    row = [ILA_name]
                    yellow_cnt = 0
                    all_cnt = 0
                    for e_name in evaluation_name_list:
                        output, temp_yellow_cnt, temp_all_cnt = add_graybox(round(np.median(result_dict[delete_rate][m_name][p_name][ILA][e_name]), 3),
                                                                              rank_dict[delete_rate][m_name][p_name][e_name][ILA_name.replace(",",".").replace("\\","").replace("{}","")],
                                                                              rank_dict[delete_rate][m_name][p_name][e_name]["KE"])
                        row.append("{0}".format(output))
                        yellow_cnt = yellow_cnt + temp_yellow_cnt
                        all_cnt = all_cnt + temp_all_cnt


                    row.append("{0} ({1})\\\\".format(all_cnt, yellow_cnt))
                    TABLE.append(row)

                    if all_cnt>=3:
                        temp_ILA_list.append(ILA_name)
                        temp_all_ILA_list.append(ILA_name)

                    if not ILA_name in cnt_ILA_better_rank:
                        cnt_ILA_better_rank[ILA_name] = 0
                    cnt_ILA_better_rank[ILA_name] += all_cnt


                TABLE = pd.DataFrame(TABLE,columns=table_column)
                TABLE.to_csv(path_or_buf='./effort_tables/diff_rank_{0}_{1}_{2}.csv'.format(p_name, delete_rate, m_name),index=False, sep="&")

                print("\n===")
                print("{0}, delete: {1}, project: {2}".format(m_name, delete_rate, p_name))
                print(temp_ILA_list)

    print("\n===")
    print("Total count (max: 18, except delete=0: max: 15)")
    print(Counter(temp_all_ILA_list))

    print("Sum of the better rank (max: 108, except delete=0: max: 90)")
    diff_rank_sum_list = sorted(cnt_ILA_better_rank.items(), key=lambda x:-x[1])
    TABLE = []
    for diff_rank_sum in diff_rank_sum_list:
        row = []
        row.append(diff_rank_sum[0])
        row.append("{0}\\\\".format(diff_rank_sum[1]))
        TABLE.append(row)
    TABLE = pd.DataFrame(TABLE,columns=["\\ILA{}", "SUM\\\\"])
    TABLE.to_csv(path_or_buf='./effort_tables/diff_rank_sum.csv', index=False, sep="&")


def compute_spearman(result_dict, interest_ILA_list):

    corr_dict = {}
    for m_name in modelName:
        corr_dict[m_name] = {}
        for ILA in interest_ILA_list:
            corr_dict[m_name][ILA] = {}
            for p_name in project_name_list:
                corr_dict[m_name][ILA][p_name] = {}
                yellow_cnt = 0
                for e_name in evaluation_name_list:
                    delete_data = []
                    med_diff = []
                    for delete_rate in deleted_rate_list:
                        med_diff.append(np.median(result_dict[delete_rate][m_name][p_name][ILA][e_name]))
                        delete_data.append(int(delete_rate))

                    correlation, pvalue = spearmanr(med_diff, delete_data)
                    #print("\n===")
                    #print("ILA: {0}, p_name: {1}, e_name: {2}".format(ILA, p_name, e_name))
                    #print(med_diff)
                    #print(delete_data)
                    #print("corr: {0}, p-value: {1}".format(round(correlation, 3), pvalue))

                    if correlation<=0:
                        round_corr = '\\cellcolor{yellow}{%03.3f}' % round(correlation, 3)
                        yellow_cnt += 1
                    else:
                        round_corr = "%03.3f" % round(correlation, 3)

                    if pvalue <= 0.001:
                        corr_dict[m_name][ILA][p_name][e_name] = round_corr + "***"
                    elif pvalue <= 0.01:
                        corr_dict[m_name][ILA][p_name][e_name] = round_corr + "**"
                    elif pvalue <= 0.05:
                        corr_dict[m_name][ILA][p_name][e_name] = round_corr + "*"
                    else:
                        corr_dict[m_name][ILA][p_name][e_name] = round_corr
                corr_dict[m_name][ILA][p_name]["yellow_cnt"] = yellow_cnt

    return corr_dict

def make_table_interesting_ILA(result_dict, rank_dict):
    interest_ILA_list = ["1", "3,5", "14_1", "3,14_2", "14_1,14_2", "3,14_1,14_2", "9_2,14_1,14_2"]

    corr_dict = compute_spearman(result_dict, interest_ILA_list)

    for m_name in modelName:
        for ILA in interest_ILA_list:
            ILA_str_list = []
            for temp in ILA.split(","):
                ILA_str_list.append(DISP_ILA_dict[temp])
            ILA_name = ",".join(ILA_str_list)

            TABLE = []
            for p_name in project_name_list:
                for delete_rate in deleted_rate_list:

                    row = [p_name, delete_rate]
                    yellow_cnt = 0
                    all_cnt = 0
                    for e_name in evaluation_name_list:
                        output, temp_yellow_cnt, temp_all_cnt = add_graybox(round(np.median(result_dict[delete_rate][m_name][p_name][ILA][e_name]), 3),
                                                                            rank_dict[delete_rate][m_name][p_name][e_name][ILA_name.replace(",",".").replace("\\","").replace("{}","")],
                                                                            rank_dict[delete_rate][m_name][p_name][e_name]["KE"])
                        row.append("{0}".format(output))
                        yellow_cnt = yellow_cnt + temp_yellow_cnt
                        all_cnt = all_cnt + temp_all_cnt


                    row.append("{0} ({1})\\\\".format(all_cnt, yellow_cnt))
                    TABLE.append(row)

                row = [p_name, "Spearman"]
                for e_name in evaluation_name_list:
                    row.append(corr_dict[m_name][ILA][p_name][e_name])
                row.append("{0}\\\\".format(corr_dict[m_name][ILA][p_name]['yellow_cnt']))
                TABLE.append(row)
                TABLE.append(["\\midrule"])

            temp_table_column = ["Project", "Delete rate"]
            temp_table_column.extend(table_column[1:])
            TABLE = pd.DataFrame(TABLE,columns=temp_table_column)
            TABLE.to_csv(path_or_buf='./effort_tables/diff_rank_{0}_{1}.csv'.format(m_name, ILA_name),index=False, sep="&")


def main():

    result_dict = util.load_pickle("./results/effort_diff_result_data.pickle")
    rank_dict = util.load_pickle("./results/effort_diff_rank_data.pickle")

    # HERE we need to compute the median across the bootstrap idx
    make_table(result_dict, rank_dict)

    make_table_interesting_ILA(result_dict, rank_dict)

if __name__=="__main__":

    main()

    # _unit test
    #import random
    #data_dict = {}
    #for idx, bootstrap_idx in enumerate(range(BOOTSTRAP_SIZE)):
    #    #data_dict[bootstrap_idx] = {"key": {"target": idx}}
    #    data_dict[bootstrap_idx] = {"key": {"target": random.random()}}

    #print(data_dict)
    #print(compute_median(data_dict, "key", "target"))

