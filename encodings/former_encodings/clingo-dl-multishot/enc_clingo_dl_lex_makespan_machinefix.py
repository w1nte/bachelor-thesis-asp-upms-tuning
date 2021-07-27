#!/usr/bin/env python3

# 
# Requirements:
# - PYTHONPATH must contain module clingo
# - Dynamically linked library of clingo-dl must be found by ctypes.util.find_library
# - PYTHONPATH must contain module theory from https://github.com/potassco/tefoli
# 



__version__ = '0.0.2'



import argparse

from clingo import Control
from clingo import Function
from clingo import __version__ as clingo_version

from collections import defaultdict

import ctypes

import os

import re

import sys

import theory

import threading

import time



class TimeKeep:
    
    def get_current_time(self):
        return time.time()
    
    def __init__(self):
        self.start_time = self.get_current_time()
        self.last_time = self.start_time
    
    def time_total(self):
        return (self.get_current_time() - self.start_time)
    
    def time_stage(self):
        current_time = self.get_current_time()
        result = ((current_time - self.start_time), (current_time - self.last_time), )
        self.last_time = current_time
        return result



class PerLevel:
    
    def __init__(self, *args):
        self.timeouts = list(args)
    
    def get_timeouts(self, machine_count):
        return self.timeouts
    
    def __repr__(self):
        return 'PerLevel({})'.format(','.join(map(str, self.timeouts)))


class Geometric:
    
    def __init__(self, timeout, ratio):
        self.timeout = timeout
        self.ratio = ratio
    
    def get_timeouts(self, machine_count):
        if machine_count <= 1:
            return [self.timeout]
        # else
        result = [self.timeout * self.ratio**(i+1) for i in range(machine_count-1)]
        return result + [self.timeout - sum(result)]
    
    def __repr__(self):
        return 'Geometric({},{})'.format(self.timeout, self.ratio)



RE_MACHINE_OR_JOB = re.compile(r'(?P<predicate>machine|job)\((?P<constant>[^)]+)\)\.')



# From https://github.com/joetsch/Scheduling/blob/master/encodings/pmsp/clingo-dl/enc_clingo-dl_makespan_v2.lp
BASE_PROGRAM = (
        'base',
        [],
        '''


% assign jobs to capable machines
1 { assigned(J,M) : capable(M,J) } 1 :- job(J).

% pick first and last job for each 
1 { first(J,M) : assigned(J,M) } 1 :- assigned(_,M).
1 { last(J,M) : assigned(J,M) } 1 :- assigned(_,M).

% define before relation
before(J1,J2,M) | before(J2,J1,M) :- assigned(J1,M), assigned(J2,M), J1 < J2.
:- first(J1,M), before(J2,J1,M).
:- last(J1,M), before(J1,J2,M). 

% pick an immediate predecessor
1 { next(J1,J2,M) :  before(J1,J2,M)  } 1 :- assigned(J2,M), not first(J2,M).
1 { next(J2,J1,M) :  before(J2,J1,M)  } 1 :- assigned(J2,M), not last(J2,M).

% each jobs starts after its release
&diff{ 0 - compl(J1) } <= -(T+D+S) :- assigned(J1,M), next(J3,J1,M), setup(J3,J1,M,S), duration(J1,M,D), release(J1,M,T).  

% each jobs starts after all predecessors
&diff{ compl(J2) - compl(J1) } <= -(P+S) :- before(J2,J1,M), next(J3,J1,M), setup(J3,J1,M,S), duration(J1,M,P).

% redundant constraints
&diff{ compl(J2) - compl(J1) } <= -P :- before(J2,J1,M), duration(J1,M,P).
&diff{ 0 - compl(J1) } <= -(T+D) :- assigned(J1,M), duration(J1,M,D), release(J1,M,T). 


% machine spans are greater than completion times of jobs assigned to them
&diff { 0 - span(M) } <= 0 :- machine(M).
&diff { compl(J) - span(M) } <= 0 :- assigned(J,M).


#show first/2.
#show next/3.
#show assigned/2.


''',
    )



# Bind machine spans.
BOUND = (
        'bound',
        ['bound', 'machine', 'module_id'],
        '''
% For deactivation.
#external deactive_module(module_id).

&diff { span(machine) - 0 } <= bound :- not deactive_module(module_id).

''',
    )



# Fix jobs on a machine.
FIX_FIRST_JOB = (
        'fixFirstJob',
        ['job', 'machine'],
        '''
:- not first(job, machine).
''',
    )

FIX_NEXT_JOB = (
        'fixNextJob',
        ['previous_job', 'next_job', 'machine'],
        '''
:- not next(previous_job, next_job, machine).
''',
    )

FORBID_ASSIGNED = (
        'forbidAssigned',
        ['job', 'machine'],
        '''
:- assigned(job, machine).
''',
    )



def main(input_filename, timeout_spec, print_to, max_level=0):
    
    print('Approximation of Lexical Makespan by fixing machines with max span', file=print_to)
    print('version: {}'.format(__version__), file=print_to)
    print('Clingo version: {}'.format(clingo_version), file=print_to)
    print("Clingo-dl library: {} (I don't know how to get the version :-P)".format(ctypes.util.find_library('clingo-dl')), file=print_to, flush=True)
    
    
    timekeep = TimeKeep()
    
    model_count = 0
    module_count = 0
    interrupted_levels = []
    fixed_machines = set()
    
    
    ## Read machines and jobs from the input.
    
    machines = []
    jobs = []
    with open(input_filename) as fd:
        input_str = fd.read()
        for match in RE_MACHINE_OR_JOB.finditer(input_str):
            if match.group('predicate') == 'machine':
                machines.append(match.group('constant'))
            elif match.group('predicate') == 'job':
                jobs.append(match.group('constant'))
    machine_count = len(machines)
    if max_level <= 0 or max_level > machine_count:
        max_level = machine_count
    timeouts_seconds = timeout_spec.get_timeouts(machine_count)
    
    
    ## Prepare Clingo.
    
    ctrl = Control()
    
    dl = theory.Theory("clingodl", "clingo-dl")
    dl.configure("propagate", "full,1")
    dl.register(ctrl)
    
    
    ## Add programs and input and ground base.
    
    ctrl.add(*BASE_PROGRAM)
    ctrl.load(input_filename)
    ctrl.ground([('base', [])])
    
    # after grounding, before solving. As far as I know, this does nothing for DL.
    dl.prepare(ctrl)
    
    ctrl.add(*BOUND)
    ctrl.add(*FIX_FIRST_JOB)
    ctrl.add(*FIX_NEXT_JOB)
    ctrl.add(*FORBID_ASSIGNED)
    
    
    ## Solve.
    
    for level in range(max_level):
        print('\nLevel: {}'.format(level+1), file=print_to)
        
        last_bound_module_id = None
        
        # global bound# TODO: This is needed when bound is assigned in a different function!
        model = None
        bound = None
        max_machine = None
        
        cancel_me = None
        if level < len(timeouts_seconds):
            cancel_me = threading.Timer(timeouts_seconds[level], ctrl.interrupt)
            cancel_me.start()
        
        while True:
            
            with ctrl.solve(yield_=True, on_statistics=lambda step, accu: dl.on_statistics(step, accu)) as handle:
                for m in handle:
                    dl.on_model(m)
                    total_time = timekeep.time_total()
                    model = m.symbols(shown=True)
                    print('Time: {}s'.format(total_time), file=print_to)
                    model_count += 1
                    print('Answer: {}'.format(model_count), file=print_to)
                    for a in model:
                        print(a, file=print_to, end=' ')
                    spans = {}
                    for k, v in dl.assignment(m.thread_id):
                        print("dl({},{})".format(k,v), file=print_to, end=' ')
                        if k.match('span', 1):
                            spans[k.arguments[0].name] = v
                    ms = list(spans.keys())
                    ms.sort(key=lambda m: spans[m], reverse=True)
                    bound = spans[ms[level]]
                    max_machine = ms[level]
                    print('\nDL Optimization: {}'.format([spans[m] for m in ms]), file=print_to, flush=True)
                    # Get only the first model.
                    break
                else:
                    # There was no model,
                    # either the previous model (if not None) is the level optimum,
                    # or solver was interrupted.
                    # In both cases we exit the loop.
                    if cancel_me is not None:
                        cancel_me.cancel()
                        # TODO: It may have happened, that the timer fired between solve finished and here!
                        # In such case the next solve will be interrupted before it timeouts!
                        # Maybe implementation of Control.interrupt() is clever enough to account for this,
                        # because we still have the SolveHandle :-P
                    result = handle.get()
                    if result.interrupted:
                        interrupted_levels.append(level)
                        print('INTERRUPTED', file=print_to, flush=True)
                    break
            
            # bound, max_machine and model isn't be None, because if there is no model, we exit the optimisation loop
            
            # Bind machines that are not fixed.
            last_bound_module_id = module_count
            module_count += 1
            ctrl.ground([(BOUND[0], [bound-1, Function(machine), last_bound_module_id]) for machine in machines if machine not in fixed_machines])
            
            pass
        
        if level >= max_level - 1:
            # No need to prepare for the next iteration, because there will be none.
            break
        
        # Deactivate the last bound.
        # last_bound_module_id may be None if the first iteration didn't finish, i.e., there is no model
        if last_bound_module_id is not None:
            ctrl.assign_external(Function('deactive_module', [last_bound_module_id]), True)
        
        # Fix the maximal machine.
        first_job = None
        previous2next = {}
        jobs_on_max_machine = set()
        for atom in model:
            if atom.match('first', 2):
                job = atom.arguments[0].name
                machine = atom.arguments[1].name
                if machine == max_machine:
                    first_job = job
                    jobs_on_max_machine.add(job)
            if atom.match('next', 3):
                previous_job = atom.arguments[0].name
                next_job = atom.arguments[1].name
                machine = atom.arguments[2].name
                if machine == max_machine:
                    previous2next[previous_job] = next_job
                    jobs_on_max_machine.add(previous_job)
                    jobs_on_max_machine.add(next_job)
        
        ground_me = []
        
        # if first_job is None, nothing was scheduled on max_machine, which is possible :-P
        if first_job is not None:
            ground_me.append((FIX_FIRST_JOB[0], [Function(first_job), Function(max_machine)], ))
        
        for previous_job, next_job in previous2next.items():
            ground_me.append((FIX_NEXT_JOB[0], [Function(previous_job), Function(next_job), Function(max_machine)], ))
        
        for job in jobs:
            if job not in jobs_on_max_machine:
                ground_me.append((FORBID_ASSIGNED[0], [Function(job), Function(max_machine)], ))
        
        ctrl.ground(ground_me)
        fixed_machines.add(max_machine)
    
    
    ## Stats.
    
    print('\nTime: {}s'.format(timekeep.time_total()), file=print_to)
    print('Interrupted levels: {}'.format(list(map(lambda x: x+1, interrupted_levels))), file=print_to, flush=True)
    if not interrupted_levels:
        print('OPTIMUM FOUND', file=print_to, flush=True)



if __name__ == '__main__':
    
    def existing_file(argument):
        if argument == '-' or (os.path.exists(argument) and os.path.isfile(argument)):
            return argument
        else:
            raise argparse.ArgumentTypeError('Value must be an existing file!')
    
    def timeout_spec(argument):
        ts = eval(argument)
        if not isinstance(ts, (PerLevel, Geometric, )):
            raise argparse.ArgumentTypeError('Value must be an instance of PerLevel or Geometric! It has type {}'.format(type(ts)))
        return ts
    
    parser = argparse.ArgumentParser(
            description='Approximate of lex-makespan by fixing machines with max span.')
    parser.add_argument('-i', '--input', type=existing_file, metavar='FILE', default='-',
            help='the input file with ASP facts or "-" for stdin (default: %(default)s)')
    parser.add_argument('-t', '--timeout', type=timeout_spec, metavar='TIMEOUT', default=PerLevel(),
            help='either "PerLevel(t1,t2,t3,...)" where t1 is the timeout for the first level, t2 for second, etc... No timeout means no timeout. \
Or "Geometric(t,r)" where level i gets timeout t*(r**i). The timeouts t, t1, t2, ... are in seconds (default: %(default)s)')
    parser.add_argument('-l', '--max-level', type=int, metavar='N', default=0,
            help='maximal level of lexical makespan, 0 means all machines (default: %(default)s)')
    parser.add_argument('-o', '--output', type=argparse.FileType('w', encoding='UTF-8'), metavar='FILE', default='-',
            help='the output file or "-" for stdout (default: %(default)s)')
    
    args = parser.parse_args()
    try:
        main(
                input_filename = args.input,
                timeout_spec = args.timeout,
                print_to = args.output,
                max_level = args.max_level,
            )
    finally:
        args.output.close()


