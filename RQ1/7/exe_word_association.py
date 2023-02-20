
import argparse
import sys

from Utils import util
sys.path.append("./../common")
import git_reader
import issue_db_reader

from WA import word_association


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--project', '-p', type=str, required=True,
                        help='project name')
    parser.add_argument('--assoc_threshold', '-t', type=int, required=True,
                        help='project name')
    parser.add_argument('--delete_rate', '-b', type=int, required=True,
                        help='delete rate')
    parser.add_argument('--bootstrap_idx', '-bi', type=int, required=True,
                        help='bootstrap index')
    args = parser.parse_args()
    p_name = args.project
    assoc_threshold = args.assoc_threshold
    delete_rate = args.delete_rate
    bootstrap_idx = args.bootstrap_idx

    repodir = "./../../prepare_data/repository/{0}".format(p_name)
    db_path = "./../../prepare_data/extract_issues/db/{0}_issue_field_data.db".format(p_name)

    print(p_name)

    issue_id_list = issue_db_reader.read_issue_id_list(db_path)
    hash_list = git_reader.get_all_hash_without_merge(repodir)

    #for assoc_threshold in [1]:
    #for assoc_threshold in [1, 2, 3, 8, 9, 95]:

    log_message_info_path = \
        "./../../prepare_data/extract_issues/data_{0}/{1}_log_message_info.pickle".format(p_name.upper(), p_name)
    keyword_extraction_dict_path = \
        "./../deleted_data/{0}_keyword_extraction_{1}_{2}.pickle".format(p_name, delete_rate, bootstrap_idx)
    output_dir = "./../7/params/bi{0}_{1}".format(bootstrap_idx, p_name)
    lscp_processed_data_pickle_path = "./pickle_{0}".format(p_name)

    print("assoc threshold: {0}".format(assoc_threshold/10))
    word_association_obj = word_association.WordAssociation(ASSOC_THRESHOLD=assoc_threshold/10, verbose=1,
            max_iteration=25, keyword_extraction_dict_path=keyword_extraction_dict_path, delete_rate=delete_rate)

    issue2hash_dict = word_association_obj.run(hash_list, issue_id_list, log_message_info_path,
                                               lscp_processed_data_pickle_path, output_dir)
    util.dump_pickle("./data/{0}_{1}_word_association_th{2}_bi{3}.pickle".format(p_name, delete_rate,
                     assoc_threshold, bootstrap_idx), issue2hash_dict)



if __name__=="__main__":

    main()
