#!/usr/bin/env python3

# 
# Requirements:
# - PYTHONPATH must contain module clingo
# - Dynamically linked library of clingo-dl must be found by ctypes.util.find_library
# - PYTHONPATH must contain module theory from https://github.com/potassco/tefoli
# 



__version__ = '0.0.3'



import argparse

from clingo import Control
from clingo import Function
from clingo import __version__ as clingo_version

from collections import defaultdict

import ctypes

import os

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



# Only to get the number of machines.
BASE_PROGRAM = (
        'base',
        [],
        '''
machine_count(C) :- C = #count{ M : machine(M) }.

#show machine_count/1.
''',
    )

# From https://github.com/joetsch/Scheduling/blob/master/encodings/pmsp/clingo-dl/enc_clingo-dl_makespan_v2.lp
MAIN_PROGRAM = (
        'main',
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


#show next/3.
#show assigned/2.


''',
    )



# Guess a subset of machines.
# The first level is 0 and the last one is (machine_count - 1) !!!
MACHINE_SUBSET = (
        'machine_subset',
        ['level', 'module_id'],
        '''
% For deactivation.
#external deactive_module(module_id).

(C-level) { selected_machine(module_id, M) : machine(M) } :- machine_count(C), not deactive_module(module_id).

''',
    )



# Bind machine spans.
BOUND = (
        'bound',
        ['bound', 'machine_subset_module_id', 'module_id'],
        '''
% For deactivation.
#external deactive_module(module_id).

&diff { span(M) - 0 } <= bound :- selected_machine(machine_subset_module_id, M), not deactive_module(module_id).

''',
    )



def main(input_filename, timeout_spec, print_to, max_level=0):
    
    print('Hierarchical optimisation of Lexical Makespan', file=print_to)
    print('version: {}'.format(__version__), file=print_to)
    print('Clingo version: {}'.format(clingo_version), file=print_to)
    print("Clingo-dl library: {} (I don't know how to get the version :-P)".format(ctypes.util.find_library('clingo-dl')), file=print_to, flush=True)
    
    
    timekeep = TimeKeep()
    
    model_count = 0
    module_count = 0
    interrupted_levels = []
    
    
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
    
    machine_count = None
    with ctrl.solve(yield_=True, on_statistics=lambda step, accu: dl.on_statistics(step, accu)) as handle:
        for m in handle:
            dl.on_model(m)
            for atom in m.symbols(shown=True):
                if atom.match('machine_count', 1):
                    machine_count = atom.arguments[0].number
                    break
            break
    if machine_count is None:
        raise Exception('Failed to retrieve the number of machines!')
    if max_level <= 0 or max_level > machine_count:
        max_level = machine_count
    timeouts_seconds = timeout_spec.get_timeouts(machine_count)
    
    ctrl.add(*MAIN_PROGRAM)
    ctrl.ground([('main', [])])
    
    ctrl.add(*MACHINE_SUBSET)
    ctrl.add(*BOUND)
    
    
    ## Solve.
    
    for level in range(max_level):
        print('\nLevel: {}'.format(level+1), file=print_to)
        
        machine_subset_module_id = module_count
        module_count += 1
        ctrl.ground([('machine_subset', [level, machine_subset_module_id])])
        
        bound_module_ids = []
        
        # global bound# TODO: This is needed when bound is assigned in a different function!
        bound = None
        
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
                    assignment = []
                    spans = []
                    for k, v in dl.assignment(m.thread_id):
                        assignment.append((k,v))
                        if k.match('span', 1):
                            spans.append(v)
                    spans.sort(reverse=True)
                    bound = spans[level]
                    print('Time: {}s'.format(total_time), file=print_to)
                    model_count += 1
                    print('Answer: {}'.format(model_count), file=print_to)
                    for a in model:
                        print(a, file=print_to, end=' ')
                    for k,v in assignment:
                        print("dl({},{})".format(k,v), file=print_to, end=' ')
                    print('\nDL Optimization: {}'.format(spans), file=print_to, flush=True)
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
            
            # bound shouldn't be None, because if there is no model, we exit the optimisation loop
            
            bound_module_id = module_count
            module_count += 1
            bound_module_ids.append(bound_module_id)
            ctrl.ground([('bound', [bound-1, machine_subset_module_id, bound_module_id])])
            
            pass
        
        # Deactivate the modules for level optimisation.
        for bound_module_id in bound_module_ids:
            ctrl.assign_external(Function('deactive_module', [bound_module_id]), True)
        
        # Constraint bound for the finished level.
        ctrl.ground([('bound', [bound, machine_subset_module_id, module_count])])
        module_count += 1
    
    
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
            description='Optimise lex-makespan hierarchically.')
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


