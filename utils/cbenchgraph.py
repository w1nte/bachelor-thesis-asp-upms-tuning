#!/usr/bin/env python

import argparse
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter


CSV_SEPARATOR = ';'

graphs = {}


def main():
    args = parse_arguments()
    df = pd.read_csv(args.csv, sep=CSV_SEPARATOR)
    for g in args.graph:
        plt.clf()
        graphs.get(g, lambda: None)(df=df)
        plt.savefig(f'{args.out}_{g}.png')


def parse_arguments() -> any:
    parser = argparse.ArgumentParser(description='Creates graphs')

    parser.add_argument('csv', type=str, help='csv input file')
    parser.add_argument('graph', nargs='+', type=str, choices=graphs.keys(), help='graph type')
    parser.add_argument('--out', '-o', type=str, default='', help='graph output name (without extension)')

    args = parser.parse_args()
    return args


def graph(name):
    def wrapper(func):
        graphs[name] = func
        return func
    return wrapper


@graph('runtime')
def runtime(df: pd.DataFrame):
    ax = plt.subplot(111)

    cids = Counter(df['CID']).keys()
    x = df[(df['CID'] == 0)]['Instance']
    w = 0.3
    for i in cids:
        y = df[(df['CID'] == i)]['Time.Total']
        ax.bar(x.keys() + w * i - len(cids) * (w/2), y, width=w, align='center')

    ax.legend(cids)
    ax.set_xlabel('instance')
    ax.set_ylabel('seconds')
    plt.xticks(x.keys(), x, rotation=15, fontsize=4)
    plt.title('Time.Total')


if __name__ == '__main__':
    main()
