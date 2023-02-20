
import sqlite3
import glob
import re
from datetime import datetime

import sys
sys.path.append("./../common")
import git_reader

def extract_description(db_path):
    """
    extract description of issue for each issue id.

    Arguments:
    dp_path [string] -- database path

    Returns:
    return_dict [dict<issue id, description] -- description for each issue id
    """

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('SELECT issue_id, description FROM basic_fields;')
    return_dict = {}
    for row in cur.fetchall():

        return_dict[row[0]] = row[1]
    cur.close()
    conn.close()


    return return_dict

def extract_comment(db_path):
    """
    extract comments for each issue id.

    Arguments:
    dp_path [string] -- database path

    Returns:
    return_dict [dict<issue id, comments (a string)] -- a string of comments for each issue id
    """

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('SELECT issue_id, body FROM comments;')
    return_dict = {}
    for row in cur.fetchall():
        if not row[0] in return_dict:
            return_dict[row[0]] = ""
        return_dict[row[0]] += row[1] + "\n"
    cur.close()
    conn.close()


    return return_dict


def extract_modified_file_repo(repodir, hash_list):
    """
    Extract all modified files for each commit hash in the (org) repository

    Arguments:
    repodir [string] -- path to repository
    hash_list [list<commit hash>] -- studied commit hash list

    Returns:
    return_dict [dict<commit hash, list<modified files>>] -- modified files list for each commit hash
    """

    print("Extract modified files")
    return_dict = {}
    num_hash_list = len(hash_list)
    for idx, commit_hash in enumerate(hash_list):
        if idx%1000==0:
            print("{0}/{1}".format(idx, num_hash_list))
        return_dict[commit_hash] = git_reader.get_all_modified_files(repodir, commit_hash)

    return return_dict

def _extract_all_javadoc(f_path):
    re_javadoc = r"\s*comment\(Type=JavadocComment\):\s*$"
    re_javadoc_content = r"\s*content:\s(.*)$"

    return_list = []

    with open(f_path, "r", encoding="utf-8") as f:
        contents = f.readlines()

    flag = 0
    for row in contents:
        if flag==1:
            flag = 0
            match = re.search(re_javadoc_content, row)
            return_list.append(match.group(1)[1:-1])

        if re.match(re_javadoc, row):
            flag = 1

    return return_list



def extract_javadoc(p_name, modified_file_repo_dict, verbose=1):
    """
    Extract the javadocs of all the modified fils for each commit hash.
    Such a javadoc is already preprocessed.

    Arguments:
    modified_file_repo_dict [dict<commit hash, list<modified files>>] -- modified files list for each commit hash

    Returns:
    return_dict [dict<commit_hash, javadocs (a string)>] -- all javadocs that were extracted
    """
    return_dict = {}

    if verbose>0:
        num_modified_file_repo = len(modified_file_repo_dict)
    for idx_commit_hash, commit_hash in enumerate(modified_file_repo_dict.keys()):
        #for commit_hash in ['00a01dca6babded748869eb67133f66262a02013']:

        if verbose>0:
            if idx_commit_hash%1000==0:
                print("Done commit hash: {0}/{1}".format(idx_commit_hash, num_modified_file_repo))


        prefix = commit_hash[0:2]

        file_path_list = glob.glob("./output/{0}/{1}/{2}/*".format(p_name, prefix, commit_hash))

        content = ""
        for f_path in file_path_list:
            #data = util.read_yaml(f_path)
            #content += " ".join(self._extract_all_javadoc(data, None))
            content += " ".join(_extract_all_javadoc(f_path))

        #return_dict[commit_hash] = ntext_similarity.preprocess_text(content).split()
        return_dict[commit_hash] = content

    return return_dict

def extract_datetime_from_string(target):
    return datetime.strptime(target, "%Y-%m-%dT%H:%M:%S.%f%z")

def extract_dates(db_path):
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

        return_dict[row[0]] = {'created': extract_datetime_from_string(row[1]),
                               'updated': extract_datetime_from_string(row[2]),
                               'resolutiondate': extract_datetime_from_string(row[3])}
    cur.close()
    conn.close()


    return return_dict
