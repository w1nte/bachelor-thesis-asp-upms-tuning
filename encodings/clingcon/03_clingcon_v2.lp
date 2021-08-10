#include "../generators/clingcon.lp".

% calculate completion time.
&sum{ start(J); D; S } = complete(J) :- assign(J, M), next(JB, J, M), duration(J, M, D), setup(JB, J, M, S).

% completion time must be after release + duration time.
&sum{ complete(J) } >= (R+D) :- assign(J, M), release(J, M, R), duration(J, M, D).

% start time must be after release time.
&sum{ start(J); -R } >= 0 :- assign(J, M), release(J, M, R).

% start time must be after prev job.
&sum{ start(J); -complete(JB) } >= 0 :- assign(J, M), next(JB, J, M).

% makespan is max completion time.
&sum{ complete(J); -makespan } <= 0 :- job(J).


&minimize{ makespan }.

#show assign/2.