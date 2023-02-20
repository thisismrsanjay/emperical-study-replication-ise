#!/bin/sh


project_list=("project name here")
delete_rate=("0" "10" "20" "30" "40" "50")
ila_list=("1" "3" "5" "9_2" "14_1" "14_2" "3,5" "3,9_2" "3,14_1" "3,14_2" "5,9_2" "5,14_1" "5,14_2" "9_2,14_1" "9_2,14_2" "14_1,14_2" "3,5,9_2" "3,5,14_1" "3,5,14_2" "3,9_2,14_1" "3,9_2,14_2" "3,14_1,14_2" "5,9_2,14_1" "5,9_2,14_2" "5,14_1,14_2" "9_2,14_1,14_2" "3,5,9_2,14_1" "3,5,9_2,14_2" "3,5,14_1,14_2" "3,9_2,14_1,14_2" "5,9_2,14_1,14_2" "3,5,9_2,14_1,14_2")
bootstrap_sample_iteration=19



for p_name in ${project_list[@]}; do
	for delete in ${delete_rate[@]}; do
		for ila_name in ${ila_list[@]}; do
			for bootstrap_idx in `seq 0 $bootstrap_sample_iteration`; do
				python3 prediction.py -p ${p_name} -i ${ila_name} -br ${delete} -b ${bootstrap_idx}
			done
		done
	done
done
