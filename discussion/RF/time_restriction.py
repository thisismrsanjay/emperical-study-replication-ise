import re
from datetime import datetime, timedelta
import sqlite3
import sys
from Utils import util


class TimeRestriction:
    def __init__(self, LINK_DATA_PATH="./data/keyword_extraction.pickle", verbose=0):

        self.link_data_path = LINK_DATA_PATH
        self.verbose = verbose

    def extract_datetime_from_string(self, target):
        return datetime.strptime(target, "%Y-%m-%dT%H:%M:%S.%f%z")

    def extract_dates(self, db_path):
        """
        extract created, updated and resolutiondate for each issue id.

        Arguments:
        dp_path [string] -- database path

        Returns:
        return_dict [dict<issue id, dict<date keyword, date (datetime object)>>] -- extract date for each date keyword for each issue. date keywords are created, updated, and resolutiondate
        """

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute('SELECT issue_id, created, updated, resolutiondate FROM basic_fields;')
        return_dict = {}
        for row in cur.fetchall():

            if row[3] is None:
                print("\n====")
                print("Skip: {0}".format(row[0]))
                print("====\n")
                if row[0]!="CHUKWA-6":
                    print("Error")
                    sys.exit()
                return_dict[row[0]] = {'created': self.extract_datetime_from_string(row[1]),
                                       'updated': self.extract_datetime_from_string(row[2]),
                                       'resolutiondate': self.extract_datetime_from_string(row[2])}
            
            else:
                return_dict[row[0]] = {'created': self.extract_datetime_from_string(row[1]),
                                       'updated': self.extract_datetime_from_string(row[2]),
                                       'resolutiondate': self.extract_datetime_from_string(row[3])}
        cur.close()
        conn.close()


        return return_dict


    def compare_date(self, keyword_extraction_dict, date_issue_dict, date_repo_dict):
        """
        Compare the created date of an issue with the commit date of a commit, and the resolution date of an issue with the commit date of a commit.
        If they meet the time restrictions, we store these pairs into the return dictionary.

        Arguments:
        keyword_extraction_dict [dict<issue id, list<commit hash>>] -- issue id to list of commit hashes. these commit hashes include issue id in their log message
        date_issue_dict [dict<issue id, dict<date keyword, date (datetime object)>>] -- extract date for each date keyword for each issue. date keywords are created, updated, and resolutiondate
        date_repo_dict [dict<commit hash, dict<key name, data>>] -- key name list: author_date, commit_date, author, committer, issue_id

        Returns:
        return_dict [dict<issue id, list<commit hash>>] -- issue id to list of commit hashes. these commit hashes include issue id in their log message and meet the time restriction
        """

        num_issue_id = len(keyword_extraction_dict)
        return_dict = {}
        for idx_issue_id, issue_id in enumerate(keyword_extraction_dict):
            if self.verbose>0:
                if idx_issue_id%1000==0:
                    print("Done issue: {0}/{1}".format(idx_issue_id, num_issue_id))
            for commit_hash in keyword_extraction_dict[issue_id]:

                if (date_issue_dict[issue_id]["created"] <= date_repo_dict[commit_hash]["commit_date"]) and (date_issue_dict[issue_id]["resolutiondate"] >= date_repo_dict[commit_hash]["commit_date"]):
                    if not issue_id in return_dict:
                        return_dict[issue_id] = []
                    return_dict[issue_id].append(commit_hash)

        return return_dict

    def run(self, p_name):
        """
        Exclude issue ids and commit hashes if they do not match the time restrictions
        on the keyword extraction data.

        Arguments:
        p_name [string] -- project name string

        Returns:
        issue2hash_dict [dict<issue id, list<commit hash>>] -- issue id to list of commit hashes. 
        """

        keyword_extraction_dict = util.load_pickle(self.link_data_path)

        """
        date_issue_dict [dict<issue id, dict<date keyword, date (datetime object)>>] -- extract date for each date keyword for each issue. date keywords are created, updated, and resolutiondate
        """
        db_path = "./../../prepare_data/extract_issues/db/{0}_issue_field_data.db".format(p_name)
        date_issue_dict = self.extract_dates(db_path)
        #print(date_issue_dict)
        self.date_issue_dict = date_issue_dict

        """
        repo_dict [dict<commit hash, dict<key name, data>>] -- key name list: author_date, commit_date, author, committer, issue_id
        """
        pickle_path = "./../../prepare_data/extract_issues/data_{0}/{1}_log_message_info.pickle".format(p_name.upper(), p_name)
        date_repo_dict = util.load_pickle(pickle_path) # 
        self.date_repo_dict = date_repo_dict

        issue2hash_dict = self.compare_date(keyword_extraction_dict, date_issue_dict, date_repo_dict)
        return issue2hash_dict

    def get_date_repo_dict(self):
        return self.date_repo_dict

    def get_date_issue_dict(self):
        return self.date_issue_dict


