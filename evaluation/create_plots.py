#!/usr/bin/env python
import os
import pandas as pd
from glob import glob
import sys
import numpy as np
import matplotlib as mpl
import upsetplot
from matplotlib import cm


LATEX_PLOT = len(sys.argv) > 1 and sys.argv[1] == 'latex'
if LATEX_PLOT:
    print('pgf plot')
    mpl.use('pgf')
import matplotlib.pyplot as plt

if LATEX_PLOT:
    plt.style.use(['science'])
    plt.rcParams.update({
        "pgf.texsystem": "pdflatex",
        "figure.figsize": (6, 4),
        "font.size" : 8,
    })
else:
    plt.style.use('default')

__PLOT_FOLDER = './plots/'
__RESULTS_FOLDER = './results/'


def main():
    clear_plot_folder()

    files, index, frames = load_experiments({
        'baseline': '07_baseline_heuristic.lp.evaluation.csv',
        'baseline without heuristics': '00_baseline.lp.evaluation.csv',
        'clingcon': '01_02_clingcon.lp.evaluation.csv',
        'clingo-dl': '03_01_clingodl.lp.evaluation.csv',
        'clingo-dl with heuristic': '09_01_clingodl_heuristic.lp.evaluation.csv',
        'clingo-dl with heuristic and smac-optimization': '10_01_clingodl_heuristic_smac.lp.evaluation.csv',
        'clingo-dl with pure next relation': '05_01_clingodl_next.lp.evaluation.csv',
        'clingo-dl with slots': '06_01_clingodl_slots.lp.evaluation.csv',
        'clingo-dl with more constraints': '02_02_clingodl_more_constraints.lp.evaluation.csv',
        'clingo-dl with more constraints and heuristic': '04_05_clingodl_more_constraints_heuristic.lp.evaluation.csv',
        'clingo-dl with clingo optimization': '08_06_clingodl_boundary.lp.evaluation.csv',
        'clingo-dl with clingo optimization and modified horizon': '08_06_clingodl_boundary_modified_horizon.lp.evaluation.csv',
        'clingo-dl with smac encoding': '11_smac_optimized.lp.evaluation.csv',
        'clingo-dl with smac encoding v2': '12_smac_optimized_v2.lp.evaluation.csv'
    })


    instances = extract_instances(frames[0])
    best_worst = determine_best_worst_makespan(index, frames)
    encoding_results = determine_encoding_results(index, frames)

    pd.concat([instances, best_worst], axis=1).to_csv(__PLOT_FOLDER + 'all_instances.csv', sep=';')
    pd.concat([instances['instance'], encoding_results], axis=1).to_csv(__PLOT_FOLDER + 'all_encoding_results.csv', sep=';')

    print('OPTIMAL results: {}'.format(best_worst[best_worst['best_encoding_result'] == 'OPTIMAL'].shape[0]))
    print('FEASIBLE results: {}'.format(best_worst[best_worst['best_encoding_result'] == 'FEASIBLE'].shape[0]))

    plot_bar('all', 'All Instances', frames, files, index)

    
    df = pd.concat([instances, encoding_results], axis=1)
    for i, encoding in enumerate(index):
        df = df.set_index(df[encoding] != ' ', append=(i!=0))
    df['dedication'] = df['dedication'].replace('H', 'High dedication').replace('L', 'Low dedication')
    plt.clf()
    upset = upsetplot.UpSet(df, intersection_plot_elements=0, max_subset_size=600, show_counts=True, element_size=20)
    upset.add_stacked_bars(by="dedication", colors=cm.Pastel1, title="instances", elements=8)
    upset.style_subsets(absent=["baseline"], facecolor="gray", label="Better than baseline")
    upset.add_catplot(value='machines', kind='box', color='violet')
    upset.add_catplot(value='jobs', kind='box', color='red')
    fig = plt.figure(figsize=(7, 12))
    upset.plot(fig=fig)
    plt.title("Intersections of feasible instances")
    save_plot('upset_all_feasible')


    # encodings with at least 90% (450) feasible
    files, index, frames = load_experiments({
        'baseline': '07_baseline_heuristic.lp.evaluation.csv',
        #'baseline without heuristics': '00_baseline.lp.evaluation.csv',
        #'clingcon': '01_02_clingcon.lp.evaluation.csv',
        'clingo-dl': '03_01_clingodl.lp.evaluation.csv',
        'clingo-dl\n with\n heuristic': '09_01_clingodl_heuristic.lp.evaluation.csv',
        'clingo-dl\n with\n heuristic and smac-optimization': '10_01_clingodl_heuristic_smac.lp.evaluation.csv',
        'clingo-dl\n with\n pure next relation': '05_01_clingodl_next.lp.evaluation.csv',
        'clingo-dl\n with\n slots': '06_01_clingodl_slots.lp.evaluation.csv',
        #'clingo-dl with more constraints': '02_02_clingodl_more_constraints.lp.evaluation.csv',
        'clingo-dl\n with\n more constraints and heuristic': '04_05_clingodl_more_constraints_heuristic.lp.evaluation.csv',
        'clingo-dl\n with\n clingo optimization': '08_06_clingodl_boundary.lp.evaluation.csv',
        #'clingo-dl with clingo optimization and modified horizon': '08_06_clingodl_boundary_modified_horizon.lp.evaluation.csv',
        'clingo-dl\n with\n smac encoding': '11_smac_optimized.lp.evaluation.csv',
        'clingo-dl\n with\n smac encoding v2': '12_smac_optimized_v2.lp.evaluation.csv',
    })
    plot_boxplot('boxplot_encodings_min_450_feasible', '/ Makespan (Relative Difference)', frames, files, index, best_worst)

    # encodings with 100% feasible
    files, index, frames = load_experiments({
        'clingo-dl': '03_01_clingodl.lp.evaluation.csv',
        'clingo-dl\n with\n heuristic': '09_01_clingodl_heuristic.lp.evaluation.csv',
        'clingo-dl\n with\n heuristic and smac-optimization': '10_01_clingodl_heuristic_smac.lp.evaluation.csv',
        'clingo-dl\n with\n smac encoding': '11_smac_optimized.lp.evaluation.csv',
        'clingo-dl\n with\n smac encoding v2': '12_smac_optimized_v2.lp.evaluation.csv'
    })
    plot_boxplot('boxplot_encodings_all_feasible', '/ Makespan (Relative Difference)', frames, files, index, best_worst)

    # 3 best encodings against baseline
    files, index, frames = load_experiments({
        'clingo-dl\n with\n heuristic': '09_01_clingodl_heuristic.lp.evaluation.csv',
        'clingo-dl with smac encoding': '11_smac_optimized.lp.evaluation.csv',
        'clingo-dl\n with\n smac encoding v2': '12_smac_optimized_v2.lp.evaluation.csv',
        'baseline': '07_baseline_heuristic.lp.evaluation.csv',
    })
    plot_boxplot('boxplot_best_encodings_against_baseline', '/ Makespan (Relative Difference)', frames, files, index, best_worst)


    # 3 best encodings against baseline
    files, index, frames = load_experiments({
        'clingo-dl with heuristic': '09_01_clingodl_heuristic.lp.evaluation.csv',
        'clingo-dl with smac encoding': '11_smac_optimized.lp.evaluation.csv',
        'clingo-dl with smac encoding v2': '12_smac_optimized_v2.lp.evaluation.csv',
        'baseline': '07_baseline_heuristic.lp.evaluation.csv',
    })

    encoding_results = determine_encoding_results(index, frames)
    df = pd.concat([instances, encoding_results], axis=1)
    for i, encoding in enumerate(index):
        df = df.set_index(df[encoding] == 'o', append=(i!=0))
    df['dedication'] = df['dedication'].replace('H', 'High dedication').replace('L', 'Low dedication')
    plt.clf()
    upset = upsetplot.UpSet(df, intersection_plot_elements=0, max_subset_size=300, show_counts=True, element_size=None)
    upset.add_stacked_bars(by="dedication", colors=cm.Pastel1, title="instances", elements=4)
    upset.add_catplot(value='machines', kind='box', color='violet')
    upset.add_catplot(value='jobs', kind='box', color='red')
    upset.style_subsets(absent=["baseline"], facecolor="gray", label="Better than baseline")
    fig = plt.figure(figsize=(6, 8))
    upset.plot(fig=fig)
    plt.title("Intersections of optimal instances")
    save_plot('upset_best_encodings_against_baseline_optimal')



def load_experiments(experiments):
    # load all experiment results and prepare dataframe

    # all input files (output from evaluate.py)
    files = experiments.values()
    # x-axis, must have the same order as files
    index = experiments.keys()

    frames = []
    for filename in files:
        df = pd.read_csv(__RESULTS_FOLDER + filename, sep=';', index_col=None, header=0)

        # extract instance infos
        df['machines'] = [int(i.split('_')[1]) for i in df['instance']]
        df['jobs'] = [int(i.split('_')[2]) for i in df['instance']]  
        df['dedication'] = [i.split('_')[3][0] for i in df['instance']]
        # extract best (minimal) makespan
        df['best_makespan'] = [m[1:-1].split(',').pop() for m in df['makespans']]
        df['best_makespan'] = [(int(m) if m else np.nan) for m in df['best_makespan']]
        # extract worst (maximal) makespan
        df['worst_makespan'] = [m[1:-1].split(',').pop(0) for m in df['makespans']]
        df['worst_makespan'] = [(int(m) if m else np.nan) for m in df['worst_makespan']]

        frames.append(df)

    return files, index, frames


def extract_instances(frame):
    df = pd.concat([frame['instance'].apply(lambda x: '.'.join(x.split('.')[:-1])), frame['machines'], frame['jobs'], frame['dedication']], axis=1)
    return df


def clear_plot_folder():
    if not os.path.isdir(__PLOT_FOLDER):
        os.mkdir(__PLOT_FOLDER)
    plot_files = glob(os.path.join(__PLOT_FOLDER, '*'))
    [os.remove(f) for f in plot_files]  # clear plot folder


def save_plot(filename):
    if LATEX_PLOT:
        plt.savefig(f'{__PLOT_FOLDER}{filename}.pgf', format='pgf')
    else:
        plt.savefig(f'{__PLOT_FOLDER}{filename}.png', format='png', dpi=200)


def determine_best_worst_makespan(index, frames):
    df_best_makespan = pd.concat([df['best_makespan'] for df in frames], axis=1, join='inner').min(axis=1).apply(int)
    df_worst_makespan = pd.concat([df['best_makespan'] for df in frames], axis=1, join='inner').max(axis=1).apply(int)

    df_best_encoding = pd.concat([df['best_makespan'] for df in frames], axis=1, join='inner', keys=index).idxmin(axis=1)
    df_worst_encoding = pd.concat([df['best_makespan'] for df in frames], axis=1, join='inner', keys=index).idxmax(axis=1)

    best_encoding_result = pd.concat(
        [pd.concat([df['best_makespan'] for df in frames], axis=1, join='inner', keys=range(0, len(index))).idxmin(axis=1)]
        + [df['result'] for df in frames], axis=1, join='inner', keys=['best_encoding'] + list(index)).apply(lambda x: x[1:][int(x[0])], axis=1)

    df_best_and_worst = pd.concat([
        df_best_makespan, 
        df_worst_makespan,
        df_best_encoding,
        df_worst_encoding,
        best_encoding_result
    ], axis=1, join='inner', keys=(
        'best_encoding_makespan',
        'worst_encoding_makespan',
        'best_encoding',
        'worst_encoding',
        'best_encoding_result'
    ))
    return df_best_and_worst


def determine_encoding_results(index, frames):
    df = pd.concat([df['result'] for df in frames], axis=1, join='inner', keys=index)

    df = df.replace('OPTIMAL', 'o').replace('FEASIBLE', 'x').replace('UNFEASIBLE', ' ')

    return df
    

def plot_bar(filename, title, dfs, files, index):
    # count the number of best makespan for each encoding, ignores rows where all approaches did not find any schedule.
    best = pd.concat([df['best_makespan'] for df in dfs], axis=1, keys=files, join='inner').dropna(how='all').idxmin(axis=1, skipna=True).value_counts()
    # count results
    results = [df['result'].value_counts() for df in dfs]
    g_result = lambda x: [(r[x] if x in r else 0) for r in results]

    optimal = g_result('OPTIMAL')
    feasible = [sum(x) for x in zip(optimal, g_result('FEASIBLE'))]  # sum up feasible with optimal (optimal is a subset of feasible)
    best = [(best[f] if f in best else 0) for f in files]

    df = pd.DataFrame({
        'optimal': optimal,
        'feasible': feasible,
        'best': best
    }, index=index)

    plt.clf()
    fig, ax = plt.subplots(figsize=(6, 5))
    df.plot.bar(ax=ax)
    ax.tick_params(axis='x', rotation=15)
    plt.title(title)
    plt.xticks(fontsize=5)
    plt.tight_layout()
    plt.grid()

    save_plot(filename)


def plot_jobs(filename, title, dfs, files, index):
    dfs = [df.sort_values(by='jobs') for df in dfs]

    # determine optimal makespan
    dfs_results = [df[['result', 'best_makespan']] for df in dfs]
    for df in dfs_results:
        df.loc[df['result'] != 'OPTIMAL', 'best_makespan'] = np.nan
    df_optimal = pd.concat([df['best_makespan'] for df in dfs_results], axis=1, join='inner').min(axis=1)

    df = pd.concat([dfs[0]['jobs']] + [df['best_makespan'] for df in dfs] + [df_optimal], axis=1, keys=['jobs'] + list(index) + ['optimal'], join='inner')

    plt.clf()
    fig, ax = plt.subplots(figsize=(6, 5))
    df.set_index('jobs').plot(style=['o'] * len(index) + ['xy'], linewidth=1, markersize=2.5, ax=ax)
    plt.title(title)
    plt.legend(fontsize=6)
    plt.tight_layout()
    plt.grid()

    save_plot(filename)


def plot_boxplot(filename, title, frames, files, index, df_best_and_worst):
    # df_best_and_worst = determine_best_worst_makespan(index, frames)
    new_frames = []
    for df in frames:
        # determine relative difference
        new_df = pd.concat([df, df_best_and_worst], axis=1, join='inner')
        new_df['relative_difference'] = (new_df['best_makespan'] - new_df['best_encoding_makespan']) / new_df['best_encoding_makespan']
        new_frames.append(new_df)

    df_relative_difference = pd.concat([df['relative_difference'] for df in new_frames], axis=1, join='inner', keys=index)

    # sort columns by median
    meds = df_relative_difference.median()
    meds.sort_values(ascending=True, inplace=True)
    df_relative_difference = df_relative_difference[meds.index]

    plt.clf()
    fig, ax = plt.subplots(figsize=(6, 5))
    boxplot = df_relative_difference.boxplot(ax=ax)
    plt.title(f'Relative difference to the best solution')
    plt.xticks(fontsize=5)
    plt.tight_layout()

    save_plot(filename)


if __name__ == '__main__':
    main()
