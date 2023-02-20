#!/bin/sh

sudo rm -rf tmp

project_name_list=("project name here")
mkdir tmp
mkdir tmp/source
mkdir tmp/out
for project in ${project_name_list[@]}; do
    mkdir tmp/source/$project
    mkdir tmp/out/$project

    for ite in `seq 0 9`; do
        python3 extract_diff.py -i $ite -p $project &
        #python extract_AST.py $ite
    done
    wait
done

cp -r ./tmp ./bouffier-java/

python3 extract_AST.py
wait

cp -r ./bouffier-java/tmp/out ./tmp/

for project in ${project_name_list[@]}; do
    python3 comb_file.py -p $project &
    mkdir pickle_${project}
done
wait
