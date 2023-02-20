import time
from sklearn.model_selection import RandomizedSearchCV
from sklearn import linear_model as lm
from sklearn.ensemble import RandomForestClassifier as rf

import sys


class Train():
    def __init__(self, train_data, train_labels, test_data, test_labels):
        self.train_data = train_data
        self.train_labels = train_labels
        self.test_data = test_data
        self.test_labels = test_labels


    def run(self, parameters, m_name):

        #print('# of train:', len(self.train_labels), '# of test:', len(self.test_labels))

        start_time = time.time()
        best_estimaters, best_scores = [], []

        if m_name=="LR":
            clf = RandomizedSearchCV(lm.LogisticRegression(), parameters, n_iter=50, scoring='f1', n_jobs=-1)
            #clf = RandomizedSearchCV(lm.LogisticRegression(), parameters, n_iter=50, scoring='f1', n_jobs=10)
        elif m_name=="RF":
            clf = RandomizedSearchCV(rf(), parameters, n_iter=50, scoring='f1', n_jobs=-1)
            #clf = RandomizedSearchCV(rf(), parameters, n_iter=50, scoring='f1', n_jobs=10)
        clf = clf.fit(self.train_data, self.train_labels)
        #print('Best parameters:\n', clf.best_params_)

        train_time = time.time() - start_time
        #print('Train time:', train_time, '(s)')


        test_start_time = time.time()
        probs = list(clf.predict_proba(self.test_data))
        fault_probs = [prob[1] for prob in probs]

        test_time = time.time() - test_start_time

        evaluation_dict = {'Time': [train_time],'test_Time': [test_time]}
        prob_dict = {'Prob': fault_probs, 'Label': self.test_labels, 'BestPara': clf.best_params_}

        return evaluation_dict, prob_dict

