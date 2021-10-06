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