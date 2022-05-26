import matplotlib
import matplotlib.pyplot as plt
import re
import random
import argparse
import sys
from math import ceil


def main():
    parser = argparse.ArgumentParser(description='''
Custom gantt chart generator. The ASP lp file must contain:
    #show job/1.
    #show machine/1.
    #show setup/4.
    #show duration/3.
    #show release/3.
    #show first/2.
    #show next/3.
Example usage: clingo any.lp --quiet=1 | gantt -o gantt.png
    ''')
    random.seed(42)

    parser.add_argument('--output', '-o', help='output image file', type=str, default=None)
    parser.add_argument('--disable-text', help='disables job/release labels', action='store_true', default=False)

    args = parser.parse_args()
    if args.output:
        matplotlib.use('Agg')

    inp = ''
    for line in sys.stdin:
        # print(line, end='')
        inp += line

    try:
        inp = inp.split('Answer')[-1]
    except IndexError:
        pass

    machines = [int(m[1:]) for m in find_predicates(inp, 'machine', 1)]
    jobs = [int(j[1:]) for j in find_predicates(inp, 'job', 1)]
    releases = {(int(m[1:]), int(j[1:])): int(t) for j, m, t in find_predicates(inp, 'release', 3)}
    setups = {(int(j1[1:]), int(j2[1:]), int(m[1:])): int(t) for j1, j2, m, t in find_predicates(inp, 'setup', 4)}
    durations = {(int(m[1:]), int(j[1:])): int(t) for j, m, t in find_predicates(inp, 'duration', 3)}
    firsts = {int(m[1:]): int(j[1:]) for j, m in find_predicates(inp, 'first', 2)}
    nexts = {int(j1[1:]): int(j2[1:]) for j1, j2, m in find_predicates(inp, 'next', 3)}

    start_positions = calculate_start_positions(machines, firsts, releases, nexts, durations, setups)

    draw_gantt(start_positions, jobs, machines, releases, setups, durations, args.disable_text)

    if args.output:
        plt.savefig(args.output, dpi=300)
    else:
        plt.show()


def find_predicates(inp: str, name: str, arity=1):
    reg = re.compile('{}\({}\)'.format(name, ','.join(['([^,)]+)'] * arity)), re.IGNORECASE | re.MULTILINE)
    return re.findall(reg, inp)

def calculate_start_positions(machines, firsts, releases, nexts, durations, setups):
    # returns a tuple (start_time, setup_time, machine) for each job.
    jobs = {}
    for m in machines:
        job = firsts.get(m)
        job_before = None
        t = releases.get((m, job), 0)

        while job:  # else no further job exists on this machine.
            job_duration = durations[(m, job)]
            job_release = releases[(m, job)]
            job_setup = setups.get((job_before, job, m), 0)

            t = max(job_release, t)

            jobs[job] = (t, job_setup, m)

            t += job_setup + job_duration
            job_before = job
            job = nexts.get(job)
    return jobs

def draw_gantt(start_positions, jobs, machines, releases, setups, durations, disable_text=False):
    number_of_machines = len(machines)
    fig, ax = plt.subplots()
    max_t = 0
    bar_height = 100 / number_of_machines
    bar_margin = 10 / number_of_machines
    
    for job in jobs:
        t, job_setup, job_machine = start_positions[job]
        job_duration = durations[(job_machine, job)]
        job_release = releases[(job_machine, job)]

        x, w = (t + job_setup, job_duration)
        h = bar_height - bar_margin
        y = bar_height * job_machine - bar_height + bar_margin / 2

        ax.broken_barh([(t, job_setup)], (y, h), facecolors=(0.95, 0.95, 0.95))
        ax.broken_barh([(x, w)], (y, h), facecolors=(random.random(), 0.8, random.random()))
        if not disable_text:
            ax.text(x + w / 2, y + h / 2, '{}'.format(job), horizontalalignment='center',
                    verticalalignment='center', fontsize=7)
            ax.text(job_release, y - 5, str(job), horizontalalignment='center', verticalalignment='center', fontsize=6)
        ax.plot([job_release, job_release], [y, y + h], linewidth=0.25, color=(0.6, 0.6, 0.6))

        max_t = max(max_t, x + w)
        
    print(number_of_machines)

    ax.set_xlim(0, ceil(max_t * 1.025))
    ax.set_ylim(1, 100)
    ax.set_xlabel('time')
    ax.set_ylabel('machine')
    ax.set_yticks([bar_height * m for m in range(1, number_of_machines + 1)])
    ax.set_yticklabels([str(m) for m in range(1, number_of_machines + 1)])
    ax.grid(True)


if __name__ == '__main__':
    main()
