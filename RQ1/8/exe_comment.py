
from GS import comment
from Utils import util
import sqlite3
import glob
import re

import sys
sys.path.append("./../common")
import git_reader
import issue_db_reader
import common

project_name_list = ["your project here"]


def run():

    for p_name in project_name_list:

        repodir = "./../../prepare_data/repository/{0}".format(p_name)
        db_path = "./../../prepare_data/extract_issues/db/{0}_issue_field_data.db".format(p_name)
        hash_list = git_reader.get_all_hash_without_merge(repodir)
        issue_id_list = issue_db_reader.read_issue_id_list(db_path)

        dsc_issue_dict = common.extract_description(db_path)
        comment_issue_dict = common.extract_comment(db_path)

        """
        modified_file_repo_dict [dict<commit hash, list<modified files>>] -- modified files list for each commit hash
        repo_javadoc_dict [dict<commit_hash, javadocs (a string)>] -- all javadocs that were extracted
        """
        print("read javadoc")
        modified_file_repo_dict = common.extract_modified_file_repo(repodir, hash_list)
        repo_javadoc_dict = common.extract_javadoc(p_name, modified_file_repo_dict)

        cosine_sim_threshold = 0.4
        num_iteration = 1
        ins = comment.Comment(THRESHOLD_COSINE_SIM=cosine_sim_threshold, parallel_iteration=num_iteration)
        issue2hash_dict = ins.run(hash_list, issue_id_list, issue_id_list,
                            dsc_issue_dict, comment_issue_dict,
                            repo_javadoc_dict, "./pickle_{0}".format(p_name))

        util.dump_pickle("./data/{0}_comment_costh{1}_ite{2}.pickle".format(p_name, cosine_sim_threshold, num_iteration), issue2hash_dict)



if __name__=="__main__":


    run()
