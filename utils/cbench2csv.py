#!/usr/bin/env python

import argparse
import logging
import pandas as pd
import os
import re
import sys
import json
import datetime
from typing import Union


def main():
    args = parse_arguments()
    clasp_output = sys.stdin.read()

    df = clasp_result_to_dataframe(clasp_output)
    if df is not None:
        df.insert(0, 'Date', datetime.datetime.now())
        df_to_csv(df, args.csvfile)


def parse_arguments() -> any:
    parser = argparse.ArgumentParser(description='Writes the clasp output into a csv file. If the'
                                                 'csv file already exists then the data is appended.')

    parser.add_argument('csvfile', type=str, help='output csv file')

    args = parser.parse_args()
    return args


def sanitize_clasp_output(clasp_output: str) -> str:
    """
    Sanitizes the clingo/clasp output to prevent json read errors.
    """
    # remove costs and signal info because they break json_normalize
    clasp_output = re.sub(r'(\'Costs\'|"Costs"):\s?\[[^\]]*\]', '"Costs": []', clasp_output,
                          re.IGNORECASE | re.MULTILINE)
    clasp_output = clasp_output.replace('*** Info : (clingo-dl): INTERRUPTED by signal!', '')

    return clasp_output


def clasp_result_to_dataframe(clasp_output: str) -> Union[pd.DataFrame, None]:
    """
    Converts the clasp output (with parameter --outf=2) to a pandas DataFrame.
    """
    clasp_output_sanitized = sanitize_clasp_output(clasp_output)

    try:
        output_json = json.loads(clasp_output_sanitized)
    except json.decoder.JSONDecodeError:
        logging.warning('the clasp output is no valid json. Maybe the clasp parameter "--outf=2" is missing.')
        return None

    df = pd.json_normalize(output_json)

    return df


def df_to_csv(new_df: pd.DataFrame, output_csv: str, csv_separator=';') -> bool:
    """
    Writes a pandas DataFrame into a csv file. If the csv file already exists then it appends the data.
    """
    if os.path.exists(output_csv):
        # read existing csv df
        df = pd.read_csv(output_csv, sep=csv_separator, index_col=False)
        df = pd.concat([df, new_df], axis=0, ignore_index=True)
    else:
        df = new_df

    # creates a csv file if not exist, otherwise appends to the existing csv.
    df.to_csv(output_csv, mode='w+', sep=csv_separator, index=False)

    return True


if __name__ == '__main__':
    main()
