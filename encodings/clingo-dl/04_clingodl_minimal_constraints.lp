% imports the solutions generator. This encoding only needs assign/2 and next/3.
#include "../generators/before_relation.lp".

% calculate completion time
&diff{ completion(JB) - completion(J) } <= -(S+D) :- assign(J, M), next(JB, J, M), setup(JB, J, M, S), duration(J, M, D).

% job completes after setup + duration + release time.
&diff{ 0 - completion(J) } <= -(R+D+S) :- assign(J, M), release(J, M, R), duration(J, M, D), next(JB, J, M), setup(JB, J, M, S).

% first job completes after duration + release time.
&diff{ 0 - completion(J) } = -(R+D) :- first(J, M), release(J, M, R), duration(J, M, D).

% makespan is max completion time.
&diff{ completion(J) - makespan } <= 0 :- job(J).

#show assign/2.
