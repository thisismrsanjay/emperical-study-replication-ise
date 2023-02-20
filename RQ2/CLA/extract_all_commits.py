
from Utils import git_reader
from Utils import util

project_name_list = ["project name here"]


def main():

    for p_name in project_name_list:
        repo_dir = "./../../prepare_data/repository/{0}".format(p_name)
        hash_list = git_reader.get_all_hash(repo_dir)

        util.dump_pickle("./hash/{0}_all_commits.pickle".format(p_name), {"all": hash_list})
        util.dump_pickle("./hash/{0}_keyword_extraction_0_with_restriction.pickle".format(p_name), {})



if __name__=="__main__":
    main()

