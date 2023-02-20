
import argparse
import sys

from Utils import util
sys.path.append("./../common")
import git_reader
import issue_db_reader
import common

from PU import pu_link


#max_ite = None
max_ite = 10
max_iteration_TS = 25

def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--project', '-p', type=str, required=True,
                        help='project name')
    parser.add_argument('--delete_rate', '-b', type=int, required=True,
                        help='delete rate')
    parser.add_argument('--bootstrap_idx', '-bi', type=int, required=True,
                        help='bootstrap index')
    args = parser.parse_args()
    p_name = args.project
    delete_rate = args.delete_rate
    bootstrap_idx = args.bootstrap_idx

    repodir = "./../../prepare_data/repository/{0}".format(p_name)
    db_path = "./../../prepare_data/extract_issues/db/{0}_issue_field_data.db".format(p_name)

    print(p_name)
    issue_id_list = issue_db_reader.read_issue_id_list(db_path)

    hash_list = git_reader.get_all_hash_without_merge(repodir)

    keyword_extraction_dict_path = \
        "./../deleted_data/{0}_keyword_extraction_{1}_{2}.pickle".format(p_name, delete_rate, bootstrap_idx)

    pu_link_obj = pu_link.PULink(repo_dir=repodir, db_path=db_path, random_state=200, verbose=1,
                                 keyword_extraction_dict_path=keyword_extraction_dict_path,
                                 delete_rate=delete_rate, max_iteration=max_iteration_TS)

    dsc_issue_dict = common.extract_description(db_path)
    comment_issue_dict = common.extract_comment(db_path)

    log_message_info_path = \
        "./../../prepare_data/extract_issues/data_{0}/{1}_log_message_info.pickle".format(p_name.upper(), p_name)
    log_message_without_issueid_path = \
        "./../../prepare_data/extract_issues/data_{0}/{1}_log_message_without_issueid.pickle".format(p_name.upper(), p_name)

    output_dir = "./../5/pickle_{0}".format(p_name)

    if max_ite is None:
        issue2hash_dict = pu_link_obj.run(hash_list, issue_id_list,
                                          log_message_info_path, log_message_without_issueid_path,
                                          dsc_issue_dict, comment_issue_dict, output_dir)
        util.dump_pickle("./data/{0}_{1}_pu_link_bi{2}.pickle".format(p_name, delete_rate, bootstrap_idx), issue2hash_dict)
    else:
        hash_list_dict = {}
        for num_ite in range(max_ite):
            if (num_ite+1) == max_ite:
                hash_list_dict[num_ite] = hash_list[num_ite*int(len(hash_list)/max_ite):]
            else:
                hash_list_dict[num_ite] = hash_list[num_ite*int(len(hash_list)/max_ite):(num_ite+1)*int(len(hash_list)/max_ite)]



        for num_ite in range(max_ite):
        #for num_ite in [0]:

            issue2hash_dict = pu_link_obj.run(hash_list_dict[num_ite], issue_id_list,
                                              log_message_info_path, log_message_without_issueid_path,
                                              dsc_issue_dict, comment_issue_dict, output_dir)
            util.dump_pickle("./data/{0}_{1}_pu_link_bi{2}_{3}.pickle".format(p_name, delete_rate, bootstrap_idx, num_ite), issue2hash_dict)
        #issue2hash_dict = pu_link_obj.run(p_name, hash_list_2, issue_id_list)
        #util.dump_pickle("./data/{0}_pu_link_2.pickle".format(p_name), issue2hash_dict)




if __name__=="__main__":

    main()
