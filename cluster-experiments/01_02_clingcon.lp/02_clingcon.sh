#!/bin/sh

SOLVER="/home/mwinters/miniconda3/bin/clingcon"
ENCODING="/home/mwinters/cluster-experiments/01_02_clingcon.lp/02_clingcon.lp"
INSTANCE=$1
TIME_LIMIT=$2

ulimit -t `expr $TIME_LIMIT + 5`; 
ulimit -v 20971520;

$SOLVER $ENCODING $INSTANCE --outf=2 --quiet=0,2,2 --time-limit $TIME_LIMIT 0