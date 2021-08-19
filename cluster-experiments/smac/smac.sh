#!/bin/sh

PYTHON="/home/mwinters/bin/python3"
CLINGOSMAC="/home/mwinters/smac-wrapper/clingosmac.py"
ENCODING="/home/mwinters/cluster-experiments/smac/enc_clingo-dl_lex-makespan_v2.lp"
INSTANCE_FILE_TRAIN="/home/mwinters/instances/instances_industrial_train.txt"
INSTANCE_FILE_TEST="/home/mwinters/instances/instances_industrial_test.txt"

REPETITIONS=$1
CUTOFF=$2
WALLCLOCK_LIMIT=$3
OBJECTIVE_FN=$4
MAX_MEMORY=16384

ulimit -t $WALLCLOCK_LIMIT; 
ulimit -v 20971520;
$PYTHON $CLINGOSMAC $ENCODING $INSTANCE_FILE_TRAIN $INSTANCE_FILE_TEST -r $REPETITIONS -c $CUTOFF -w $WALLCLOCK_LIMIT -o $OBJECTIVE_FN -l $MAX_MEMORY
