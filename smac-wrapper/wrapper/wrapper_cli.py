import sys
import re
import os
import argparse
from dataclasses import dataclass
from enum import Enum
from pcs_parse_parameters import pcs_parse_parameters
from clasp_parse_result import clasp_parse_result, ClaspResult, ClaspParseError
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

    encoding: str
    runsolver_binary: str
    memory_limit: int
    instance: str
    instance_specific: str
    cutoff: float
    cutoff_length: float
    seed: float
    pcs_parameters: [any]

    def __init__(self) -> None:
        super().__init__()
        self.parse_arguments()

    def run(self):
        result = SMAC_result(SMAC_status.TIMEOUT, self.cutoff, -1, float(sys.maxsize), self.seed)

        solver_parameters, solver = pcs_parse_parameters(self.pcs_parameters)

        if not solver:
            raise Exception('pcs parameter "--solver" is missing!')

        solver_cmd = self.build_solver_cmd(solver, solver_parameters)

        runsolver_cfg = RunsolverConfiguration(
            runsolver_bin=self.runsolver_binary,
            vsize_limit=self.memory_limit,
            wall_clock_limit=self.cutoff
        )

        output_raw = runsolver(solver_cmd, runsolver_cfg)
        output_raw_decoded = output_raw.decode('utf-8')

        try:
            output = clasp_parse_result(output_raw_decoded, quality_fn=self.calculate_quality)
        except ClaspParseError as e:
            result.status = SMAC_status.CRASHED
            raise e

        if output.status == 'SATISFIABLE' or output.status == 'OPTIMUM FOUND':
            result.status = SMAC_status.SAT
        elif output.status == "UNSATISFIABLE":
            result.status = SMAC_status.UNSAT

        result.running_time = output.running_time
        result.quality = output.quality

        print(result)

    def calculate_quality(self, clasp_json_result: str) -> float:
        try:
            values = [float(re.match(r'span\(.+?,(\d+)\)', y).group(1)) for y in filter(lambda x: x.startswith('span'), clasp_json_result['Call'][0]['Witnesses'][0]['Value'])]
        except:
            values = [sys.maxsize]
        return max(values)

    def build_solver_cmd(self, solver_binary: str, solver_parameters: [str]):
        return [solver_binary, '--outf', '2', '--quiet=1', self.encoding, self.instance] + solver_parameters

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description='smac3 <-> clingo-dl wrapper.')

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
