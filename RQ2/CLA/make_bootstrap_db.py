from Utils import util
import sqlite3
import sys
import os

project_name_list = ["project name here"]

BOOTSTRAP_SIZE = 100
TIME_FILTERING_MIN = 10
NTEXT_TH = 3
WORD_ASSOC_TH = 5
COMMENT_COS_TH = 4
NSD_SIM_COS_TH = 2

def extract_cregit2org_commit_hashes(cur, cregit2org_commit_hashes_list, org2cregit_dict):
    ###########
    ###########
    command = """SELECT cregit_commit_hash, org_commit_hash
                 FROM cregit2org_commit_hashes;"""
    cur.execute(command)

    for row in cur.fetchall():
        cregit2org_commit_hashes_list.append(row)
        org2cregit_dict[row[1]] = row[0]

def extract_defect_fixing_commits(cur, cregit_defect_fix_hash_set, defect_fixing_commits_list):
    ###########
    ###########
    command = """SELECT *
                 FROM defect_fixing_commits;"""
    cur.execute(command)

    for row in cur.fetchall():
        if not row[0] in cregit_defect_fix_hash_set:
            continue
        defect_fixing_commits_list.append(row)

    #print(defect_fixing_commits_list)


def extract_defect_inducing_lines(cur, cregit_defect_fix_hash_set, defect_inducing_lines_list, cregit_defect_induce_hash_set):
    ###########
    ###########
    command = """SELECT *
                 FROM defect_inducing_lines;"""
    cur.execute(command)

    for row in cur.fetchall():
        if not row[6] in cregit_defect_fix_hash_set:
            continue
        defect_inducing_lines_list.append(row)
        cregit_defect_induce_hash_set.add(row[0])

    #print(defect_inducing_lines_list)
    #print(cregit_defect_induce_hash_set)


def extract_defect_inducing_commits(cur, cregit_defect_induce_hash_set, defect_inducing_commits_list):
    ###########
    ###########
    command = """SELECT *
                 FROM defect_inducing_commits;"""
    cur.execute(command)

    for row in cur.fetchall():
        if row[0] in cregit_defect_induce_hash_set:
            defect_inducing_commits_list.append((row[0], 1))
            #print(row[0])
        else:
            defect_inducing_commits_list.append((row[0], 0))


def create_db(org_db_name, new_db_name, org_defect_fix_hash_set, bootstrap_idx):


    org2cregit_dict = {}
    cregit_defect_fix_hash_set = set()
    cregit_defect_induce_hash_set = set()

    cregit2org_commit_hashes_list = []
    defect_fixing_commits_list = []
    defect_inducing_lines_list = []
    defect_inducing_commits_list = []

    conn = sqlite3.connect(org_db_name)
    cur = conn.cursor()

    extract_cregit2org_commit_hashes(cur, cregit2org_commit_hashes_list, org2cregit_dict)

    for commit_hash in org_defect_fix_hash_set:
        try:
            cregit_defect_fix_hash_set.add(org2cregit_dict[commit_hash])
        except KeyError:
            # it might be non source code modification
            continue

    extract_defect_fixing_commits(cur, cregit_defect_fix_hash_set, defect_fixing_commits_list)

    extract_defect_inducing_lines(cur, cregit_defect_fix_hash_set, defect_inducing_lines_list, cregit_defect_induce_hash_set)

    extract_defect_inducing_commits(cur, cregit_defect_induce_hash_set, defect_inducing_commits_list)

    conn.close()


    #try:
    #    os.remove(new_db_name)
    #except FileNotFoundError:
    #    pass
    conn = sqlite3.connect(new_db_name)
    cur = conn.cursor()
    #cur.execute("CREATE TABLE defect_fixing_commits_bi{0}(commit_hash TEXT PRIMARY KEY);")
    ##cur.execute("""CREATE TABLE defect_inducing_lines(commit_hash TEXT,
    ##        file_name TEXT, line INTEGER, day TEXT, time TEXT, zone TEXT, fixing_commit_hash TEXT,
    ##        PRIMARY KEY (commit_hash, file_name, line, fixing_commit_hash));""")
    #cur.execute("""CREATE TABLE defect_inducing_lines_bi{0}(commit_hash TEXT, fixing_commit_hash TEXT,
    #        PRIMARY KEY (commit_hash, fixing_commit_hash));""".format(bootstrap_idx))
    #cur.execute("""CREATE TABLE defect_inducing_commits_bi{0}(commit_hash TEXT PRIMARY KEY, defect INTEGER);""")
    #cur.execute("""CREATE TABLE cregit2org_commit_hashes(cregit_commit_hash TEXT PRIMARY KEY, org_commit_hash TEXT);""")

    for row in defect_fixing_commits_list:
        #cur.execute('INSERT INTO defect_fixing_commits(commit_hash, day, time, zone) VALUES(?,?,?,?)', row)
        cur.execute('INSERT INTO defect_fixing_commits_bi{0}(commit_hash) VALUES(?)'.format(bootstrap_idx), [row[0]])

    unique_check_set = set()
    for row in defect_inducing_lines_list:
        #cur.execute("""INSERT INTO defect_inducing_lines(commit_hash, file_name, line, day, time, zone, fixing_commit_hash)
        #                        VALUES(?,?,?,?,?,?,?)""", row)
        if (row[0]+row[6]) in unique_check_set:
            continue
        unique_check_set.add(row[0]+row[6])
        cur.execute("""INSERT INTO defect_inducing_lines_bi{0}(commit_hash, fixing_commit_hash)
                                VALUES(?,?)""".format(bootstrap_idx), [row[0], row[6]])

    for row in defect_inducing_commits_list:
        cur.execute("""INSERT INTO defect_inducing_commits_bi{0}(commit_hash, defect)
                    VALUES(?,?)""".format(bootstrap_idx), row)

    if bootstrap_idx==0:
        for row in cregit2org_commit_hashes_list:
            cur.execute("""INSERT INTO cregit2org_commit_hashes(cregit_commit_hash, org_commit_hash)
                    VALUES(?,?)""", row)
    conn.commit()
    conn.close()


def combine_dict(dict_A, dict_B):
    """
    Combine dict_A and dict_b. dict_A becomes the combined dict
    Args:
        dict_A:
        dict_B:

    """

    for key in dict_B:
        if not key in dict_A:
            dict_A[key] = dict_B[key]
            continue

        dict_A[key] = list(set(dict_A[key]) | set(dict_B[key]))


def execute(p_name, all_db, new_db, delete_rate, ila, bootstrap_idx, dict_path):
    ILA_dict = {"1": "{0}_keyword_extraction_{1}_{2}_with_restriction" \
        .format(p_name, delete_rate, bootstrap_idx),
                "3": "{0}_time_filtering_min_af{1}_with_restriction" \
                    .format(p_name, TIME_FILTERING_MIN),
                "5": "{0}_ntext_similarity_costh{1}_with_restriction" \
                    .format(p_name, NTEXT_TH),
                "7": "{0}_{1}_word_association_th{2}_bi{3}_with_restriction" \
                    .format(p_name, delete_rate, WORD_ASSOC_TH, bootstrap_idx),
                "8": "{0}_comment_costh0.{1}_ite1_with_restriction" \
                    .format(p_name, COMMENT_COS_TH),
                "9_1": "{0}_{1}_loner_bi{2}_with_restriction" \
                    .format(p_name, delete_rate, bootstrap_idx),
                "9_2": "{0}_{1}_phantom_bi{2}_with_restriction" \
                    .format(p_name, delete_rate, bootstrap_idx),
                "10": "{0}_nsd_similarity_costh{1}_with_restriction" \
                    .format(p_name, NSD_SIM_COS_TH),
                "11": "{0}_{1}_pu_link_bi{2}_with_restriction" \
                    .format(p_name, delete_rate, bootstrap_idx),
                "14_1": "{0}_RF_{1}_model_bi{2}_with_restriction" \
                    .format(p_name, delete_rate, bootstrap_idx),
                "14_2": "{0}_SVM_{1}_model_bi{2}_with_restriction" \
                    .format(p_name, delete_rate, bootstrap_idx)
                }


    key_issue2hash_dict = util.load_pickle(
        "{0}/{1}.pickle".format(dict_path, ILA_dict["1"]))
    target_issue2hash_dict = {}
    for temp_ila in ila.split(","):
        temp_dict = util.load_pickle("{0}/{1}.pickle".format(dict_path, ILA_dict[temp_ila]))
        combine_dict(target_issue2hash_dict, temp_dict)


    combine_dict(key_issue2hash_dict, target_issue2hash_dict)
    #print(len(key_issue2hash_dict))

    defect_fix_hash_set = set()
    for issue_id in key_issue2hash_dict:
        for commit_hash in key_issue2hash_dict[issue_id]:
            defect_fix_hash_set.add(commit_hash)
    print("number of defect fixing commits: {0:,}".format(len(defect_fix_hash_set)))

    create_db(all_db, new_db, defect_fix_hash_set, bootstrap_idx)


def init_new_db(new_db):
    try:
        os.remove(new_db)
    except FileNotFoundError:
        pass

    conn = sqlite3.connect(new_db)
    cur = conn.cursor()

    for i in range(BOOTSTRAP_SIZE):
        cur.execute("CREATE TABLE defect_fixing_commits_bi{0}(commit_hash TEXT PRIMARY KEY);".format(i))
        cur.execute("""CREATE TABLE defect_inducing_lines_bi{0}(commit_hash TEXT, fixing_commit_hash TEXT,
                PRIMARY KEY (commit_hash, fixing_commit_hash));""".format(i))
        cur.execute("""CREATE TABLE defect_inducing_commits_bi{0}(commit_hash TEXT PRIMARY KEY, defect INTEGER);""".format(i))

    #output = []
    #for i in range(BOOTSTRAP_SIZE):
    #    output.append("defect_bi{0} INTEGER".format(i))
    #output = ", ".join(output)
    #cur.execute("""CREATE TABLE defect_inducing_commits(commit_hash TEXT PRIMARY KEY, """ + output + """);""")
    cur.execute("""CREATE TABLE cregit2org_commit_hashes(cregit_commit_hash TEXT PRIMARY KEY, org_commit_hash TEXT);""")

    conn.commit()
    conn.close()

def main():

    dict_path = "./../../RQ1/evaluation/data"



    for p_name in project_name_list:
        print("===========")
        print(p_name)
        all_db = "./db/{0}_all.db".format(p_name)

        deleted_rate_list = [0, 10, 20, 30, 40, 50]

        ILA_list = ["1", "3", "5", "9_2", "14_1", "14_2", "3,5", "3,9_2", "3,14_1", "3,14_2",
                    "5,9_2", "5,14_1", "5,14_2", "9_2,14_1", "9_2,14_2", "14_1,14_2",
                    "3,5,9_2", "3,5,14_1", "3,5,14_2", "3,9_2,14_1", "3,9_2,14_2", "3,14_1,14_2",
                    "5,9_2,14_1", "5,9_2,14_2", "5,14_1,14_2", "9_2,14_1,14_2",
                    "3,5,9_2,14_1", "3,5,9_2,14_2", "3,5,14_1,14_2",
                    "3,9_2,14_1,14_2", "5,9_2,14_1,14_2",
                    "3,5,9_2,14_1,14_2"]
        
        assert 32==len(set(ILA_list)), "Num ILA_list is wrong: {0}".format(len(set(ILA_list)))

        for delete_rate in deleted_rate_list:
            print("delete rate: {0}".format(delete_rate))
            try:
                os.mkdir("./db/delete{0}".format(delete_rate))
            except FileExistsError:
                pass

            for ila in ILA_list:
                print("ILA: {0}".format(ila))
                new_db = "./db/delete{0}/{1}_{2}.db".format(delete_rate, p_name, ila)
                init_new_db(new_db)

                for bootstrap_idx in range(BOOTSTRAP_SIZE):
                    print("bootstrap: {0}".format(bootstrap_idx))

                    execute(p_name, all_db, new_db,
                            delete_rate, ila, bootstrap_idx, dict_path)




if __name__=="__main__":
    main()
