## Report

https://docs.google.com/document/d/1FbYK3RxR91ZSd1Yz1CQF5dV2dHfLLif8xC8rA7URQx4/edit?usp=sharing

## ILA's  & Required Model
https://bit.ly/3kcdSKJ

## Code Documentation 

This contains scripts to replicate "An empirical study of issue-link algorithms: which issue-link algorithms should we use?"


There were lots of bugs in the orignal guide which was difficult to consolidate in one place but testing one repo at a time works 

## How to get same output

### 0. Core of Experiement

```
cd ./motivation_example/target_repository/
bash clone.sh
cd ./../
bash mk_dir.sh
bash conduct.sh
python3 evaluate.py
```

    <!-- put the result here also the tables and folders  work1 -->
The output in ./tables/link_proportion.csv
corresponds to Table 1. 

![research question 1 result](https://github.com/thisismrsanjay/emperical-study-replication-ise/blob/master/table1.png?raw=true)



Table 1 The proportion of commits in which we can find issue id candidates in the studied projects in Group B (58 projects from 24 studies). The numerator is the number of commits in which we can find issue id candidates; the denominator is the number of all commits without merge commits. We cloned all the projects on Oct. 7, 2021


### 1. Data Prepration

<!-- Put arvo data here work2-->
I have checked for arvo 

Clone repos.





Extract all issues from the issue tracking system

```
cd ./../extract_issues
bash mk_dir.sh
python3 extract_issues_from_JIRA.py                  
python3 parse_issue_list_json.py             
python3 extract_data_from_JIRA.py
python3 check_all_log_repository.py
python3 extract_log_msg_repository.py         
```

I have use arvo to test ILA's 
prepared data repository should be at ./prepare_data/repository 

Extracted database will be in sqlite database with issue_id,decription etc..

![database](https://github.com/thisismrsanjay/emperical-study-replication-ise/blob/master/database.png?raw=true)


### 2. For ResearchQuestion1

Reseach criteria exe file is in 1,3,5,7,8,9,10,11,14 folder we have to run all the executalbes.py 
individual file is in: https://bit.ly/3kcdSKJ 

```
$ cd ./../../RQ1
$ bash mk_dir.sh
$ cd 1/
$ python3 exe_keyword_extraction.py
$ cd ./../random_delete/
$ python3 generate_delete_data.py
$ python3 ground_truth.py
$ cd ./../3/
$ python3 exe_time_filtering.py
$ cd ./../5/
$ bash conduct.sh
$ cd ./../7/
$ bash conduct.sh
$ cd ./../8
$ vim extract_AST.py # please modify {{absolute path}} following your environment
$ bash para.sh
$ python3 exe_comment.py
$ cd ./../9
$ bash conduct_loner.sh
$ bash conduct_phantom.sh
$ cd ./../10
$ bash conduct.sh
$ cd ./../11
$ bash conduct.sh
$ cd ./../14
$ bash conduct.sh
$ cd ./../evaluation
$ python3 ILA.py
$ python3 evaluation_with_restriction.py
$ python3 SKESD.py
$ python3 make_table_with_rank.py
```

#### the extracted results and databases images are inserted



The output in /RQ1/evaluation/tables/*
corresponds to Table 7 in our paper.
 
![research question 1 result](https://github.com/thisismrsanjay/emperical-study-replication-ise/blob/master/table7.png?raw=true)


I din't able to format csv properly but most of data was correct 

I was able to do this much till now RQ2 is giving lots of error messages,
which I  tried for 2-3 days 
