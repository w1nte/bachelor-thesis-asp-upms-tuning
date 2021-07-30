% imports the solutions generator. This encoding only needs assign/2 and next/3.
#include "sequence_dependency_1_before.lp".

&dom{ 0..N } = start(J) :- job(J), horizon(N).

% calculate completion time.
&sum{ start(J); D; S } = complete(J) :- assign(J, M), next(JB, J, M), duration(J, M, D), setup(JB, J, M, S).

&sum{ complete(J) } >= (R+D) :- assign(J, M), release(J, M, R), duration(J, M, D).

% start time must be after release time.
&sum{ start(J); -R } >= 0 :- assign(J, M), release(J, M, R).

% start time must be after prev job.
&sum{ start(J); -complete(JB) } >= 0 :- assign(J, M), next(JB, J, M).

% makespan is max completion time.
&sum{ complete(J); -makespan } <= 0 :- job(J).


&minimize{ makespan }.

#show assign/2.