#!/bin/sh

mkdir CLA/hash
mkdir CLA/db
mkdir CLA/data
mkdir DP/data


delete_rate=("0" "10" "20" "30" "40" "50")
bootstrap_sample_iteration=19

mkdir ./DP/results
mkdir ./DP/log
mkdir ./DP/pickle

for delete in ${delete_rate[@]}; do
    mkdir ./DP/results/delete$delete
    for bootstrap_idx in `seq 0 $bootstrap_sample_iteration`; do
        mkdir ./DP/results/delete$delete/bi$bootstrap_idx
    done
done


for bootstrap_idx in `seq 0 $bootstrap_sample_iteration`; do
    mkdir ./DP/pickle/bi$bootstrap_idx
done



mkdir evaluation/results
mkdir evaluation/plot
mkdir evaluation/tables

mkdir evaluation/effort_plot
mkdir evaluation/effort_tables
