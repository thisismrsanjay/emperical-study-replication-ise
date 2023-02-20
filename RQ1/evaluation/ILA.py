import sys

from Utils import util

sys.path.append("./../random_delete")
import time_restriction


project_name_list = ["project name here"]

BOOTSTRAP_SIZE = 100
TIME_FILTERING_MIN = 10
NTEXT_TH = 3
WORD_ASSOC_TH = 5
COMMENT_COS_TH = 4
NSD_SIM_COS_TH = 2

def _compare_org_new(org_dict, new_dict):
    print("===")
    print("num issue ids -- no restriction: {0:,}, with restriction: {1:,}, diff: {2:,} ({3}%)".format(len(org_dict), len(new_dict), len(org_dict) - len(new_dict), 100*round((len(org_dict)-len(new_dict))/len(org_dict), 3)))

    org_commit_set = set()
    new_commit_set = set()
    for issue_id in org_dict.keys():
        org_commit_set = org_commit_set | set(org_dict[issue_id])

    for issue_id in new_dict.keys():
        new_commit_set = new_commit_set | set(new_dict[issue_id])

    print("num commit hashes -- no restriction: {0:,}, with restriction: {1:,}, diff: {2:,} ({3}%)".format(len(org_commit_set), len(new_commit_set), len(org_commit_set) - len(new_commit_set), 100*round((len(org_commit_set)-len(new_commit_set))/len(org_commit_set), 3)))



def add_restrictions(p_name, ILA_dict):
    for issue_dir in ILA_dict.keys():

        if issue_dir=="9_1" or issue_dir=="9_2":
            temp_dir = "9"
        elif issue_dir=="14_1" or issue_dir=="14_2":
            temp_dir = "14"
        else:
            temp_dir = issue_dir

        exp40_ILA_set = set(["7", "9", "11", "14"])

        if temp_dir=="1":
            data_dict = util.load_pickle("./../deleted_data/{0}.pickle".format(ILA_dict[issue_dir]))
        elif temp_dir in exp40_ILA_set:
            print("{0}, {1}".format(temp_dir, issue_dir))
            data_dict = util.load_pickle("./../{0}/data/{1}.pickle".format(temp_dir, ILA_dict[issue_dir]))
        else:
            data_dict = util.load_pickle("./../{0}/data/{1}.pickle".format(temp_dir, ILA_dict[issue_dir]))
        util.dump_pickle("./data/{0}.pickle".format(ILA_dict[issue_dir]), data_dict)

        TimeRestriction = time_restriction.TimeRestriction(LINK_DATA_PATH="./data/{0}.pickle".format(ILA_dict[issue_dir]), verbose=1)
        issue2hash_dict = TimeRestriction.run(p_name)

        util.dump_pickle("./data/{0}_with_restriction.pickle".format(ILA_dict[issue_dir]), issue2hash_dict)


def compare_org_new(p_name, ILA_dict):
    for issue_dir in ILA_dict.keys():
        print(ILA_dict[issue_dir])

        org_dict = util.load_pickle("./data/{0}.pickle".format(ILA_dict[issue_dir]))
        new_dict = util.load_pickle("./data/{0}_with_restriction.pickle".format(ILA_dict[issue_dir]))

        _compare_org_new(org_dict, new_dict)

        print("===")



def main():
    for p_name in project_name_list:
        print("===========")
        print(p_name)


        #############################################3
        #############################################3
        #############################################3
        deleted_rate_list = [10, 20, 30, 40, 50]
        for delete_rate in deleted_rate_list:
            print("delete rate: {0}".format(delete_rate))

            #ILA_dict = {"8": "{0}_comment_costh{1}".format(p_name, COMMENT_COS_TH),
            ILA_dict = {"8": "{0}_comment_costh0.{1}_ite1".format(p_name, COMMENT_COS_TH),
                        "10": "{0}_nsd_similarity_costh{1}".format(p_name, NSD_SIM_COS_TH)}


            add_restrictions(p_name, ILA_dict)
            #compare_org_new(p_name, ILA_dict)

        for bootstrap_idx in range(BOOTSTRAP_SIZE):

            for delete_rate in deleted_rate_list:
                print("delete rate: {0}".format(delete_rate))

                ILA_dict = {"7": "{0}_{1}_word_association_th{2}_bi{3}".format(p_name, delete_rate, WORD_ASSOC_TH, bootstrap_idx),
                            "11": "{0}_{1}_pu_link_bi{2}".format(p_name, delete_rate, bootstrap_idx)}

                add_restrictions(p_name, ILA_dict)
                #compare_org_new(p_name, ILA_dict)



        #############################################3
        #############################################3
        #############################################3
        deleted_rate_list = [0, 10, 20, 30, 40, 50]
        for delete_rate in deleted_rate_list:
            print("delete rate: {0}".format(delete_rate))

            ILA_dict = {"3": "{0}_time_filtering_min_af{1}".format(p_name, TIME_FILTERING_MIN),
                        "5": "{0}_ntext_similarity_costh{1}".format(p_name, NTEXT_TH)}


            add_restrictions(p_name, ILA_dict)
            #compare_org_new(p_name, ILA_dict)

        for bootstrap_idx in range(BOOTSTRAP_SIZE):
            for delete_rate in deleted_rate_list:
                print("delete rate: {0}".format(delete_rate))

                ILA_dict = {"1": "{0}_keyword_extraction_{1}_{2}".format(p_name, delete_rate, bootstrap_idx),
                            "9_1": "{0}_{1}_loner_bi{2}".format(p_name, delete_rate, bootstrap_idx),
                            "9_2": "{0}_{1}_phantom_bi{2}".format(p_name, delete_rate, bootstrap_idx),
                            "14_1": "{0}_RF_{1}_model_bi{2}".format(p_name, delete_rate, bootstrap_idx),
                            "14_2": "{0}_SVM_{1}_model_bi{2}".format(p_name, delete_rate, bootstrap_idx)}


                add_restrictions(p_name, ILA_dict)
                #compare_org_new(p_name, ILA_dict)

if __name__=="__main__":

    main()
