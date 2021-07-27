import matplotlib
import matplotlib.pyplot as plt
import re
import random
import argparse
import sys


def find_predicates(inp: str, name: str, arity=1):
    reg = re.compile('{}\({}\)'.format(name, ','.join(['([^,)]+)'] * arity)), re.IGNORECASE | re.MULTILINE)
    return re.findall(reg, inp)


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
    #show span/2.
Example usage: clingo any.lp --quiet=1 | python gantt.py -o gantt.png
    ''')

    parser.add_argument('--output', '-o', help='output gantt graph image', type=str, default=None)

    args = parser.parse_args()
    if args.output:
        matplotlib.use('Agg')

    inp = ''
    for line in sys.stdin:
        print(line, end='')
        inp += line

    machines = [int(m[1:]) for m in find_predicates(inp, 'machine', 1)]
    jobs = [int(j[1:]) for j in find_predicates(inp, 'job', 1)]
    releases = {(int(m[1:]), int(j[1:])): int(t) for j, m, t in find_predicates(inp, 'release', 3)}
    durations = {(int(m[1:]), int(j[1:])): int(t) for j, m, t in find_predicates(inp, 'duration', 3)}
    firsts = {int(m[1:]): int(j[1:]) for j, m in find_predicates(inp, 'first', 2)}
    nexts = {int(j1[1:]): int(j2[1:]) for j1, j2, m in find_predicates(inp, 'next', 3)}
    setups = {(int(j1[1:]), int(j2[1:]), int(m[1:])): int(t) for j1, j2, m, t in find_predicates(inp, 'setup', 4)}
    spans = {int(m[1:]): int(t) for m, t in find_predicates(inp, 'span', 2)}
    max_time = max(spans.values())

    number_of_machines = len(machines)

    bar_height = 100 / (number_of_machines + 1)
    bar_margin = 100 / (number_of_machines + 4)
    
    fig, ax = plt.subplots()
    ax.set_xlim(0, max_time)
    ax.set_ylim(1, 100)
    ax.set_xlabel('time')
    ax.set_ylabel('machine')
    ax.set_yticks([bar_height * m for m in range(1, number_of_machines + 1)])
    ax.set_yticklabels([str(m) for m in range(1, number_of_machines + 1)])
    ax.grid(True)

    for m in machines:
        job = firsts.get(m)
        t = releases.get((m, job), 0)

        while job:  # else no further job exists on this machine.
            job_next = nexts.get(job)
            job_duration = durations[(m, job)]
            job_release = releases[(m, job)]

            t = max(t, job_release)

            x, w = (t, job_duration)
            h = bar_height - bar_margin
            y = bar_height * m - h / 2

            ax.broken_barh([(x, w)], (y, h), facecolors=(random.random(), 0.8, random.random()),
                           edgecolors=(0.4, 0.4, 0.4))
            ax.text(x + w / 2, y + h / 2, '{}'.format(job), horizontalalignment='center',
                    verticalalignment='center', fontsize=7)
            ax.text(job_release, y - 5, str(job), horizontalalignment='center', verticalalignment='center', fontsize=6)
            ax.plot([job_release, job_release], [y, y + h], linewidth=2, color=(0, 0, 0))

            t += job_duration + setups.get((job, job_next, m), 500)
            job = job_next

    if args.output:
        plt.savefig(args.output, dpi=300)
    else:
        plt.show()


if __name__ == '__main__':
    main()
