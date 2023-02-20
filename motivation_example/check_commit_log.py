import argparse
import re
import subprocess
import sys
from Utils import util
sys.path.append("./../RQ1/common")
from Utils import git_reader

class ExtractIssueID:
    def __init__(self, repo_path, product_name):
        self.repo_path = repo_path
        self.product_name = product_name

    def get_commit_message(self, repodir, commit_hash):
        commit_msg_list = subprocess.check_output(
                ['git', '-C', '{}'.format(repodir), 'log', '--format=%B',
                '-n', '1', commit_hash],
                universal_newlines=True,
                errors="replace"
                ).splitlines()

        return "\n".join(commit_msg_list)


    def extract_commits(self):
        """
        dump: return_dict [dict<commit_hash, dict<key, data>>] -- dictionary of commit data. key: author, log, and modified_files
                                                                                             value: corresponding values
        """
        hash_list = git_reader.get_all_hash_without_merge(self.repo_path)

        return_dict = {}

        len_all_commits = len(hash_list)
        for cnt, commit_hash in enumerate(hash_list):
            if (cnt % 100) == 0:
                print("index: {0:,}/{1:,}".format(cnt, len_all_commits))

            return_dict[commit_hash] = {}

            return_dict[commit_hash]['log'] = self.get_commit_message(self.repo_path, commit_hash)

        util.dump_pickle("./data/{0}_commits.pickle".format(self.product_name), return_dict)

    def check_issue_id(self):

        def extract_issue_id(log):
            def find_all_num(re_str, log):
                return_list = []
                for num in re.findall(re_str, log):
                    return_list.append(num)

                return return_list

            log = log.lower()

            return_dict = {}
            re_apache = r"{0}-([0-9]+)".format(self.product_name)

            re_bug = r"bug[#\s\t]*([0-9]+)"
            re_fix = r"fix[#\s\t]*([0-9]+)"
            re_pr = r"pr[#\s\t]*([0-9]+)"
            re_show = r"show\_bug\.cgi\?id=([0-9]+)"
            re_num = r"\[([0-9]+)\]"

            return_dict['apache'] = find_all_num(re_apache, log)
            return_dict['bug'] = find_all_num(re_bug, log)
            return_dict['fix'] = find_all_num(re_fix, log)
            return_dict['pr'] = find_all_num(re_pr, log)
            return_dict['show'] = find_all_num(re_show, log)
            return_dict['num'] = find_all_num(re_num, log)

            return return_dict


        commit_data_dict = util.load_pickle("./data/{0}_commits.pickle".format(self.product_name))

        result_dict = {}
        for commit_hash in commit_data_dict.keys():
            log = commit_data_dict[commit_hash]['log']
            result_dict[commit_hash] = extract_issue_id(log)

        util.dump_pickle("./data/{0}_commit2issue.pickle".format(self.product_name), result_dict)


    def run(self):
        self.extract_commits()
        self.check_issue_id()


if __name__=="__main__":
    """ argument parser """
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--project', '-p', type=str, required=True,
                        help='project name')
    parser.add_argument('--repo', '-r', type=str, required=True,
                        help='path/to/repository')
    args = parser.parse_args()
    p_name = args.project
    repo_dir = args.repo

    extract_issue_id_obj = ExtractIssueID(repo_path=repo_dir, product_name=p_name)
    extract_issue_id_obj.run()





