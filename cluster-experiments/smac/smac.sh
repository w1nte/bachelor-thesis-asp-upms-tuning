#!/bin/sh

PYTHON="/home/mwinters/bin/python3"
CLINGOSMAC="/home/mwinters/smac-wrapper/clingosmac.py"
ENCODING="/home/mwinters/experiments/smac/enc_clingo-dl_lex-makespan_v2.lp"
INSTANCE_FILE_TRAIN="/home/mwinters/instances/instances_industrial_train.txt"
INSTANCE_FILE_TEST="/home/mwinters/instances/instances_industrial_test.txt"
MAX_MEMORY=16384

ulimit -t $3; 
ulimit -v 20971520;
$PYTHON $CLINGOSMAC $ENCODING $INSTANCE_FILE_TRAIN $INSTANCE_FILE_TEST -r $1 -c $2 -w $3 -o $4 -l $MAX_MEMORY
