import subprocess
import re
import sys
import os

from Utils import util

sys.path.append("./../common")
import issue_db_reader
import common

project_name_list = ["project name here"]


class WordAssociation:

    # the default value of ASSOC_THRESHOLD: refer to Figure 10 in Section 8.2.1 in nguyen2012FSE
    def __init__(self):
        self.verbose = 1


    def use_lscp(self, snippet, text):
        with open('tmp/in/snippet.txt', 'w') as f:
            f.write(snippet)
        if text:
            out = subprocess.check_output(['./lscp_text.pl'], stderr=subprocess.STDOUT).decode('utf-8', errors='ignore')
        else:
            out = subprocess.check_output(['./lscp.pl'], stderr=subprocess.STDOUT).decode('utf-8', errors='ignore')
        # if the result is 'regular subexpression recursion limit (32766) exceed'
        if 'limit' in out:
            raise
        with open('tmp/out/snippet.txt', 'r') as f:
            result = ' '.join(f.read().splitlines()) # separate the output
        return result

    def lscp(self, snippet, text=False):
        try:
            return self.use_lscp(snippet, text)
        except Exception:
            # print('lscp failed at', commithash)
            print("lscp is failed")
            return ""

    def init_lscp(self):
        if not os.path.exists('tmp'):
            os.mkdir('tmp')
            os.mkdir('tmp/in')
            os.mkdir('tmp/out')


    def compare_association(self, p_name, dsc_issue_dict, comment_issue_dict, issue_id_list):

        self.init_lscp()
        for idx_issue_id, issue_id in enumerate(issue_id_list):
            if self.verbose > 0:
                if idx_issue_id%1000==0:
                    print("Done issue id: {0}".format(idx_issue_id))

            if not issue_id in dsc_issue_dict:
                content = ""
            elif dsc_issue_dict[issue_id] is None:
                content = ""
            else:
                content = dsc_issue_dict[issue_id]

            if not issue_id in comment_issue_dict:
                content += ""
            elif comment_issue_dict[issue_id] is None:
                content += ""
            else:
                content += comment_issue_dict[issue_id]
        
            
            util.dump_pickle("./pickle_{0}/{1}_dsc_comment_string.pickle".format(p_name, issue_id), self.lscp(content, text=True))


    def run(self, p_name, issue_id_list):

        db_path = "./../../prepare_data/extract_issues/db/{0}_issue_field_data.db".format(p_name)
        """
        dsc_issue_dict [dict<issue id, description>] -- description for each issue id
        comment_issue_dict [dict<issue id, comments (a string)>] -- a string of comments for each issue id
        """
        dsc_issue_dict = common.extract_description(db_path)
        comment_issue_dict = common.extract_comment(db_path)



        self.compare_association(p_name, dsc_issue_dict, comment_issue_dict, issue_id_list)




if __name__=="__main__":

    for p_name in project_name_list:
        if not os.path.exists('pickle_{0}'.format(p_name)):
            os.mkdir('pickle_{0}'.format(p_name))
        db_path = "./../../prepare_data/extract_issues/db/{0}_issue_field_data.db".format(p_name)
        issue_id_list = issue_db_reader.read_issue_id_list(db_path)
        word_association_obj = WordAssociation()
        #word_association_obj.run(issue_id_list[0:100])
        word_association_obj.run(p_name, issue_id_list)
