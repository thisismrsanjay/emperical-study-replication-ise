import argparse
import glob
import sys
import os
import shutil

def mkdir_if_not_exist(path):
    if not os.path.exists(path):
        os.makedirs(path)

def move_files(ite_num, p_name):

    file_path_list = glob.glob("./tmp/out/{0}/tmp{1}/*/*/*.yaml".format(p_name, ite_num))
    #file_path_list = glob.glob("./tmp/out/tmp0/00/*/*.yaml".format(ite_num))
    for f_path in file_path_list:
        f_path_split = f_path.split("/")
        prefix = f_path_split[5]
        commit_hash = f_path_split[6]

        mkdir_if_not_exist("./output/{0}/{1}/{2}".format(p_name, prefix, commit_hash))

        target = "./output/{0}/{1}".format(p_name, "/".join(f_path_split[5:]))
        shutil.copy(f_path, target)


if __name__=="__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--project', '-p', type=str, required=True,
                        help='project name')
    args = parser.parse_args()
    p_name = args.project

    mkdir_if_not_exist("output/{0}".format(p_name))

    for ite_num in range(10):
        print("ite num: {0}".format(ite_num))
        move_files(ite_num, p_name)
