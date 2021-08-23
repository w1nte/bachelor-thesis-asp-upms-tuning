# SMAC-Wrapper
This is an adaption of the algorithm configurator [SMAC3](https://github.com/automl/SMAC3) for [clingo-dl](https://potassco.org/labs/clingodl/) (1.2.1) and [clasp](https://potassco.org/) (3.3.6).
SMAC-Wrapper is mostly inspired by [piclasp](https://www.cs.uni-potsdam.de/wv/piclasp/), unfortunately piclasp has not been further developed since 2015.

## Quick Usage:

Install all python requirements:
```bash
    python -m pip install -r requirements.txt
```

Then, install the runsolver binary:
```bash
    sh runsolver/install.sh
```

Run clingosmac.py:
```bash
    python clingosmac.py ../encodings/clingo-dl/01_clingodl.lp ../instances/instances_simple.txt ../instances/instances_simple.txt -o runtime -c 30 -w 600 -r 2
```
See `python clingosmac.py --help` for more information about the parameters.


### Used Environment
* python 3.9.6
* clingo 5.5.1
* clingo-dl 1.2.1
* smac 1.0.1






 