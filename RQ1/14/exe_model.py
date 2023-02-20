
import argparse
import sys

from Utils import util
sys.path.append("./../common")
import git_reader
import issue_db_reader
import common

from ML import execute

#max_ite = None
max_ite = 10
max_iteration_TS = 25

def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--project', '-p', type=str, required=True,
                        help='project name')
    parser.add_argument('--model', '-m', type=str, required=True,
                        help='model name (RF, SVM)')
    parser.add_argument('--delete_rate', '-b', type=int, required=True,
                        help='delete rate')
    parser.add_argument('--bootstrap_idx', '-bi', type=int, required=True,
                        help='bootstrap index')
    args = parser.parse_args()
    p_name = args.project
    model_name = args.model
    delete_rate = args.delete_rate
    bootstrap_idx = args.bootstrap_idx

    repodir = "./../../prepare_data/repository/{0}".format(p_name)
    db_path = "./../../prepare_data/extract_issues/db/{0}_issue_field_data.db".format(p_name)

    print(p_name)
    issue_id_list = issue_db_reader.read_issue_id_list(db_path)

    hash_list = git_reader.get_all_hash_without_merge(repodir)

    keyword_extraction_dict_path = \
        "./../deleted_data/{0}_keyword_extraction_{1}_{2}.pickle".format(p_name, delete_rate, bootstrap_idx)

    ml_model_obj = execute.MLModel(repo_dir=repodir, db_path=db_path, model_name=model_name, random_state=200,
                                   verbose=1, keyword_extraction_dict_path=keyword_extraction_dict_path,
                                   delete_rate=delete_rate, max_iteration=max_iteration_TS)

    dsc_issue_dict = common.extract_description(db_path)
    comment_issue_dict = common.extract_comment(db_path)

    log_message_info_path = \
        "./../../prepare_data/extract_issues/data_{0}/{1}_log_message_info.pickle".format(p_name.upper(), p_name)
    log_message_without_issueid_path = \
        "./../../prepare_data/extract_issues/data_{0}/{1}_log_message_without_issueid.pickle".format(p_name.upper(), p_name)
    output_dir = "./../5/pickle_{0}".format(p_name)

    if max_ite is None:
        issue2hash_dict = ml_model_obj.run(hash_list, issue_id_list,
                              log_message_info_path, log_message_without_issueid_path,
                              dsc_issue_dict, comment_issue_dict, output_dir)

        util.dump_pickle("./data/{0}_{1}_{2}_model_bi{3}.pickle".format(p_name, model_name, delete_rate, bootstrap_idx), issue2hash_dict)
        if model_name=="RF":
            util.dump_pickle("./data/{0}_{1}_{2}_important_features_bi{3}.pickle".format(p_name, model_name, delete_rate, bootstrap_idx), ml_model_obj.extract_important_features())
    else:

        hash_list_dict = {}
        for num_ite in range(max_ite):
            if (num_ite+1) == max_ite:
                hash_list_dict[num_ite] = hash_list[num_ite*int(len(hash_list)/max_ite):]
            else:
                hash_list_dict[num_ite] = hash_list[num_ite*int(len(hash_list)/max_ite):(num_ite+1)*int(len(hash_list)/max_ite)]

        for num_ite in range(max_ite):
        #for num_ite in [0]:
            try:
                issue2hash_dict = ml_model_obj.run(hash_list_dict[num_ite], issue_id_list,
                                      log_message_info_path, log_message_without_issueid_path,
                                      dsc_issue_dict, comment_issue_dict, output_dir)
            except Exception:
                continue
            util.dump_pickle("./data/{0}_{1}_{2}_model_bi{3}_{4}.pickle".format(p_name, model_name, delete_rate, bootstrap_idx, num_ite), issue2hash_dict)

            if model_name=="RF":
                util.dump_pickle("./data/{0}_{1}_{2}_important_features_bi{3}_{4}.pickle".format(p_name, model_name, delete_rate, bootstrap_idx, num_ite), ml_model_obj.extract_important_features())



if __name__=="__main__":

    main()
