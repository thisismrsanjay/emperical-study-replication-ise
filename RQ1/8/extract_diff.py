import argparse
import os

import sys
sys.path.append("./../common")
import git_reader


extension_set = set([".java"])

def mkdir_if_not_exist(path):
    if not os.path.exists(path):
        os.mkdir(path)

def write_file_content(p_name, ite_num, f_name, prefix, commit_hash, content):
    mkdir_if_not_exist("./tmp/source/{0}/tmp{1}/{2}".format(p_name, ite_num, prefix))
    mkdir_if_not_exist("./tmp/source/{0}/tmp{1}/{2}/{3}".format(p_name, ite_num, prefix, commit_hash))
    with open("./tmp/source/{0}/tmp{1}/{2}/{3}/{4}".format(p_name, ite_num, prefix, commit_hash, f_name), "w") as f:
    #with open("./tmp/source/{0}".format(f_name), "w") as f:
        f.write(content)

def extract_diff(p_name, repodir, modified_file_repo_dict, hash_list, ite_num):
    """
    Extract entier file content for each file for each commit hash.
    Here we use get_cur_entier_file so we extract entier file after applying changes to the file.

    Arguments:
    p_name [string] -- project name string
    repodir [string] -- path to repository
    modified_file_repo_dict [dict<commit hash, list<modified files>>] -- modified files list for each commit hash
    hash_list [list<commit hash>] -- studied commit hashes
    ite_num [integer] -- iteration number
    """

    os.mkdir('tmp/source/{0}/tmp{1}'.format(p_name, ite_num))
    num_commit_hash = len(hash_list)

    for idx, commit_hash in enumerate(hash_list):
        if (idx%100)==0:
            print("ite num {0}: {1}/{2} done".format(ite_num, idx, num_commit_hash))

        prefix = commit_hash[0:2].lower()
        file_path_list = []
        for cnt, f_path in enumerate(modified_file_repo_dict[commit_hash]):
            root, ext = os.path.splitext(f_path)
            if ext in extension_set:
                content = git_reader.get_cur_entier_file(repodir, commit_hash, f_path)
                write_file_content(p_name, ite_num, "{0}_{1}".format(cnt, os.path.basename(f_path)), prefix, commit_hash, content)

def extract_modified_file_repo(p_name, hash_list):
    """
    Extract all modified files for each commit hash in the (org) repository

    Arguments:
    p_name [string] -- project name string
    hash_list [list<commit hash>] -- studied commit hash list

    Returns:
    return_dict [dict<commit hash, list<modified files>>] -- modified files list for each commit hash
    """

    print("Extract modified files")
    repo_dir = "./../../prepare_data/repository/{0}".format(p_name)
    return_dict = {}
    num_hash_list = len(hash_list)
    for idx, commit_hash in enumerate(hash_list):
        if idx%1000==0:
            print("{0}/{1}".format(idx, num_hash_list))
        return_dict[commit_hash] = git_reader.get_all_modified_files(repo_dir, commit_hash)

    return return_dict


def run(p_name, hash_list, ite_num):
    """
    Combine issue ids and commit hashes using word association.

    Arguments:
    p_name [string] -- project name string
    hash_list [list<commit hash>] -- studied commit hash list
    """

    """
    modified_file_repo_dict [dict<commit hash, list<modified files>>] -- modified files list for each commit hash
    """

    modified_file_repo_dict = extract_modified_file_repo(p_name, hash_list)
    repodir = "./../../prepare_data/repository/{0}".format(p_name)


    extract_diff(p_name, repodir, modified_file_repo_dict, hash_list, ite_num)


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--iteration', '-i', type=int, required=True,
                        help='iteration num')
    parser.add_argument('--project', '-p', type=str, required=True,
                        help='project name')
    args = parser.parse_args()
    p_name = args.project
    iteration = args.iteration

    repodir = "./../../prepare_data/repository/{0}".format(p_name)
    hash_list = sorted(git_reader.get_all_hash(repodir))
    #hash_list = ['001078e0677e39b962ca1da81fc34d7ac9a7e65c']

    #ite_num = 0
    ##run(p_name, hash_list[0:10], ite_num)
    #run(p_name, hash_list, ite_num)

    epoch_num = int(len(hash_list)/10)
    #epoch_num = 3
    ite_num = int(iteration)
    if ite_num!=9:
        run(p_name, hash_list[ite_num*epoch_num:(ite_num+1)*epoch_num], ite_num)
        #run(p_name, hash_list[1781:1782], 0)
    else:
        run(p_name, hash_list[ite_num*epoch_num:], ite_num)



if __name__=="__main__":

    main()
