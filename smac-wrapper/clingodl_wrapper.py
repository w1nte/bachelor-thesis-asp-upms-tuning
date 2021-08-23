#!/usr/bin/env python
from wrapper.wrapper_cli import WrapperCLI, SMAC_status, SMAC_result
import sys


class ClingoDLWrapper(WrapperCLI):
    def __init__(self) -> None:
        super().__init__()

    def determine_SMAC_status(self, clasp_json: any, result: SMAC_result):
        models = int(clasp_json['Models']['Number'])
        models_more = clasp_json['Models']['More']
        if models == 0 and models_more == 'no':
            result.status = SMAC_status.UNSAT
        elif models > 0:
            result.status = SMAC_status.SAT

    def determine_solution_quality(self, clasp_json: any, result: SMAC_result):
        try:
            values = [self._MAX_QUALITY] + [float(n) for n in re.findall(r'makespan,(\d+)', str(clasp_json_result))]
        except:
            values = [self._MAX_QUALITY]
        result.quality = min(values)


if __name__ == '__main__':
    cli = ClingoDLWrapper()
    cli.run()