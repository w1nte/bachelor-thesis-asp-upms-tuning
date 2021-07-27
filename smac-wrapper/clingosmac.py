import logging
import re
import sys
import os
import argparse
import random
from multiprocessing import Process, Queue
from smac.facade.smac_ac_facade import SMAC4AC
from smac.scenario.scenario import Scenario
from smac.configspace import ConfigurationSpace
from wrapper.pcs_parse_parameters import pcs_parse_parameters


__file_dir__ = os.path.abspath(os.path.dirname(__file__))


def main():
    args = parse_arguments()
    
    best_incumbent, best_cost = (None, sys.maxsize)
    python = args.python
    repetitions = args.repetitions
    wrapper = args.wrapper
    encoding = args.encoding
    runsolver_binary = args.runsolver_binary
    runsolver_vlimit = args.vlimit

    scenario = Scenario({
        "algo": f"{python} {wrapper} {encoding} {runsolver_binary} {runsolver_vlimit}",
        "execdir": ".",
        "deterministic": 1,
        "run_obj": args.obj_fn,
        "cutoff_time": args.cutoff,
        "wallclock-limit": args.wallclock_limit,
        "instance_file": args.instancefile,
        "test_inst_fn": args.testinstancefile,
        "paramfile": args.param_file
    })

    for i in range(0, repetitions):
        print(f'Repetition {i+1}/{repetitions}') 
        smac = SMAC4AC(scenario=scenario)
        queue = Queue()
   
        while True:
            p = Process(target=run_smac, args=(queue, smac))
            p.start()
            p.join()
            if not queue.empty():
                break
            else:
                scenario.cs.seed(random.randint(0, 2 ** 32 - 1))
                print('Smac optimizing was killed! Restart.')

        incumbent = queue.get()

        params = get_params(incumbent)

        rh = smac.validate(
            config_mode='def+inc',
            instance_mode='test',    
        )
        ac = rh.average_cost(incumbent)

        with open(os.path.join(scenario.output_dir, 'result.csv'), 'a') as f:
            f.write(f'{ac};{params}\n')

        print(f'Average costs: {ac}')
        if ac < best_cost:
            best_cost = ac
            best_incumbent = incumbent
            print(f'New best incumbent: {params}')

    params = get_params(best_incumbent)
    print(f'Best incumbent with {best_cost} cost: {params}')


def run_smac(queue, smac):
    incumbent = smac.optimize()
    queue.put(incumbent)

    
def get_params(incumbent):
    cmd = []
    for p in incumbent:
        if not incumbent.get(p) is None:
            cmd.extend(['-' + str(p), str(incumbent[p])])

    return ' '.join(pcs_parse_parameters(cmd)[0])


def parse_arguments():
    parser = argparse.ArgumentParser(description='smac3 caller.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('encoding', type=str)
    parser.add_argument('instancefile', type=str)
    parser.add_argument('testinstancefile', type=str)
    parser.add_argument('-o', '--obj-fn', type=str, default='runtime', choices=['runtime', 'quality'])
    parser.add_argument('-c', '--cutoff', default=60, type=int)
    parser.add_argument('-w', '--wallclock-limit', default=600, type=int)
    parser.add_argument('-r', '--repetitions', default=5, type=int)
    parser.add_argument('-l', '--vlimit', default=2048, type=int, help='runsolver memory limit (MB)')
    parser.add_argument('--runsolver-binary', default=os.path.join(__file_dir__, 'runsolver/runsolver/src/runsolver'), type=str)
    parser.add_argument('--wrapper', default=os.path.join(__file_dir__, 'wrapper'), type=str)
    parser.add_argument('--param-file', default=os.path.join(__file_dir__, 'pcs/clingo_dl_1_1_0.txt'), type=str)
    parser.add_argument('--python', default='python', type=str, description='python executable used by SMAC3.')

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    main()
