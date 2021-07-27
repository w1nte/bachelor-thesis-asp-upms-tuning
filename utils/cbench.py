#!/usr/bin/env python

import argparse
import sys
import subprocess
import logging
import pandas as pd
import re
import os
import time
import datetime
from cbench2csv import clasp_result_to_dataframe, df_to_csv
from typing import Union


REQUIRED_CLASP_PARAMETERS = ['--outf=2', '--quiet']


def main():
    args = parse_arguments()

    commands = extract_commands(args.commands_or_files)
    number_of_commands = len(commands) * len(args.instances)
    counter = 0

    print(f'Start clasp benchmark.')
    for cid, command in enumerate(commands):
        for instance in args.instances:
            if counter >= (args.start_at - 1):
                start_time = time.time()
                command_with_instance = build_command(command, instance)

                print(f'{counter+1}/{number_of_commands} "{command_with_instance}"', end='')
                df = benchmark(command, instance)

                execution_time = round((time.time() - start_time) * 100) / 100
                if df is not None:
                    print(f'\tfinished after {execution_time} seconds.')
                    df.insert(0, 'ID', counter)
                    df.insert(1, 'Date', datetime.datetime.fromtimestamp(start_time))
                    df.insert(2, 'CID', cid)

                    df_to_csv(df, args.csv)
                else:
                    logging.error(f'benchmark {counter+1} "{command_with_instance}" failed.')
            counter += 1


def parse_arguments() -> any:
    parser = argparse.ArgumentParser(description='Run Benchmarks for Clingo (Clasp)')

    parser.add_argument('commands_or_files', nargs='+', type=str, help='clingo/clasp commands')
    parser.add_argument('--instances', '-i', nargs='+', type=str, help='instance files')
    parser.add_argument('--csv', '-c', default='out.csv', type=str, help='output csv file')
    parser.add_argument('--start-at', default=0, type=int, help='skip all commands until this number')

    args = parser.parse_args()
    return args


def execute_command(command: str) -> str:
    """
    Executes the command in the shell.
    """
    proc = subprocess.Popen(command,
                            shell=True,
                            stderr=sys.stderr,
                            stdout=subprocess.PIPE
                            )
    output, _ = proc.communicate()
    output_decoded = output.decode('utf-8')

    return output_decoded


def sanitize_clasp_output(command_output: str) -> str:
    """
    Sanitizes the clingo/clasp output to prevent json read errors.
    """
    # remove costs and signal info because they break json_normalize
    command_output = re.sub(r'(\'Costs\'|"Costs"):\s?\[[^\]]*\]', '"Costs": []', command_output, re.IGNORECASE | re.MULTILINE)
    command_output = command_output.replace('*** Info : (clingo-dl): INTERRUPTED by signal!', '')

    return command_output


def build_command(command: str, instance: str) -> str:
    """
    Build a clingo/clasp command with all required parameters.
    """
    command_with_instance = command + f' {instance}'

    for c in REQUIRED_CLASP_PARAMETERS:
        if c not in command:
            command_with_instance += f' {c}'

    return command_with_instance


def benchmark(command: str, instance: str) -> Union[pd.DataFrame, None]:
    """
    Benchmark a clingo/clasp command/instance and write it to a pandas DataFrame.
    """
    command_with_instance = build_command(command, instance)

    clasp_output = sanitize_clasp_output(execute_command(command_with_instance))

    df = clasp_result_to_dataframe(clasp_output)
    if df is not None:
        df.insert(0, 'Instance', instance)
        df.insert(1, 'Command', command_with_instance)

    return df


def extract_commands(commands_or_files: [str]) -> [str]:
    """
    Extract all commands from a list of commands and files containing commands.
    """
    commands = []
    for cf in commands_or_files:
        if os.path.isfile(cf) and not os.access(cf, os.X_OK):
            with open(cf, 'r') as f:
                for line in f.readlines():
                    commands.append(line)
        else:
            commands.append(cf)

    return commands


if __name__ == '__main__':
    main()
