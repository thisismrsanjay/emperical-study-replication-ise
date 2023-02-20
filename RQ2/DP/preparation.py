import numpy as np
from sklearn import preprocessing
import sys


def standardization_SVL(train_data, test_data, scale_name):


    if scale_name == "0-1scale":
        min_max_scaler = preprocessing.MinMaxScaler()
        train_data_std = min_max_scaler.fit_transform(train_data)
        test_data_std = min_max_scaler.fit_transform(test_data)

    elif scale_name == "z-score":
        sc = preprocessing.StandardScaler()
        sc.fit(train_data)
        train_data_std = sc.transform(train_data)
        test_data_std = sc.transform(test_data)

    else:
        print("ERROR:preprocessing")
        sys.exit()


    return train_data_std,test_data_std



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

    LA = []
    LD = []
    LT = []
    NUC = []
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


def data_preparation(train_data, test_data):
    """
    Normalized train data and test data, and
    separate training data into training data and validation data.
    In addition prepare the test_flag list

    Arguments:
    train_data, test_data [List<List<change metrics (int and string)>>] -- training data comes from dict_data
    train_label [List<0 or 1>] -- the commit is buggy (1) or not (0)

    Returns:
    train_data, valid_data, test_data [np.array<np.array<change metrics>>] -- train/valid/test data
    train_label, valid_label [List<0 or 1>] -- the commit is buggy (1) or not (0)
    test_flag [List<integer>] -- a list which indicates the index where are already analyzed (if it is equal to 1)
    """

    train_data, train_FIX = extract_metrics(train_data)
    test_data, test_FIX = extract_metrics(test_data)

    train_data, test_data = standardization_SVL(train_data,test_data,"z-score")

    train_data = integrate(train_data,train_FIX)
    test_data = integrate(test_data,test_FIX)


    return train_data, test_data
