#!/usr/bin/env bash

echo "Generate instances. This can take a while..."

BASEDIR=$(dirname $(readlink -f "$0"))
DIR_INDUSTRIAL=${BASEDIR}/industrial
DIR_INDUSTRIAL_TRAIN=${BASEDIR}/industrial_train
DIR_INDUSTRIAL_TEST=${BASEDIR}/industrial_test
DIR_SIMPLE=${BASEDIR}/simple
PYTHON="python"

# create directories
mkdir -p $DIR_INDUSTRIAL
mkdir -p $DIR_INDUSTRIAL_TRAIN
mkdir -p $DIR_INDUSTRIAL_TEST
mkdir -p $DIR_SIMPLE

# generate instances
cd $DIR_INDUSTRIAL
${PYTHON} ${BASEDIR}/instance_generator.py
cd $DIR_INDUSTRIAL_TRAIN
${PYTHON} ${BASEDIR}/instance_generator_tuning.py industrial_train
cd $DIR_INDUSTRIAL_TEST
${PYTHON} ${BASEDIR}/instance_generator_tuning.py industrial_test
cd $DIR_SIMPLE
${PYTHON} ${BASEDIR}/instance_generator_tuning.py simple

# create instance list files
cd $BASEDIR
ls -d ${DIR_INDUSTRIAL}/*.lp > instances_industrial.txt
ls -d ${DIR_INDUSTRIAL_TRAIN}/*.lp > instances_industrial_train.txt
ls -d ${DIR_INDUSTRIAL_TEST}/*.lp > instances_industrial_test.txt
ls -d ${DIR_SIMPLE}/*.lp > instances_simple.txt

echo "Done!"
