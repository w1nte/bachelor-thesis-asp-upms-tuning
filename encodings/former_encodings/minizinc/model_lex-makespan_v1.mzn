include "alldifferent.mzn";
include "alldifferent_except_0.mzn";
include "nvalue_fn.mzn";

int: nJobs;
int: nMachines;

set of int: Jobs = 1..nJobs;
set of int: Machines = 1..nMachines;

array[Jobs] of set of Machines: capableMachines;
array[Jobs,Machines] of int: durations;
array[Jobs,Machines] of int: releaseDates;
array[Jobs,Jobs,Machines] of int: setupTimes;

array[Jobs] of var Machines: machineAssignment;
array[Jobs] of var Jobs union { 0 }: predecessors;
array[Jobs] of var 0..horizon: completionTime;

array[Machines] of var 0..horizon: machineSpans;

array[Machines] of var Machines: machineLevels;

int: horizon;


% predecessors are different except for zero (first job)
constraint alldifferent_except_0([ p | p in predecessors ]);

% there can only be nMachines first jobs
constraint count(p in predecessors)(p == 0) == nvalue(machineAssignment);

% assigned machine has to be capable
constraint forall(j in Jobs)(
  machineAssignment[j] in capableMachines[j]
);

% predecessor needs to be zero or on the same machine
constraint forall(j in Jobs)(
  predecessors[j] != 0 -> machineAssignment[j] == machineAssignment[predecessors[j]]
);

% no job is its own predecessor
constraint forall(j in Jobs)(
  predecessors[j] != j
);

% each job starts after its predecessor
constraint forall(j,k in Jobs where j != k)(
  completionTime[j] >= (max(completionTime[k], releaseDates[j,machineAssignment[j]]) 
                       + setupTimes[k,j,machineAssignment[j]]
                       + durations[j,machineAssignment[j]]) * bool2int(predecessors[j] == k)
);

% each job starts after its release date
constraint forall(j in Jobs)(
  completionTime[j] >= releaseDates[j,machineAssignment[j]] 
                       + durations[j,machineAssignment[j]]
);

% machine spans 
constraint forall(m in Machines)(
  machineSpans[m] = max(j in Jobs)(completionTime[j] * bool2int(machineAssignment[j] == m))
);

% determine levels wrt to machine spans
constraint alldifferent(machineLevels);

constraint forall(m,n in Machines where m != n)(
  machineLevels[m] > machineLevels[n] -> machineSpans[m] >= machineSpans[n]
);

% objective function
function var int: makespan_objective() = max(j in Jobs)(completionTime[j]);
function var int: lex_makespan_objective() = sum(m in Machines)(((horizon + 1) ^ (machineLevels[m] - 1)) * machineSpans[m]);


solve minimize lex_makespan_objective();

