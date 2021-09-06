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

% completion time must be between zero and horizon.
&diff{ 0 - completion(J) } < 0 :- job(J).
&diff{ completion(J) - 0 } <= H :- job(J), horizon(H).

% previous completion times are always smaller.
&diff{ completion(JB) - completion(J) } < -D :- before(JB, J, M), duration(J, M, D).

% completion time must be greater than previous completion times.
&diff{ completion(JAB) - completion(J) } <= -(S+D) :- before(JAB, J, M), next(JB, J, M), setup(JB, J, M, S), duration(J, M, D).

int(I) :- I=c..H, 0=I\f, horizon(H).
{ bound(I) : int(I) } = 1.
maxDuration(J, D) :- job(J), D = #max{ T : duration(J,_,T) }.
durationSum(S) :- S = #sum{ T,J : maxDuration(J, T) }.
numberOfMachines(N) :- N = #count{ M : machine(M) }.

&diff{ makespan - 0 } <= U :- assign(J, M), bound(U).

% expand the lower boundary upwards
#heuristic bound(I) : maxInt(M), int(I), L=M-I. [L@1,true]
maxInt(I) :- I = #max{ J : int(J) }.


#include "../heuristics/prefer_short_durations.lp".
#include "../heuristics/prefer_short_setuptimes.lp".
#include "../heuristics/prefer_early_release.lp".


#show bound/1.
#show int/1.