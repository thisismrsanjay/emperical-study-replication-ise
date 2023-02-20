#!/bin/sh

project_name_list=("avro")

mkdir data
mkdir db

for project in ${project_name_list[@]}; do
    python3 execute.py -p $project -c "./../../prepare_data/repository_cregit" -t "./data" -d "./hash" -i "all" -o "./db/${project}_all.db" -b 0
done
wait
