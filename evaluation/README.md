# Evaluation

This folder contains all our experimental results and resulting plots.

----

#### The complete evaluation process:
1. Unpack the experiment results `tar -xvzf experiments.tar`
2. Install the python requirements `python -m pip install -r requirements.txt`
3. Create all evaluation files `python create_evaluation_file.py <experiment> <clingo-dl,clingo,clingcon>` (e.g. `python create_evaluation_file.py 00_baseline.lp clingo-dl`)
4. Plot all results `python ./create_plots.py`
