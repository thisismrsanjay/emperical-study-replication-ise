#!/bin/bash

mkdir data

project_name_list=("project name here")
max_iteration=25


for project in ${project_name_list[@]}; do
    mkdir pickle_${project}
    for iteration in `seq 1 $max_iteration`; do

        python3 exe_nsd_similarity.py -p $project -i $iteration -mi $max_iteration &
    done
    wait
done
wait

python3 comb_cosine_sim_and_generate_result.py
python3 comb_result.py