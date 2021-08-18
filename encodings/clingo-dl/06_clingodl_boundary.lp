% imports the solutions generator. This encoding only needs assign/2 and next/3.
#include "../generators/before_relation.lp".

% calculate completion time
&diff{ completion(JB) - completion(J) } <= -(S+D) :- next(JB, J, M), setup(JB, J, M, S), duration(J, M, D).

% job completes after setup + duration + release time.
&diff{ 0 - completion(J) } <= -(R+D+S) :- assign(J, M), release(J, M, R), duration(J, M, D), next(JB, J, M), setup(JB, J, M, S).

% job completes after duration + release time.
&diff{ 0 - completion(J) } <= -(R+D) :- assign(J, M), release(J, M, R), duration(J, M, D).

% makespan is max completion time.
&diff{ completion(J) - makespan } <= 0 :- job(J).

% completion time must be between zero and horizon.
&diff{ 0 - completion(J) } < 0 :- job(J).
&diff{ completion(J) - 0 } <= H :- job(J), horizon(H).

% previous completion times are always smaller.
&diff{ completion(JB) - completion(J) } < -D :- before(JB, J, M), duration(J, M, D).

% completion time must be greater than prev completion times.
&diff{ completion(JAB) - completion(J) } <= -(S+D) :- before(JAB, J, M), next(JB, J, M), setup(JB, J, M, S), duration(J, M, D).


lowerBound(LB) :- LB = l.
upperBound(UB) :- UB = u.

int(LB..UB) :- lowerBound(LB), upperBound(UB).
{ span(M, T) : int(T) } = 1 :- machine(M).
&diff{ completion(J) - 0 } <= S :- assign(J, M), span(M, S).

% expand the lower boundary upwards
#heuristic span(M, T) : machine(M), maxInt(I), int(T), L=I-T. [L@1,true]
maxInt(I) :- I = #max{ J : int(J) }.

% minimize the makespan
#minimize{ T : span(M,T) }.


#show lowerBound/1.
#show upperBound/1.
#show span/2.