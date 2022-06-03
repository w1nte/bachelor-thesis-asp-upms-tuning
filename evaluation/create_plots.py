#!/usr/bin/env python
import os
import xdrlib
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
__ENCODINGS = {  # id: (name, file)
        'baseline': ('Baseline', '07_baseline_heuristic.lp.evaluation.csv'),
        'baseline_without_heuristic': ('Baseline without Heuristic', '00_baseline.lp.evaluation.csv'),
        'clingcon': ('Clingcon', '01_02_clingcon.lp.evaluation.csv'),
        'clingo_dl': ('Clingo-dl', '03_01_clingodl.lp.evaluation.csv'),
        'heuristic': ('Heuristic', '09_01_clingodl_heuristic.lp.evaluation.csv'),
        'heuristic_param_tuning': ('Heuristic + Parameter Tuning', '10_01_clingodl_heuristic_smac.lp.evaluation.csv'),
        'next': ('Next', '05_01_clingodl_next.lp.evaluation.csv'),
        'slots': ('Slots', '06_01_clingodl_slots.lp.evaluation.csv'),
        'constraints': ('Constraints', '02_02_clingodl_more_constraints.lp.evaluation.csv'),
        'constraints_heuristic': ('Constraints + Heuristic', '04_05_clingodl_more_constraints_heuristic.lp.evaluation.csv'),
        'boundary': ('Boundary', '08_06_clingodl_boundary.lp.evaluation.csv'),
        'boundary_with_horizon': ('Boundary with Horizon', '08_06_clingodl_boundary_modified_horizon.lp.evaluation.csv'),
        'encoding_tuning': ('Encoding Tuning', '11_smac_optimized.lp.evaluation.csv'),
        'encoding_tuning_two': ('Encoding Tuning v2', '12_smac_optimized_v2.lp.evaluation.csv')
    }


def main():
    clear_plot_folder()
    generate_latex_commands()

    experiments_all = __ENCODINGS.keys()

    experiments_90_percent_feasible = [
        'baseline', 
        'clingo_dl', 
        'heuristic', 
        'heuristic_param_tuning', 
        'next', 
        'slots', 
        'constraints_heuristic', 
        'boundary', 
        'encoding_tuning', 
        'encoding_tuning_two', 
    ]

    experiments_all_feasible = [
        'clingo_dl', 
        'heuristic', 
        'heuristic_param_tuning', 
        'encoding_tuning', 
        'encoding_tuning_two', 
    ]

    experiments_best = [
        'baseline', 
        'heuristic', 
        'heuristic_param_tuning', 
        'encoding_tuning', 
        'encoding_tuning_two', 
    ]

    files, index, frames = load_experiments(experiments_all)
    instances = extract_instances(frames[0])
    best_worst = determine_best_worst_makespan(index, frames)
    encoding_results = determine_encoding_results(index, frames)

    save_table(pd.concat([instances['instance'], best_worst.rename(columns={
        'best_encoding_makespan': 'best makespan', 
        'worst_encoding_makespan': 'worst makespan',
        'best_encodings': 'best encodings',
        'worst_encodings': 'worst encodings',
        'best_encoding_result': 'best result'
    })], axis=1), 'all_instances')

    save_table(pd.concat([instances['instance'], encoding_results], axis=1), 'all_encoding_results')

    print('Number of optimal results: {}'.format(best_worst[best_worst['best_encoding_result'] == 'OPTIMAL'].shape[0]))
    print('Number of feasible results: {}'.format(best_worst[best_worst['best_encoding_result'] == 'FEASIBLE'].shape[0]))
    print('Number of low dedication instances: {}'.format(instances[instances['dedication'] == 'L'].shape[0]))
    print('Number of high dedication instances: {}'.format(instances[instances['dedication'] == 'H'].shape[0]))

    plot_bar('all', 'All Instances', frames, files, index)

    
    # UpSet plot 1
    df = pd.concat([instances, encoding_results], axis=1)
    for i, encoding in enumerate(index):
        df = df.set_index(df[encoding] != ' ', append=(i!=0))
    df['dedication'] = df['dedication'].replace('H', 'high dedication').replace('L', 'low dedication')
    plt.clf()
    upset = upsetplot.UpSet(df, intersection_plot_elements=0, max_subset_size=600, show_counts=True, element_size=35)
    upset.add_stacked_bars(by="dedication", colors=cm.Accent, title="instances", elements=8)
    upset.style_subsets(absent=["Baseline"], facecolor="gray", label="Better than baseline")
    upset.add_catplot(value='machines', kind='box', color='violet')
    upset.add_catplot(value='jobs', kind='box', color='red')
    upset.plot()
    plt.title("Intersections of feasible instances")
    save_plot('upset_all_feasible')


    files, index, frames = load_experiments(experiments_90_percent_feasible)
    plot_boxplot('boxplot_encodings_min_450_feasible', '/ Makespan (Relative Difference)', frames, files, index, best_worst)

    
    files, index, frames = load_experiments(experiments_all_feasible)
    plot_boxplot('boxplot_encodings_all_feasible', '/ Makespan (Relative Difference)', frames, files, index, best_worst)


    files, index, frames = load_experiments(experiments_best)
    plot_boxplot('boxplot_best_encodings_against_baseline', '/ Makespan (Relative Difference)', frames, files, index, best_worst)

    # UpSet plot 2
    encoding_results = determine_encoding_results(index, frames)
    df = pd.concat([instances, encoding_results], axis=1)
    for i, encoding in enumerate(index):
        df = df.set_index(df[encoding] == 'o', append=(i!=0))
    df['dedication'] = df['dedication'].replace('H', 'high dedication').replace('L', 'low dedication')
    plt.clf()
    upset = upsetplot.UpSet(df, intersection_plot_elements=0, max_subset_size=300, show_counts=True, element_size=35)
    upset.add_stacked_bars(by="dedication", colors=cm.Accent, title="instances", elements=8)
    upset.add_catplot(value='machines', kind='box', color='violet')
    upset.add_catplot(value='jobs', kind='box', color='red')
    upset.style_subsets(absent=["Baseline"], facecolor="gray", label="Better than baseline")
    upset.plot()
    plt.title("Intersections of optimal instances")
    save_plot('upset_best_encodings_against_baseline_optimal')



def load_experiments(list_of_experiments):
    # load all experiment results and prepare dataframes

    experiments = {__ENCODINGS[k][0]: __ENCODINGS[k][1] for k in list_of_experiments}

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


def generate_latex_commands():
    to_camel_case = lambda x: ''.join(y.title() for y in x.split('_'))
    with open(f'{__PLOT_FOLDER}/enc_commands.tex', 'w+') as f:
        f.write('\n'.join([f'\\newcommand{{\\enc{to_camel_case(key)}}}{{{__ENCODINGS[key][0]}}}' for key in __ENCODINGS.keys()]))


def extract_instances(frame):
    df = pd.concat([
        frame['instance'].apply(lambda x: '.'.join(x.split('.')[:-1])), 
        frame['machines'], 
        frame['jobs'], 
        frame['dedication']
    ], axis=1)

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


def save_table(df, filename):
    if LATEX_PLOT:
        df.to_latex(f'{__PLOT_FOLDER}{filename}.tex', longtable=True)
    else:
        df.to_csv(f'{__PLOT_FOLDER}{filename}.csv', sep=';')


def determine_best_worst_makespan(index, frames):
    all_best_makespans = pd.concat([df['best_makespan'] for df in frames], axis=1, join='inner', keys=index)

    df_best_makespan = all_best_makespans.min(axis=1).apply(int)
    df_worst_makespan = all_best_makespans.max(axis=1).apply(int)

    all_best_makespans_is_best = all_best_makespans.apply(lambda x: x == df_best_makespan, axis=0)
    df_best_encodings = all_best_makespans_is_best.agg(lambda s: s.index[s].values, axis=1)

    all_best_makespans_is_worst = all_best_makespans.apply(lambda x: x == df_worst_makespan, axis=0)
    df_worst_encodings = all_best_makespans_is_worst.agg(lambda s: s.index[s].values, axis=1)

    best_encoding_result = pd.concat(
        [pd.concat([df['best_makespan'] for df in frames], axis=1, join='inner', keys=range(0, len(index))).idxmin(axis=1)]
        + [df['result'] for df in frames], axis=1, join='inner', keys=['best_encoding'] + list(index)).apply(lambda x: x[1:][int(x[0])], axis=1)

    df_best_and_worst = pd.concat([
        df_best_makespan, 
        df_worst_makespan,
        df_best_encodings,
        df_worst_encodings,
        best_encoding_result
    ], axis=1, join='inner', keys=(
        'best_encoding_makespan',
        'worst_encoding_makespan',
        'best_encodings',
        'worst_encodings',
        'best_encoding_result'
    ))
    return df_best_and_worst


def determine_encoding_results(index, frames):
    df = pd.concat([df['result'] for df in frames], axis=1, join='inner', keys=index)

    df = df.replace('OPTIMAL', 'o').replace('FEASIBLE', 'x').replace('UNFEASIBLE', ' ')

    return df
    

def plot_bar(filename, title, dfs, files, index):
    all_best_makespans = pd.concat([df['best_makespan'] for df in dfs], axis=1, keys=files, join='inner')
    best_makespan_per_instance = all_best_makespans.min(axis=1)
    all_best_makespans_is_best = all_best_makespans.apply(lambda x: x == best_makespan_per_instance, axis=0)

    # count results
    results = [df['result'].value_counts() for df in dfs]
    g_result = lambda x: [(r[x] if x in r else 0) for r in results]

    optimal = g_result('OPTIMAL')
    feasible = [sum(x) for x in zip(optimal, g_result('FEASIBLE'))]  # sum up feasible with optimal (optimal is a subset of feasible)
    best = [all_best_makespans_is_best[f].value_counts()[1] for f in files]

    df = pd.DataFrame({
        'optimal': optimal,
        'feasible': feasible,
        'best': best
    }, index=index).sort_values(by=['best'])

    plt.clf()
    fig, ax = plt.subplots(figsize=(6, 5))
    df.plot.bar(ax=ax)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha='right')
    plt.title(title)
    plt.xticks(fontsize=5)
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
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha='right')
    plt.title(f'Relative difference to the best solution')
    plt.xticks(fontsize=5)
    plt.tight_layout()

    save_plot(filename)


if __name__ == '__main__':
    main()
