#!/usr/bin/env python
import sys
import argparse
import json
from dataclasses import dataclass
from enum import Enum
from typing import List
from pcs_parse_parameters import pcs_parse_parameters
from runsolver import runsolver, RunsolverConfiguration


class SMAC_status(Enum):
    SUCCESS = 'SUCCESS'
    CRASHED = 'CRASHED'
    SAT = 'SAT'
    UNSAT = 'UNSAT'
    TIMEOUT = 'TIMEOUT'


@dataclass
class SMAC_result:
    status: SMAC_status
    running_time: int
    runlength: int
    quality: int
    seed: int

    def __repr__(self) -> str:
        # SMAC return as decribed in the docs
        # https://automl.github.io/SMAC3/master/quickstart.html?highlight=wrapper#command-line
        return f'Result for SMAC: {self.status.value}, {self.running_time}, {self.runlength}, {self.quality}, {self.seed}'


class WrapperCLI(object):
    """
    Main SMAC wrapper object.

    This class can be inherited for costumization and methods like determine_* can be overrided.
    """

    encoding: str
    runsolver_binary: str
    memory_limit: int
    instance: str
    instance_specific: str
    cutoff: float
    cutoff_length: float
    seed: float
    pcs_parameters: List[any]

    _MAX_QUALITY = 99999999.  # quality value if solutions is unsat or solver crashed.

    def __init__(self) -> None:
        super().__init__()
        self.parse_arguments()

    def run(self):
        result = SMAC_result(SMAC_status.TIMEOUT, self.cutoff, -1, self._MAX_QUALITY, self.seed)

        solver_parameters, solver = pcs_parse_parameters(self.pcs_parameters)

        if not solver:
            raise Exception('pcs parameter "--solver" is missing!')

        solver_cmd = self.build_solver_cmd(solver, solver_parameters)

        runsolver_cfg = RunsolverConfiguration(
            runsolver_bin=self.runsolver_binary,
            vsize_limit=self.memory_limit,
            wall_clock_limit=self.cutoff 
        )

        runsolver_output = runsolver(solver_cmd, runsolver_cfg)

        try:
            clasp_json = json.loads(runsolver_output.decode('utf-8'))
            self.determine_SMAC_result(clasp_json, result)
        except (json.JSONDecodeError, LookupError) as e:
            result.status = SMAC_status.CRASHED
            print(result)
            sys.exit(1)
        finally:
            print(result)

    def determine_SMAC_result(self, clasp_json: any, result: SMAC_result):
        # override if required, note that result is a reference.
        result.running_time=float(clasp_json['Time']['Total'])
        self.determine_SMAC_status(clasp_json, result)
        self.determine_solution_quality(clasp_json, result)
        
    def determine_SMAC_status(self, clasp_json: any, result: SMAC_result):
        # override if required, note that result is a reference.
        if clasp_json['Result'] == 'SATISFIABLE' or clasp_json['Result'] == 'OPTIMUM FOUND':
            result.status = SMAC_status.SAT
        elif clasp_json['Result'] == "UNSATISFIABLE":
            result.status = SMAC_status.UNSAT

    def determine_solution_quality(self, clasp_json: any, result: SMAC_result):
        # override if required, note that result is a reference.
        try:
            costs = [self._MAX_QUALITY] + [float(c) for c in clasp_json['Models']['Costs']]
        except KeyError:
            costs = [self._MAX_QUALITY]

        result.quality = min(costs)

    def build_solver_cmd(self, solver_binary: str, solver_parameters: List[str]):
        return [solver_binary, '--outf=2', '--quiet=1,1,2', self.encoding, self.instance] + solver_parameters

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description='SMAC3 Clingo-dl Wrapper.')

        parser.add_argument('encoding', type=str, help='clingo encoding.')
        parser.add_argument('runsolver_binary', type=str, help='runsolver binary.')
        parser.add_argument('memory_limit', type=int, help='clingo memory limit (MB)')
        parser.add_argument('instance', type=str)
        parser.add_argument('instance_specific', type=str)
        parser.add_argument('cutoff', type=float)
        parser.add_argument('cutoff_length', type=float)
        parser.add_argument('seed', type=float)

        args, pcs_parameters = parser.parse_known_args()

        self.encoding = args.encoding
        self.runsolver_binary = args.runsolver_binary
        self.memory_limit = args.memory_limit
        self.instance = args.instance
        self.instance_specific = args.instance_specific
        self.cutoff = max(float(args.cutoff), 1.)
        self.cutoff_length = float(args.cutoff_length)
        self.seed = float(args.seed)
        self.pcs_parameters = pcs_parameters


if __name__ == '__main__':
    cli = WrapperCLI()
    cli.run()
