#!/bin/sh
ulimit -t `expr $2 + 15`
ulimit -v 20971520
/home/mwinters/applications/clingo-dl/bin/clingo-dl /home/mwinters/experiments/baseline_minimize_statement/enc_clingo-dl_makespan_v2.lp $1 --outf=2 --quiet=0,2,2 --time-limit $2
