#!/bin/sh

SOLVER="/home/mwinters/miniconda3/bin/clingo-dl"
ENCODING="/home/mwinters/cluster-experiments/04_clingo-dl-with-more-redundant-constraints-and-heuristic.lp/04_clingo-dl-with-more-redundant-constraints-and-heuristic.lp"
INSTANCE=$1
TIME_LIMIT=$2

ulimit -t `expr $TIME_LIMIT + 5`; 
ulimit -v 20971520;

$SOLVER $ENCODING $INSTANCE --outf=2 --quiet=0,2,2 --time-limit $TIME_LIMIT --minimize-variable=makespan --heuristic=Domain