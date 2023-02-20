#!/bin/bash

project_name_list=("project name here")
delete_rate_list=(10 20 30 40 50)

bootstrap_sample_iteration=99

for bootstrap_idx in `seq 0 $bootstrap_sample_iteration`; do
    for project in ${project_name_list[@]}; do
        for delete_rate in ${delete_rate_list[@]}; do
            python3 ./exe_pu_link.py -p $project -b $delete_rate -bi $bootstrap_idx
        done
    done
done

python3 comb_separated_hash.py
