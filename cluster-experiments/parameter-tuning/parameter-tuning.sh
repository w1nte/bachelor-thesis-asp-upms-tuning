#!/bin/sh

PYTHON="/home/mwinters/bin/python3"
CLINGOSMAC="/home/mwinters/smac-wrapper/clingosmac.py"
WRAPPER="/home/mwinters/smac-wrapper/clingo_dl_wrapper.py"
PCS="/home/mwinters/smac-wrapper/pcs/minimize_makespan.txt"
ENCODING="/home/mwinters/cluster-experiments/parameter-tuning/03_clingo-dl-with-heuristic.lp"
INSTANCE_FILE_TRAIN="/home/mwinters/instances/instances_industrial_train.txt"
INSTANCE_FILE_TEST="/home/mwinters/instances/instances_industrial_test.txt"

REPETITIONS=$1
CUTOFF=$2
WALLCLOCK_LIMIT=$3
OBJECTIVE_FN=$4
MAX_MEMORY=16384

ulimit -t `expr $WALLCLOCK_LIMIT + 18000`; 
ulimit -v 20971520;
$PYTHON $CLINGOSMAC $ENCODING $INSTANCE_FILE_TRAIN $INSTANCE_FILE_TEST -r $REPETITIONS -c $CUTOFF -w $WALLCLOCK_LIMIT -o $OBJECTIVE_FN -l $MAX_MEMORY --wrapper $WRAPPER --param-file $PCS --output result.csv --python $PYTHON
