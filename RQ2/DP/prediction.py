import csv
import datetime
import os
import sqlite3
import time
import numpy as np
from collections import Counter

from Utils import util
from scipy.stats import uniform

from TimeFlowDataValidation import time_flow_data_validation
from TimeFlowDataValidation import initializer

import preparation
import model
import evaluation

import sys
import argparse

import warnings
warnings.simplefilter('ignore')
os.environ["PYTHONWARNINGS"] = "ignore"


modelName = ['LR']

parameters = {"LR": {"C": uniform(loc=0,scale=10), "penalty": ["l2", "l1"]}}
START_GAP = 30

def read_change_metrics_context(db_path):
    """Extract snippet data from database"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    command = """SELECT commit_hash,fix,ns,nd,nf,entrophy,la,ld,lt,ndev,age,nuc,exp,rexp,sexp
                 FROM data
                 ORDER BY id;"""
    cur.execute(command)

    metrics = {}
    for row in cur.fetchall():
        temp_change_metrics = []
        for cnt, value in enumerate(row[1:]):
            try:
                temp_change_metrics.append(float(value))
            except ValueError:
                if value=='False':
                    temp_change_metrics.append(0)
                elif value=='True':
                    temp_change_metrics.append(1)
                elif cnt == 0:
                    temp_change_metrics.append(0)
                else:
                    sys.exit()
        metrics[row[0]] = temp_change_metrics

    conn.close()

    return metrics

def extract_change_metrics(p_name):

    change_metrics = read_change_metrics_context("./../commitguru_data/{0}.db".format(p_name))
    return change_metrics



def extract_metrics(data):

    metrics = ['fix','ns','nd','nf','entropy','la','ld','lt','ndev','age','nuc','exp','rexp','sexp']

    fix_index = metrics.index('fix')
    NS_index = metrics.index('ns')
    NF_index = metrics.index('nf')
    Entropy_index = metrics.index('entropy')
    NDEV_index = metrics.index('ndev')
    AGE_index = metrics.index('age')
    EXP_index = metrics.index('exp')
    SEXP_index = metrics.index('sexp')


    LA_index = metrics.index('la')
    LT_index = metrics.index('lt')
    LD_index = metrics.index('ld')
    NUC_index = metrics.index('nuc')

    FIX = []
    DATA = []

    for row in data:

        FIX.append([row[fix_index]])

        DATA.append([row[NS_index],row[NF_index],row[Entropy_index],row[NDEV_index],row[AGE_index],row[EXP_index],row[SEXP_index]])

        #print(row[LT_index])
        try:
            DATA[-1].extend([row[LA_index]/row[LT_index]])
            DATA[-1].extend([row[LD_index]/row[LT_index]])
        except ZeroDivisionError:
            DATA[-1].extend([row[LA_index]])
            DATA[-1].extend([row[LD_index]])

        #print(row[NF_index])
        try:
            DATA[-1].extend([row[LT_index]/row[NF_index]])
            DATA[-1].extend([row[NUC_index]/row[NF_index]])
        except ZeroDivisionError:
            DATA[-1].extend([row[LT_index]])
            DATA[-1].extend([row[NUC_index]])


    #print(DATA)

    return DATA, FIX

def integrate(DATA,FIX):

    temp = []
    for data, fix in zip(DATA,FIX):

        temp.append(list(data))
        temp[-1].extend(list(fix))


    return np.array(temp)

def initialize_dictionary():

    result_dict = {}

    for m_name in modelName:

        result_dict[m_name] = {'AUC':[],'F1':[],'Pre':[],'Rec':[],'MCC':[],'brier_score':[],'Prob':[],'Label':[],'test_commits': []}

    return result_dict


def smote_tuned(train_data, train_label):
    #####################
    #####################
    #####################
    # SMOTUNED script should be here
    #####################
    #####################
    #####################
    return train_data, train_label

def cal_10_fold_CV(projectName, ila_list, delete_rate_list, BOOTSTRAP_IDX):

    if os.path.exists("./pickle/bi{0}/test_label_zero_{1}_{2}_{3}.pickle".format(BOOTSTRAP_IDX, projectName[0], ila_list[0], delete_rate_list[0])):
        os.remove("./pickle/bi{0}/test_label_zero_{1}_{2}_{3}.pickle".format(BOOTSTRAP_IDX, projectName[0], ila_list[0], delete_rate_list[0]))
    if os.path.exists("./pickle/bi{0}/balance_error_{1}_{2}_{3}.pickle".format(BOOTSTRAP_IDX, projectName[0], ila_list[0], delete_rate_list[0])):
        os.remove("./pickle/bi{0}/balance_error_{1}_{2}_{3}.pickle".format(BOOTSTRAP_IDX, projectName[0], ila_list[0], delete_rate_list[0]))

    for bootstrap_idx in range(BOOTSTRAP_IDX, BOOTSTRAP_IDX+1):
        bootstrap_start_time = time.time()
        print("bootstrap idx: {0}".format(bootstrap_idx))

        for delete_rate in delete_rate_list:
            print("delete rate: {0}".format(delete_rate))

            for ILA_num in ila_list:
                print("ILA: {0}".format(ILA_num))

                for p_name in projectName:
                    project_start_time = time.time()
                    print("project: {0}".format(p_name))

                    log_file_name = './log/{0}_{1}_delete{2}_bi{3}.txt'.format(p_name, ILA_num, delete_rate, bootstrap_idx)
                    try:
                        os.remove(log_file_name)
                    except FileNotFoundError:
                        pass

                    db_path_cv = "./../CLA/db/delete0/{0}_1.db".format(p_name) # cv fold
                    db_path = "./../CLA/db/delete{0}/{1}_{2}.db".format(delete_rate, p_name, ILA_num) # cv fold


                    author_date_pickle_path = "./data/gap_para_author_date_{0}_without_merge.pickle".format(p_name)


                    # read metrics (dict<commit hash, metrics>)
                    change_metrics_dict = extract_change_metrics(p_name)

                    merge_commits = util.load_pickle("./data/{0}_merge.pickle".format(p_name))
                    first_author_date, median_defect_fixing_interval = \
                            initializer.return_initial_parameters(db_path_cv, p_name, author_date_pickle_path, bootstrap_idx, merge_commits)


                    first_author_date = first_author_date + datetime.timedelta(days=START_GAP)
                    start_day = datetime.datetime(year=first_author_date.year,month=first_author_date.month,day=first_author_date.day)
                    median_defect_fixing_interval = datetime.timedelta(days=median_defect_fixing_interval)

                    train_data, train_label, test_data, test_label, time_keeper, \
                    author_date, defect_fixing_commits, training_period, test_commits \
                        = time_flow_data_validation.separate_dict(db_path=db_path, author_date_pickle_path=author_date_pickle_path, dict_data=change_metrics_dict,
                                                                    start_day=start_day, gap_days=median_defect_fixing_interval, bootstrap_idx=bootstrap_idx)

                    result_dict = initialize_dictionary()
                    best_parameter_dict_list = []
                    number_of_test_data = []
                    number_of_positive_test_data = []

                    for ite in range(training_period):
                    #for ite in range(2):

                        #if len(train_label)==0 or sum(train_label)==0 or len(test_label)==0 or sum(test_label)==0:
                        if len(test_label)==0:
                            # updating training data.
                            train_data, train_label, test_data, test_label, test_commits \
                                = time_flow_data_validation.separate_dict_update(db_path, time_keeper,
                                                                    author_date, defect_fixing_commits,
                                                                    change_metrics_dict, bootstrap_idx)
                            continue

                        train_data, train_FIX = extract_metrics(train_data)
                        test_data, test_FIX = extract_metrics(test_data)

                        train_data, test_data = preparation.standardization_SVL(train_data,test_data,"z-score")

                        train_data = integrate(train_data,train_FIX)
                        test_data = integrate(test_data,test_FIX)

                        print('Original dataset shape %s' % Counter(train_label))

                        train_data, train_label = smote_tuned(train_data, train_label)

                        print('Resampled dataset shape %s' % Counter(train_label))

                        number_of_test_data.append(len(test_label))
                        number_of_positive_test_data.append(sum(test_label))

                        Trainer = model.Train(train_data, train_label, test_data, test_label)
                        evaluation_dict, prob_dict = Trainer.run(parameters[modelName[0]], modelName[0])

                        prob_RF = prob_dict['Prob']
                        best_parameter_dict = prob_dict['BestPara']
                        best_parameter_dict_list.append(best_parameter_dict)

                        temp = [prob_RF]

                        for m_name,prob in zip(modelName,temp):

                            # In CMake, AUC cannot be computed in two commits where all commits are clean.
                            # This try sentence is for these two commits.
                            try:
                                auc, f1, precision, recall, MCC, brier_score = evaluation.evaluations_SVL(prob, test_label)
                            except ValueError:
                                f = open(log_file_name,'a')
                                csvWriter = csv.writer(f)
                                csvWriter.writerow(['ValueError: iteration is {0}, model is {1}'.format(ite,m_name)])
                                f.close()

                            print(auc)
                            result_dict[m_name]['AUC'].append(auc)
                            result_dict[m_name]['F1'].append(f1)
                            result_dict[m_name]['Pre'].append(precision)
                            result_dict[m_name]['Rec'].append(recall)
                            result_dict[m_name]['MCC'].append(MCC)
                            result_dict[m_name]['brier_score'].append(brier_score)
                            result_dict[m_name]['Prob'].append(prob)
                            result_dict[m_name]['Label'].append(test_label)
                            result_dict[m_name]['test_commits'].append(test_commits)


                        train_data, train_label, test_data, test_label, test_commits \
                            = time_flow_data_validation.separate_dict_update(db_path, time_keeper,
                                                                            author_date, defect_fixing_commits,
                                                                            change_metrics_dict, bootstrap_idx)


                    for m_name in modelName:

                        ALL = [result_dict[m_name]['AUC'],result_dict[m_name]['F1'],result_dict[m_name]['Pre'],result_dict[m_name]['Rec'],result_dict[m_name]['MCC'],result_dict[m_name]['brier_score']]
                        with open('./results/delete{0}/bi{1}/{2}_{3}_{4}.csv'.format(
                                delete_rate, bootstrap_idx, p_name, m_name, ILA_num),'w') as f:
                            csvWriter = csv.writer(f)

                            for metrics in ALL:
                                csvWriter.writerow(metrics)


                        with open('./results/delete{0}/bi{1}/prob_{2}_{3}_{4}.csv'.format(
                                delete_rate, bootstrap_idx, p_name,m_name,ILA_num),'w') as f:
                            csvWriter = csv.writer(f)
                            for row in result_dict[m_name]['Prob']:
                                csvWriter.writerow(row)


                        with open('./results/delete{0}/bi{1}/label_{2}_{3}_{4}.csv'.format(
                                delete_rate, bootstrap_idx, p_name,m_name,ILA_num),'w') as f:
                            csvWriter = csv.writer(f)
                            for row in result_dict[m_name]['Label']:
                                csvWriter.writerow(row)

                        util.dump_pickle('./results/delete{0}/bi{1}/test_commits_{2}_{3}_{4}.pickle'.format(
                                delete_rate, bootstrap_idx, p_name,m_name,ILA_num),
                                result_dict[m_name]['test_commits']
                        )


                        with open('./results/delete{0}/bi{1}/best_parameters_{2}_{3}_{4}.csv'.format(
                                delete_rate, bootstrap_idx, p_name,m_name,ILA_num),'w') as f:
                            csvWriter = csv.writer(f)
                            for best_parameter_dict in best_parameter_dict_list:
                                key_list = sorted(best_parameter_dict.keys())
                                csvWriter.writerow(["{0}: {1}".format(row, best_parameter_dict[row]) for row in key_list])


                        with open('./results/delete{0}/bi{1}/number_of_test_data_{2}_{3}_{4}.csv'.format(
                                delete_rate, bootstrap_idx, p_name,m_name,ILA_num),'w') as f:
                            csvWriter = csv.writer(f)
                            for row1, row2 in zip(number_of_test_data, number_of_positive_test_data):
                                csvWriter.writerow([row1, row2])

                    project_end_time = time.time()
                    print("=======================")
                    print("project time: {0} [sec]".format(project_end_time - project_start_time))
                    print("=======================")

                    with open('./results/delete{0}/bi{1}/project_time_{2}_{3}.csv'.format(
                            delete_rate, bootstrap_idx, p_name, ILA_num),'w') as f:
                        csvWriter = csv.writer(f)
                        csvWriter.writerow(["project time: {0} [sec]".format(project_end_time - project_start_time)])
        bootstrap_end_time = time.time()
        print("=======================")
        print("bootstrap time: {0} [sec]".format(bootstrap_end_time - bootstrap_start_time))
        print("=======================")

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--project', '-p', type=str, required=True,
                        help='project name separated by ,')
    parser.add_argument('--ila', '-i', type=str, required=True,
                        help='ILA list separated by ;')
    parser.add_argument('--deleterate', '-br', type=str, required=True,
                        help='delete rate list separated by ,')
    parser.add_argument('--bootstrap', '-b', type=int, required=True,
                        help='bootstrap idx (0~99)')
    args = parser.parse_args()
    projectName = args.project.split(",")
    ila_list = args.ila.split(";")
    delete_rate_list = args.deleterate.split(",")
    BOOTSTRAP_IDX = args.bootstrap

    cal_10_fold_CV(projectName, ila_list, delete_rate_list, BOOTSTRAP_IDX)
