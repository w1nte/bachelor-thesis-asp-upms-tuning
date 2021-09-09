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


minDuration(J, D) :- job(J), D = #min{ T : duration(J,_,T) }.
minDurationSum(S) :- S = #sum{ T,J : minDuration(J, T) }.

% set upper and lower bound for span domain.
lowerBound(LB) :- minDurationSum(LB).
upperBound(UB) :- horizon(UB).

int(LB..UB) :- lowerBound(LB), upperBound(UB).
{ span(M, T) : int(T) } = 1 :- machine(M).
&diff{ completion(J) - 0 } <= S :- assign(J, M), span(M, S).


% minimize the makespan
#minimize{ T : span(M,T) }.


#show lowerBound/1.
#show upperBound/1.
#show span/2.