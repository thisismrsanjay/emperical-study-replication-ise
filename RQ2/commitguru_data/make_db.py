import argparse
from os import path
import re
import csv
import sys
import sqlite3
from Utils import git_reader

csv.field_size_limit(sys.maxsize)

project_name_list = ['project name here']

def read_csv(csv_path):
    csv_data = []
    with open(csv_path, 'r', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            csv_data.append(row)
    return csv_data


def order_by_date(repo_dir, csv_data):
    hash_list = git_reader.get_all_hash(repo_dir)
    hash_list.reverse() 
    csv_hash_dict = {}
    ordered_list = [csv_data.pop(0)]
    for row in csv_data:
        csv_hash_dict[row[0]] = row
    for commit_hash in hash_list:
        #if commit_hash in csv_hash_dict:
        ordered_list.append(csv_hash_dict[commit_hash])
    return ordered_list


def write_data(output_data, output_path):

    conn = sqlite3.connect(output_path)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS data;")

    header = output_data.pop(0)
    header = ', '.join(header)
    cur.execute("CREATE TABLE data(id integer PRIMARY KEY, {});".format(header))
    for row in output_data:
        row = list(map(lambda x: re.sub("'", "''", x), row))
        values = ', '.join(map(lambda x: "'" + x + "'", row))  # 全要素''で囲む
        cur.execute("INSERT INTO data({}) VALUES({})".format(header, values))
    conn.commit()
    conn.close()


def main():

    for p_name in project_name_list:
        csv_path = "./{0}.csv".format(p_name)
        repo_dir = "./../../prepare_data/repository/{0}".format(p_name)
        output_path = "./{0}.db".format(p_name)

        if not path.exists(csv_path):
            exit('file not found.')

        print('### Step 1: Read Commit Guru CSV.')
        csv_data = read_csv(csv_path)
        print('# of commits in Commit Guru CSV:', len(csv_data) - 1)
        csv_data = order_by_date(repo_dir, csv_data)
        print('# of commits (after ordering by date):', len(csv_data) - 1)

        print('### Step 2: Write data to {}.'.format(output_path))
        write_data(csv_data, output_path)


if __name__ == "__main__":
    main()
