import sys
from collections import Counter
from datetime import datetime, timedelta
import sqlite3


from Utils import util
sys.path.append("./../common")
import git_reader
import issue_db_reader
import common

from TF import time_filtering

project_name_list = ["your project here"]


def main():
    for p_name in project_name_list:
        repodir = "./../../prepare_data/repository/{0}".format(p_name)
        db_path = "./../../prepare_data/extract_issues/db/{0}_issue_field_data.db".format(p_name)
        hash_list = git_reader.get_all_hash_without_merge(repodir)

        log_message_info_path = "./../../prepare_data/extract_issues/data_{0}/{1}_log_message_info.pickle".format(p_name.upper(), p_name)
        issue_id_list = issue_db_reader.read_issue_id_list(db_path)
        date_issue_dict = common.extract_dates(db_path)

        for time_interval_after in [5, 10, 30, 60, 120]:

            ins = time_filtering.TimeFiltering(TIME_INTERVAL_AFTER=timedelta(minutes=time_interval_after))
            data = ins.run(hash_list, issue_id_list, date_issue_dict, log_message_info_path)

            util.dump_pickle("./data/{0}_time_filtering_min_af{1}.pickle".format(p_name, time_interval_after), data)

if __name__=="__main__":

    #delta = timedelta(minutes=5)
    #print(delta)

    main()
