#!/bin/bash

mkdir data

project_name_list=("project name here")
delete_rate_list=(0 10 20 30 40 50)
model_name_list=("SVM" "RF")

bootstrap_sample_iteration=99

for bootstrap_idx in `seq 0 $bootstrap_sample_iteration`; do
    for model_name in ${model_name_list[@]}; do
        for project in ${project_name_list[@]}; do
            for delete_rate in ${delete_rate_list[@]}; do
                python3 exe_model.py -p $project -m $model_name -b $delete_rate -bi $bootstrap_idx
            done
        done
    done
done


mkdir feature_importance_RF
mkdir tables
python3 comb_separated_hash.py
python3 comb_separated_hash_important_features.py
