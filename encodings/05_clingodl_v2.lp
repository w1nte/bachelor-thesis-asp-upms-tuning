% imports the solutions generator. This encoding only needs assign/2 and next/3.
#include "sequence_dependency_1_before.lp".

% start time must be after release time.
&diff{ R - start(J) } <= 0 :- assign(J, M), release(J, M, R).

% completion time after Start + Duration + Setup Time.
&diff{ start(J) - completion(J) } <= S-D :- assign(J, M), next(JB, J, M), duration(J, M, D), setup(JB, J, M, S).

% completion time after Release + Duration.
&diff{ 0 - completion(J) } <= -(R+D) :- assign(J, M), duration(J, M, D), release(J, M, R).

% start time must be after prev job.
&diff{ completion(JB) - start(J) } <= 0 :- assign(J, M), next(JB, J, M).

% makespan is max completion time.
&diff{ completion(J) - makespan } <= 0 :- job(J).

#show assign/2.