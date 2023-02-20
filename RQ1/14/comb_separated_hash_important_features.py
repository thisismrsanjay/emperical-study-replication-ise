import sys

from Utils import util
import pandas as pd

project_name_list = ["project name here"]
ml_model_list = ["RF"]
max_iteration = 10
#delete_rate_list=[0, 10, 20, 30, 40, 50]
delete_rate_list=[0, 50]
bootstrap_sample_iteration=100

# pro_modified_file: proprtion of modified Java files among all modified files in a commit
# num_modified_file: number of modified Java files in a commit
# time_diff: time difference between commit and issue
# ntext: cosine similarity between commit message and description + comment in an issue that are transformed into TFIDF features
# time_diff_type_binary: 0 or 1 binary. Whether issue resolved date is before commit date
# dev_binary: 0 or 1 binary. Whether issue author and committer is same
column_index = ["pro_modified_file", "num_modified_file", "time_diff", "ntext", "time_diff_type_binary"]
display_index = ["\\% Modified Files", "\\# Modified Files", "Time Difference", "\\TSFUL{}", "Time Difference Type"]

def make_table(p_name, m_name, delete_rate, dat):
    TABLE = []
    for title, num in zip(display_index, dat.median(axis=0)):
        TABLE.append([title, '%03.3f\\\\' % round(num, 3)])

    column_index = ["Feature", "Importance\\\\"]
    TABLE = pd.DataFrame(TABLE,columns=column_index)
    TABLE.to_csv(path_or_buf='./tables/importance_{0}_{1}_{2}.csv'.format(p_name, m_name, delete_rate), index=False, sep="&")


def main():
    for delete_rate in delete_rate_list:
        all_result_list = []
        for p_name in project_name_list:

            for m_name in ml_model_list:

                for bootstrap_idx in range(bootstrap_sample_iteration):
                    result_list = []
                    for num_ite in range(max_iteration):
                        temp_list = list(util.load_pickle("data/{0}_{1}_{2}_important_features_bi{3}_{4}.pickle".format(p_name, m_name, delete_rate, bootstrap_idx, num_ite)))
                        result_list.append(temp_list)
                        all_result_list.append(temp_list)

                    util.dump_pickle("./feature_importance_RF/{0}_{1}_{2}_important_features_bi{3}.pickle".format(p_name, m_name, delete_rate, bootstrap_idx), result_list)

        dat = pd.DataFrame(all_result_list, columns=column_index)
        #print(dat)
        print("delete rate: {0}".format(delete_rate))
        print("Median")
        print(dat.median(axis=0))
        print("Mean")
        print(dat.mean(axis=0))
        print("")

        make_table(p_name, m_name, delete_rate, dat)



if __name__=="__main__":

    main()
