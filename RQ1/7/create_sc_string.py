import argparse
import subprocess
import sys
import os
import create_sc_string

from Utils import util
sys.path.append("./../common")
import git_reader


class LSCPProcessRepoFile:

    # the default value of ASSOC_THRESHOLD: refer to Figure 10 in Section 8.2.1 in nguyen2012FSE
    def __init__(self, extension_set=set([".java"]), verbose=0, parallel_iteration=0, p_name = None):
        """
        Arguments:
        extension_set [set<string>] -- extensions' set that would be analyzed
        """
        self.extension_set = extension_set
        self.verbose = verbose
        #self.tmp_prefix = tmp_prefix
        self.parallel_iteration = parallel_iteration

        self.p_name = p_name


    def use_lscp(self, snippet, text):
        if os.path.exists('./tmp/in/snippet.txt'):
            os.remove('./tmp/in/snippet.txt')
        if os.path.exists('./tmp/out/snippet.txt'):
            os.remove('./tmp/out/snippet.txt')

        with open('./tmp/in/snippet.txt', 'w') as f:
            f.write(snippet)
        if text:
            out = subprocess.check_output(['./lscp_text.pl'], stderr=subprocess.STDOUT).decode('utf-8', errors='ignore')
        else:
            out = subprocess.check_output(['./lscp.pl'], stderr=subprocess.STDOUT).decode('utf-8', errors='ignore')
        # if the result is 'regular subexpression recursion limit (32766) exceed'
        if 'limit' in out:
            raise
        with open('./tmp/out/snippet.txt'.format(self.parallel_iteration), 'r') as f:
            result = ' '.join(f.read().splitlines()) # separate the output
        return result

    def lscp(self, snippet, text=False):
        try:
            return self.use_lscp(snippet, text)
        except Exception:
            # print('lscp failed at', commithash)
            print("lscp is failed")
            return ""


    def extract_file_repo(self, repodir, hash_list, modified_file_repo_dict):
        """
        Extract entier file content parsed by lscp for each file for each commit hash.
        Here we use get_cur_entier_file so we extract entier file after applying changes to the file.

        Arguments:
        repodir [string] -- path to repository
        hash_list [list<commit hash>] -- studied commit hash list
        modified_file_repo_dict [dict<commit hash, list<modified files>>] -- modified files list for each commit hash

        Returns:
        return_dict [dict<commit hash, dict<file path, set<words in the file content>>>] -- words in the file content parsed by lscp for each file for each commit hash
        """

        len_hash_list = len(hash_list)

        return_dict = {}
        for idx_commit_hash, commit_hash in enumerate(hash_list):

            if self.verbose > 0:
                if (idx_commit_hash%10)==0:
                    print("extract file repo -- Done {0}/{1}".format(idx_commit_hash, len_hash_list))

            return_dict[commit_hash] = {}
            for f_path in modified_file_repo_dict[commit_hash]:
                root, ext = os.path.splitext(f_path)
                if ext in self.extension_set:
                    return_dict[commit_hash][f_path] = set(self.lscp(git_reader.get_cur_entier_file(repodir, commit_hash, f_path)).split())

        return return_dict


    def lscp_processing_for_file_repo(self, repodir, hash_list, modified_file_repo_dict):
        """
        Compare the description and comment in issue with log message at a commit.
        We identify this is a pair if they are similar

        Arguments:
        repodir [string] -- path to repository
        hash_list [list<commit hash>] -- studied commit hash list
        modified_file_repo_dict [dict<commit hash, list<modified files>>] -- modified files list for each commit hash

        Returns:
        return_dict [dict<issue id, list<commit hash>>] -- issue id to list of commit hashes. these commit hashes have the association values over a certain threshold
        """

        # extract words for each file for each commit hash (dict<commit hash, dict<file path, set<words in the file content>>>)
        modified_file_content_repo_dict = self.extract_file_repo(repodir, hash_list, modified_file_repo_dict)

        util.dump_pickle("./pickle_{0}/modified_file_content_repo_dict_ite{1}.pickle".format(self.p_name, self.parallel_iteration), modified_file_content_repo_dict)

    def extract_modified_file_repo(self, p_name, repodir, hash_list):
        """
        Extract all modified files for each commit hash in the (org) repository

        Arguments:
        p_name [string] -- project name string
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

    def run(self, p_name, hash_list):
        """
        Combine issue ids and commit hashes using word association.

        Arguments:
        p_name [string] -- project name string
        hash_list [list<commit hash>] -- studied commit hash list

        Returns:
        issue2hash_dict [dict<issue id, list<commit hash>>] -- issue id to list of commit hashes. these commit hashes are the similar wording with word association
        """

        """
        modified_file_issue_dict [dict<commit hash, list<modified files>>] -- modified files list for each commit hash
        """
        repodir = "./../../prepare_data/repository/{0}".format(p_name)
        modified_file_repo_dict = self.extract_modified_file_repo(p_name, repodir, hash_list)


        self.lscp_processing_for_file_repo(repodir, hash_list, modified_file_repo_dict)




if __name__=="__main__":


    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--project', '-p', type=str, required=True,
                        help='project name')
    parser.add_argument('--iteration', '-i', type=int, required=True,
                        help='iteration number')
    parser.add_argument('--max_iteration', '-mi', type=int, required=True,
                        help='max iteration number')
    args = parser.parse_args()
    p_name = args.project
    num_iteration = args.iteration
    max_iteration = args.max_iteration

    repodir = "./../../prepare_data/repository/{0}".format(p_name)


    print(p_name)
    print(num_iteration)
    print(max_iteration)
    hash_list = git_reader.get_all_hash_without_merge(repodir)
    len_hash_list = len(hash_list)
    unit = int(len_hash_list/max_iteration)

    if max_iteration==num_iteration:
        print("{0}:".format((num_iteration-1)*unit))
        target_hash_list = hash_list[(num_iteration-1)*unit:]
    else:
        print("{0}:{1}".format((num_iteration-1)*unit, num_iteration*unit))
        target_hash_list = hash_list[(num_iteration-1)*unit:num_iteration*unit]


    lscp_pro_obj = create_sc_string.LSCPProcessRepoFile(verbose=1, parallel_iteration=num_iteration, p_name=p_name)
    lscp_pro_obj.run(p_name, target_hash_list)


