import argparse
import sys

from Utils import util
sys.path.append("./../common")
import git_reader
import issue_db_reader

from PH import phantom

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
    hash_list = git_reader.get_all_hash_without_merge(repodir)
    issue_id_list = issue_db_reader.read_issue_id_list(db_path)

    log_message_info_path = \
        "./../../prepare_data/extract_issues/data_{0}/{1}_log_message_info.pickle".format(p_name.upper(), p_name)

    keyword_extraction_dict_path = \
        "./../deleted_data/{0}_keyword_extraction_{1}_{2}.pickle".format(p_name, delete_rate, bootstrap_idx)

    #phantom_obj = phantom.Phantom(TIME_INTERVAL_BEFORE=timedelta(days=3), TIME_INTERVAL_AFTER=timedelta(days=3), DUPLICATE_RATE=0.66, verbose=1)
    ins = phantom.Phantom(repo_dir=repodir, verbose=1, keyword_extraction_dict_path=keyword_extraction_dict_path,
                          delete_rate=delete_rate)
    issue2hash_dict = ins.run(hash_list, issue_id_list,
                          log_message_info_path)


    util.dump_pickle("./data/{0}_{1}_phantom_bi{2}.pickle".format(p_name, delete_rate, bootstrap_idx), issue2hash_dict)


if __name__=="__main__":

    main()
