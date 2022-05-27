# Evaluation

This folder contains all our experimental results and resulting plots.

----

#### The complete evaluation process:
1. Unpack the experiment results `tar -xvzf experiments.tar`
2. Create all evaluation files `python create_evaluation_file.py <experiment> <clingo-dl,clingo,clingcon>` (e.g. `python create_evaluation_file.py 00_baseline.lp clingo-dl`)
3. Plot all results `python ./create_plots.py`
