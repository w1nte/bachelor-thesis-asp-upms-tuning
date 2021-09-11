% include solution generator.
#include "../generators/before_relation.lp".

% completion time starts after the jobs processing time and immediate predecessors completion time.
&diff{ completion(JB) - completion(J) } <= -(S+D) :- next(JB, J, M), setup(JB, J, M, S), duration(J, M, D).

% completion time starts after setup + duration + release time.
&diff{ 0 - completion(J) } <= -(R+D+S) :- assign(J, M), release(J, M, R), duration(J, M, D), next(JB, J, M), setup(JB, J, M, S).

% completion time starts after duration + release time.
&diff{ 0 - completion(J) } <= -(R+D) :- assign(J, M), release(J, M, R), duration(J, M, D).

% makespan is max completion time.
&diff{ completion(J) - makespan } <= 0 :- job(J).


numberOfMachines(N) :- N = #count{ M : machine(M) }.
minDuration(J, D) :- job(J), D = #min{ T : duration(J,_,T) }.
minDurationSum(S) :- S = #sum{ T,J : minDuration(J, T) }.

% set upper and lower bound for span domain.
lowerBound(LB) :- LB = S/N, minDurationSum(S), numberOfMachines(N).
upperBound(UB) :- horizon(UB).

int(LB..UB) :- lowerBound(LB), upperBound(UB).
{ makespan(T) : int(T) } = 1.
&diff{ makespan - 0 } <= T :- makespan(T).


% minimize the makespan
#minimize{ T : makespan(T) }.


#show lowerBound/1.
#show upperBound/1.