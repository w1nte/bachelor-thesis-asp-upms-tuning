#!/bin/sh

SOLVER="/home/mwinters/miniconda3/bin/clingo-dl"
ENCODING="/home/mwinters/cluster-experiments/03_clingo-dl-with-heuristic-and-parameter-tuning.lp/03_clingo-dl-with-heuristic.lp"
INSTANCE=$1
TIME_LIMIT=$2

ulimit -t `expr $TIME_LIMIT + 10`; 
ulimit -v 20971520;

$SOLVER $ENCODING $INSTANCE --outf=2 --quiet=0,2,2 --time-limit $TIME_LIMIT --restart-on-model --acyc-prop=1 --add-mutexes=0,0 --enum-mode=domRec --heuristic=Domain --init-watches=first --lookahead=no --loops=distinct --minimize-variable=makespan --opt-heuristic=model --opt-strategy=bb,hier --otfs=1 --partial-check=0 --propagate=partial+ --propagate-budget=4 --propagate-root=9 --rand-freq=0.02 --rand-prob=0 --reset-restarts=repeat --reverse-arcs=1 --save-progress=180 --score-other=loop --sign-def=asp --strengthen=local,short --trans-ext=integ --update-lbd=no --update-mode=propagate --contraction=no --del-cfl=x,201,1.5,10 --del-estimate=0 --del-glue=2,1 --del-grow=1.5285708351922447,13.67559392783562 --del-init=3.9103798216397716,866,9000 --del-max=264554 --del-on-restart=14 --deletion=ipSort,75,activity --dom-mod=true,opt,show --eq=0 --forget-on-step=0 --sat-prepro=2,frozen=0,iter=10,occ=25,size=4000,time=0 --score-res=min