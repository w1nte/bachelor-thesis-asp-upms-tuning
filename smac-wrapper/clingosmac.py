import logging
import sys
import os
import argparse
import math
import numpy as np
import threading
from multiprocessing import Pool
from functools import partial
from smac.facade.smac_ac_facade import SMAC4AC
from smac.scenario.scenario import Scenario
from smac.tae import TAEAbortException, FirstRunCrashedException
from wrapper.pcs_parse_parameters import pcs_parse_parameters


__file_dir__ = os.path.abspath(os.path.dirname(__file__))


# result.csv semaphore if parallel
__output_lock = threading.Lock()


def main(args):
    if args.parallel == 1:
        run_smac(args, args.seed)
    elif args.parallel > 1:
        rng = np.random.RandomState(args.seed)
        with Pool(processes=args.parallel) as p:
            p.map(partial(run_smac, args), rng.randint(2**32-1, size=args.parallel))
    else:
        raise argparse.ArgumentTypeError('Minimum parallel is 1')


def run_smac(args: any, seed=None):
    best_incumbent, best_cost = (None, sys.maxsize)
    python = args.python
    repetitions = args.repetitions
    wrapper = args.wrapper
    encoding = args.encoding
    runsolver_binary = args.runsolver_binary
    runsolver_vlimit = args.vlimit
    rng = np.random.RandomState(seed)

    if not os.path.isdir(args.smac_output_dir):
        os.mkdir(args.smac_output_dir)

    scenario = Scenario({
        "algo": f"{python} {wrapper} {encoding} {runsolver_binary} {runsolver_vlimit}",
        "execdir": ".",
        "deterministic": 1,
        "run_obj": args.obj_fn,
        "cutoff_time": args.cutoff,
        "wallclock-limit": args.wallclock_limit,
        "instance_file": args.instancefile,
        "test_inst_fn": args.testinstancefile,
        "paramfile": args.param_file,
        "shared_model": True if args.psmac_dirs else False,
        "input_psmac_dirs": args.psmac_dirs,
        "output_dir": args.smac_output_dir
    })

    resultfile = args.output if args.output else os.path.join(scenario.output_dir, 'result.csv')

    logging.info(f'Result file: {resultfile}')
    if seed:
        logging.info(f'Seed: {seed}')

    for i in range(0, repetitions):
        logging.info(f'Repetition: {i+1}/{repetitions}') 
        smac = SMAC4AC(
            scenario=scenario,
            rng=rng
            )

        try:
            incumbent = smac.optimize()
        except (TAEAbortException, FirstRunCrashedException) as err:
            logging.error(err)
        finally:
            incumbent = smac.solver.incumbent

        params = get_params(incumbent)

        rh = smac.validate(
            config_mode='inc',
            instance_mode='test',    
        )
        ac = rh.average_cost(incumbent)

        __output_lock.acquire()
        with open(resultfile, 'a') as f:
            f.write(f'{math.ceil(ac*100)/100};{params}\n')
        __output_lock.release()

        logging.info(f'Average costs: {ac}')
        if ac < best_cost:
            best_cost = ac
            best_incumbent = incumbent
            logging.info(f'New best incumbent: {params}')

    params = get_params(best_incumbent)
    logging.info(f'Best incumbent with {best_cost} cost: {params}')

    
def get_params(incumbent):
    cmd = []
    for p in incumbent:
        if not incumbent.get(p) is None:
            cmd.extend(['-' + str(p), str(incumbent[p])])

    return ' '.join(pcs_parse_parameters(cmd)[0])


def parse_arguments():
    parser = argparse.ArgumentParser(description='''''', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('encoding', type=str, help='clingo encoding')
    parser.add_argument('instancefile', type=str, help='text file that contains paths to the training instances split by \\n.')
    parser.add_argument('testinstancefile', type=str, help='text file that contains paths to the test instances split by \\n.')
    parser.add_argument('-o', '--obj-fn', type=str, default='runtime', choices=['runtime', 'quality'], help='objective used by SMAC3 for optimization.')
    parser.add_argument('-c', '--cutoff', default=60, type=int, help='max runtime of each instance in seconds.')
    parser.add_argument('-w', '--wallclock-limit', default=600, type=int, help='max runtime of each repetition in seconds.')
    parser.add_argument('-r', '--repetitions', default=5, type=int, help='number of SMAC3 repetitions.')
    parser.add_argument('-l', '--vlimit', default=2048, type=int, help='runsolver memory limit (MB).')
    parser.add_argument('-p', '--parallel', default=1, type=int, help='number of parallel SMAC3 instances.')
    parser.add_argument('--seed', default=None, type=int, help='random initial seed.')
    parser.add_argument('--runsolver-binary', default=os.path.join(__file_dir__, 'runsolver/runsolver/src/runsolver'), type=str, help='runsolver binary.')
    parser.add_argument('--wrapper', default=os.path.join(__file_dir__, 'wrapper'), type=str, help='target algorithm wrapper.')
    parser.add_argument('--param-file', default=os.path.join(__file_dir__, 'pcs/clingo_dl_1_1_0.txt'), type=str, help='SMAC3 parameter file.')
    parser.add_argument('--python', default='python', type=str, help='python executable used by the wrapper.')
    parser.add_argument('--smac-output-dir', default='out', type=str, help='smac output dir (dir must exist).')
    parser.add_argument('--psmac-dirs', default=None, type=str, help='list of pSMACs output directories (enables pSMAC).')
    parser.add_argument('--output', default=None, type=str, help='output csv file.')
    parser.add_argument("-v", "--verbose", help="increase output verbosity.", action="store_true")

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_arguments()

    if args.verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s.%(msecs)03d (%(levelname)s) [%(process)d] %(module)s - %(funcName)s: %(message)s'
            )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s (%(levelname)s) [%(process)d]: %(message)s'
            )

    logging.info(f'SMAC call: {" ".join(sys.argv)}')

    main(args)
