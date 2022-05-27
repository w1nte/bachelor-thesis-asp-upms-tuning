#!/usr/bin/env python
import argparse
import os
import glob
import json
import re
import pandas as pd
import logging
from dataclasses import dataclass
from typing import List
from enum import Enum


@dataclass
class EvaluationResult:
    instance: str
    makespans: List[int]
    result: str = 'UNSATISFIABLE'
    models: int = 0
    models_more: bool = False
    time_total: float = .0
    time_unsat: float = .0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('experiment', type=str)
    parser.add_argument('solver', choices=['clingo', 'clingo-dl', 'clingcon'], default='clingo', type=str)
    args = parser.parse_args()

    files = glob.glob(os.path.join('experiments/', os.path.join(args.experiment, '*.out')))
    files.sort(key=lambda x: int(os.path.basename(x).split('_')[0]))

    data = []
    
    for f in files:
        with open(f, 'r') as fh:
            file_content = fh.read()
            if args.solver == 'clingo-dl':
                d = parse_clingodl(os.path.basename(f), file_content)
            elif args.solver == 'clingcon':
                d = parse_clingcon(os.path.basename(f), file_content)
            else:
                d = parse_clingo(os.path.basename(f), file_content)
            data.append(d)

    df = pd.DataFrame(data)
    df.to_csv(f'results/{args.experiment}.evaluation.csv', sep=';')
    print(df)


def parse_json_result(filename, file_content):
    f_json = {}
    try:
        f_json = json.loads(file_content)
    except json.JSONDecodeError:
        logging.error(f'{filename} was not a valid json file!')
    return f_json


def parse_clingodl(filename, file_content):
    result = EvaluationResult(instance=filename, makespans=[])

    f_json = parse_json_result(filename, file_content)

    try:
        result.models = int(f_json['Models']['Number'])
        result.models_more = f_json['Models']['More'] == 'yes'
        result.time_total = float(f_json['Time']['Total'])
        result.time_unsat = float(f_json['Time']['Unsat'])
        result.makespans = [int(m) for m in re.findall(r'dl\(makespan,(\d+)\)', file_content)]
    except Exception as e:
        print(filename)
        raise e

    if result.models_more:
        if result.models > 0:
            result.result = 'FEASIBLE'
        else:
            result.result = 'UNFEASIBLE'
    else:
        if result.models > 0:
            result.result = 'OPTIMAL'
        else:
            result.result = 'UNSAT'

    return result


def parse_clingcon(filename, file_content):
    result = EvaluationResult(instance=filename, makespans=[])

    f_json = parse_json_result(filename, file_content)

    try:
        result.models = int(f_json['Models']['Number'])
        result.models_more = f_json['Models']['More'] == 'yes'
        result.time_total = float(f_json['Time']['Total'])
        result.time_unsat = float(f_json['Time']['Unsat'])
        result.makespans = [int(m) for m in re.findall(r'__csp_cost\(\\"(\d+)\\"\)', file_content)]
    except Exception as e:
        print(filename)
        raise e

    if result.models_more:
        if result.models > 0:
            result.result = 'FEASIBLE'
        else:
            result.result = 'UNFEASIBLE'
    else:
        if result.models > 0:
            result.result = 'OPTIMAL'
        else:
            result.result = 'UNSAT'

    return result


def parse_clingo(filename, file_content):
    result = EvaluationResult(instance=filename, makespans=[])
    return result


if __name__ == '__main__':
    main()
