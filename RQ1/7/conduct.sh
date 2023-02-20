#!/bin/bash

mkdir data

# bash lscp_copy_script.sh # This copy script should execute at out of the docker environment

project_name_list=("project name here")

python3 create_dsc_comment_string.py

#assoc_threshold_list=(1)
assoc_threshold_list=(5)
delete_rate_list=(10 20 30 40 50)
max_iteration=25

bootstrap_sample_iteration=99
mkdir params

for project in ${project_name_list[@]}; do
    for iteration in `seq 1 $max_iteration`; do
        python3 ./create_sc_string.py -p $project -i $iteration -mi $max_iteration
    done
done


for bootstrap_idx in `seq 0 $bootstrap_sample_iteration`; do
    echo "bootstrap idx"
    echo $bootstrap_idx

    for project in ${project_name_list[@]}; do
        echo "project"
        echo $project
        mkdir params/bi${bootstrap_idx}_${project}/

        for delete_rate in ${delete_rate_list[@]}; do
            for assoc_th in ${assoc_threshold_list[@]}; do
                python3 exe_word_association.py -p $project -t $assoc_th -b $delete_rate -bi $bootstrap_idx
            done
        done
    done

done
