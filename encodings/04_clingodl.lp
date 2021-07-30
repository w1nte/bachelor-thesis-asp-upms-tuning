% imports the solutions generator. This encoding only needs assign/2 and next/3.
#include "sequence_dependency_1_before.lp".

% start time must be after release time.
&diff{ R - start(J) } <= 0 :- assign(J, M), release(J, M, R).

% start time must be after setup time of prev job.
&diff{ start(JB) - start(J) } <= -(D+S) :- assign(J, M), next(JB, J, M), setup(JB, J, M, S), duration(JB, M, D).

% makespan is max completion time.
&diff{ start(J) - makespan } <= -D :- assign(J, M), duration(J, M, D).


% TODO: is probably not correct (see processing time)