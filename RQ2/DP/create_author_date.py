from Utils import util
from Utils import git_reader
from collections import OrderedDict
import datetime
import re

project_name_list = ['project name here']
repo_path = "./../../prepare_data/repository/{0}"

def author_date_convert_to_datetime(author_date):

    re_date = re.compile('^(\d{4})-(\d{2})-(\d{2})\s(\d{2}):(\d{2}):(\d{2})\s([\+-]\d{4})')
    #print(author_date)

    match = re_date.match(author_date)

    author_date = datetime.datetime(year=int(match.group(1)),month=int(match.group(2)),day=int(match.group(3)),hour=int(match.group(4)),minute=int(match.group(5)),second=int(match.group(6))) - datetime.timedelta(hours=float(match.group(7))/100)

    return author_date


def read_author_date(org_commit_hash_list, repo_path):
    """
    Returns:
    return_dict: [dict<original commit hash, author date>]
    """

    return_dict = OrderedDict()
    for commit_hash in sorted(org_commit_hash_list):
        date = git_reader.get_date(repo_path, commit_hash)
        return_dict[commit_hash] = author_date_convert_to_datetime(date)

    return return_dict


def authordate_initialize_without_merge(repo_path, projectNames):
    first_commit_cregit_hash_set = set(['81cf991f580a841dd8c016921b6c567ae0c0c4f3',
                                        'f5893295cc864449a07f12b6db219f2f46cb19d1',
                                        '31275a67f8fa261dec38e0c5b6445d2b3d88975c',
                                        'fdd4c40c8fd4a0d9b4ed8acceb8e92239f2e6b0d',
                                        'c8b3f3b16f60151f12ce0de8f8d3632e1434a60a'])
    for p_name in projectNames:

        tmp_list = git_reader.get_all_hash_without_merge(repo_path.format(p_name))

        assert tmp_list[-1] in first_commit_cregit_hash_set, "First commit hash error"
        hash_list = tmp_list[:-1]
        assert len(hash_list)+1==len(tmp_list), "Different size error"
        author_date = read_author_date(hash_list, repo_path.format(p_name)) # key: org commit hash, value: author date
        util.dump_pickle("./data/gap_para_author_date_{0}_without_merge.pickle".format(p_name), author_date)


def initialize_authordate():
    authordate_initialize_without_merge(repo_path, project_name_list)

def merge_commit():

    for p_name in project_name_list:
        without_merge_set = set(git_reader.get_all_hash_without_merge(repo_path.format(p_name)))
        with_merge_set = set(git_reader.get_all_hash(repo_path.format(p_name)))

        merge_commits = with_merge_set - without_merge_set

        util.dump_pickle("./data/{0}_merge.pickle".format(p_name), merge_commits)


if __name__=="__main__":
    initialize_authordate()
    merge_commit()