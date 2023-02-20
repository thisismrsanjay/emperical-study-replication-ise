from sklearn.metrics import roc_auc_score
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import matthews_corrcoef
from sklearn.metrics import brier_score_loss
from sklearn.metrics import auc

import numpy as np
import sys

def calAUC(prob,train_target):

    try:
        AUC = roc_auc_score(train_target,prob)
    except ValueError:
        AUC = 0.5
    #return AUC,0,0,0
    return AUC

def evaluations_SVL(prob,train_target):

    y_pred = []
    for i in prob:
        if i>=0.5:
            y_pred.append(1)
        else:
            y_pred.append(0)

    F1 = f1_score(train_target,y_pred)
    precision = precision_score(train_target,y_pred)
    recall = recall_score(train_target,y_pred)
    MCC = matthews_corrcoef(train_target,y_pred)

    try:
        AUC = roc_auc_score(train_target,prob)
    except ValueError:
        AUC = 0.5
    brier_score = brier_score_loss(train_target,prob)

    return AUC,F1,precision,recall,MCC,brier_score




class EffortAwareEvaluation:

    def __init__(self, prob_list, label_list, line_list):
        """
        prob_list: the predicted probabilities for each commit
        label_list: 0 or 1 to indicate clean commit or defective commit
        line_list: the number of changed lines for each commit
        """
        self.prob_list = np.array(prob_list)
        self.label_list = np.array(label_list)
        self.line_list = np.array(line_list)
        self.all_commits = len(label_list)
        self.defective_commits = 0
        for num in label_list:
            if num!=0:
                self.defective_commits += 1

        sorted_prob_index = np.argsort(-self.prob_list)
        self.line_sorted_prob = self.line_list[sorted_prob_index]
        self.label_sorted_prob = self.label_list[sorted_prob_index]
    
    def IFA(self):
        result = 0
        for label in self.label_sorted_prob:
            if label==0:
                result += 1
            else:
                break
        
        return result

    def PII(self, L, prob=None):
        """
        L: number of lines or the percentage (%) of lines in the total lines
        Prob: This is a flag whether L is a percentage or number of lines
        """
        if not prob is None:
            L = int(0.01*L*sum(self.line_list))
        
        m = 0
        sum_line = 0
        for line in self.line_sorted_prob:
            sum_line += line
            if sum_line > L:
                break
            m += 1
        
        return m/self.all_commits
    
    def CostEffort(self, L, prob=None):
        """
        L: number of lines or the percentage (%) of lines in the total lines
        Prob: This is a flag whether L is a percentage or number of lines
        """
        if not prob is None:
            L = int(0.01*L*sum(self.line_list))
        
        n = 0
        sum_line = 0
        for line, label in zip(self.line_sorted_prob, self.label_sorted_prob):
            sum_line += line

            if sum_line > L:
                break

            if label!=0:
                n += 1
        
        return n/self.defective_commits

    def _compute_auc(self, target_line_list, target_label_list, L):
        x = [0]
        y = [0]
        total_line = sum(self.line_list)
        tmp_line = 0
        tmp_commits = 0
        L = 0.01 * L
        for line, label in zip(target_line_list, target_label_list):
            tmp_line += line
            if label!=0:
                tmp_commits += 1
            if (tmp_line/total_line) > L:
                break
            x.append(tmp_line/total_line)
            y.append(tmp_commits/self.defective_commits)

        if not L < 1.0:
            assert x[-1]==1.0, "x is not correct"
            assert y[-1]==1.0, "y is not correct"
        else:
            if x[-1] < L:
                x.append(L)
                y.append(y[-1])
            
            assert x[-1]==L, "The final one is not correct"

        return auc(x, y)
    
    def norm_popt(self, L=100):

        defective_line = []
        clean_line = []
        for line, label in zip(self.line_sorted_prob, self.label_sorted_prob):
            if label==0:
                clean_line.append(line)
            else:
                defective_line.append(line)

        max_auc = self._compute_auc(sorted(defective_line) + clean_line, ([1] * len(defective_line)) + ([0] * len(clean_line)), L)
        min_auc = self._compute_auc(clean_line + sorted(defective_line, reverse=True), ([0] * len(clean_line)) + ([1] * len(defective_line)), L)
        predict_auc = self._compute_auc(self.line_sorted_prob, self.label_sorted_prob, L)

        #print('mac auc')
        #print(max_auc)
        #print('min auc')
        #print(min_auc)
        #print('predict auc')
        #print(predict_auc)

        const = 0.01*L
        popt = const - (max_auc - predict_auc)
        min_popt = const - (max_auc - min_auc)

        if min_popt==1:
            return None

        assert (popt - min_popt)/(const - min_popt) <= 1.0, "Invalid norm Popt value"

        return (popt - min_popt)/(const - min_popt)

        #popt = 0.01*L*1 - (max_auc - predict_auc)
        #min_popt = 0.01*L*1 - (max_auc - min_auc)
        #return (popt - min_popt)/(0.01*L*1 - min_popt)


