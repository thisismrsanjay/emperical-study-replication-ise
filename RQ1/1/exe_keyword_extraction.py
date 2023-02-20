import sys
from collections import Counter

from Utils import util
sys.path.append("./../common")
import git_reader
import issue_db_reader

from KE import keyword_extraction

project_name_list = ["your project here"]

def main():
    for p_name in project_name_list:
        repodir = "./../../prepare_data/repository/{0}".format(p_name)
        db_path = "./../../prepare_data/extract_issues/db/{0}_issue_field_data.db".format(p_name)
        hash_list = git_reader.get_all_hash_without_merge(repodir)
        issue_id_list = issue_db_reader.read_issue_id_list(db_path)

        log_message_info_path = "./../../prepare_data/extract_issues/data_{0}/{1}_log_message_info.pickle".format(p_name.upper(), p_name)

        ins = keyword_extraction.KeywordExtraction()
        issue2hash_dict = ins.run(hash_list, issue_id_list, log_message_info_path)

        util.dump_pickle("./data/{0}_keyword_extraction.pickle".format(p_name), issue2hash_dict)


if __name__=="__main__":

    main()
