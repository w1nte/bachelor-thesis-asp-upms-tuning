#!/usr/bin/env python3

# 
# Requirements:
# - PYTHONPATH must contain module clingo
# - Dynamically linked library of clingo-dl must be found by ctypes.util.find_library
# - PYTHONPATH must contain module theory from https://github.com/potassco/tefoli
# 



__version__ = '0.0.1'



import argparse

from clingo import Control
from clingo import Function
from clingo import __version__ as clingo_version

from collections import defaultdict

import ctypes

import os

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


% guess the order of the machines
beforeM(M1,M2) | beforeM(M2,M1) :- machine(M1), machine(M2), M1 < M2.
beforeM(M1,M3) :- beforeM(M1,M2), beforeM(M2,M3).

indexM(M,I) :- machine(M), I = #count{ M1 : beforeM(M1,M) }.

% the order must be non-increasing
&diff { span(M2) - span(M1) } <= 0 :- beforeM(M1,M2).

% guess the difference point
1 { differenceIndex(I) : indexM(_,I) } 1.


#show next/3.
#show assigned/2.


''',
    )



# Bound on a component of lex-makespan.
# The index of the first component is 0 and the last one is (machine_count - 1) !!!
COMPONENT_BOUND = (
        'component_bound',
        ['index', 'bound', 'module_id'],
        '''
% For activation.
#external active_module(module_id).

c(index,bound,module_id) :- active_module(module_id).

''',
    )

# Bind machine spans.
BOUND_CONSTRAINTS = (
        'bound_constraints',
        ['module_id'],
        '''
% For activation.
#external active_module(module_id).

% machines before the difference point must have spans up to the bounds
&diff { span(M) - 0 } <= C :- indexM(M,I), c(I,C,module_id), differenceIndex(DI), I < DI, active_module(module_id).

% the machine at the difference point must have strictly smaller span than the bound
&diff { span(M) - 0 } <= (C-1) :- indexM(M,I), c(I,C,module_id), differenceIndex(I), active_module(module_id).

''',
    )



def main(input_filename, timeout_seconds, print_to, max_level=0):
    
    print('Linear Descent optimisation of Lexical Makespan', file=print_to)
    print('version: {}'.format(__version__), file=print_to)
    print('Clingo version: {}'.format(clingo_version), file=print_to)
    print("Clingo-dl library: {} (I don't know how to get the version :-P)".format(ctypes.util.find_library('clingo-dl')), file=print_to, flush=True)
    
    
    timekeep = TimeKeep()
    
    model_count = 0
    module_count = 0
    was_interrupted = False
    
    
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
    
    ctrl.add(*MAIN_PROGRAM)
    ctrl.ground([('main', [])])
    
    ctrl.add(*COMPONENT_BOUND)
    ctrl.add(*BOUND_CONSTRAINTS)
    
    
    ## Solve.
    
    bound_module_id = None
    
    # global spans# TODO: This is needed when spans is assigned in a different function!
    spans = None
    
    cancel_me = None
    if timeout_seconds > 0:
        cancel_me = threading.Timer(timeout_seconds, ctrl.interrupt)
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
                spans = spans[:max_level]
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
                # either the previous model (if not None) is the global optimum,
                # or solver was interrupted.
                # In both cases we exit the loop.
                if cancel_me is not None:
                    cancel_me.cancel()
                    # There is no threading issue here, because we don't call solve again.
                result = handle.get()
                if result.interrupted:
                    was_interrupted = True
                    print('INTERRUPTED', file=print_to, flush=True)
                break
        
        # spans shouldn't be None, because if there is no model, we exit the optimisation loop
        
        # If there was a bound grounded before the solve call, deactivate it.
        if bound_module_id is not None:
            ctrl.release_external(Function('active_module', [bound_module_id]))
        
        # Ground a bound according to spans.
        bound_module_id = module_count
        module_count += 1
        for i in range(len(spans)):
            ctrl.ground([(COMPONENT_BOUND[0], [i, spans[i], bound_module_id])])
            ctrl.assign_external(Function('active_module', [bound_module_id]), True)
        ctrl.ground([(BOUND_CONSTRAINTS[0], [bound_module_id])])
        ctrl.assign_external(Function('active_module', [bound_module_id]), True)
    
    
    ## Stats.
    
    print('\nTime: {}s'.format(timekeep.time_total()), file=print_to)
    if not was_interrupted:
        print('OPTIMUM FOUND', file=print_to, flush=True)



if __name__ == '__main__':
    
    def existing_file(argument):
        if argument == '-' or (os.path.exists(argument) and os.path.isfile(argument)):
            return argument
        else:
            raise argparse.ArgumentTypeError('Value must be an existing file!')
    
    parser = argparse.ArgumentParser(
            description='Optimise lex-makespan with linear descent.')
    parser.add_argument('-i', '--input', type=existing_file, metavar='FILE', default='-',
            help='the input file with ASP facts or "-" for stdin (default: %(default)s)')
    parser.add_argument('-t', '--timeout', type=int, metavar='N', default=0,
            help='timeout in seconds, 0 means no timeout (default: %(default)s)')
    parser.add_argument('-l', '--max-level', type=int, metavar='N', default=0,
            help='maximal level of lexical makespan, 0 means all machines (default: %(default)s)')
    parser.add_argument('-o', '--output', type=argparse.FileType('w', encoding='UTF-8'), metavar='FILE', default='-',
            help='the output file or "-" for stdout (default: %(default)s)')
    
    args = parser.parse_args()
    try:
        main(
                input_filename = args.input,
                timeout_seconds = args.timeout,
                print_to = args.output,
                max_level = args.max_level,
            )
    finally:
        args.output.close()


