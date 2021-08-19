% include solution generator.
#include "../generators/before_relation.lp".

% set start domain from release to horizon.
&dom{ R..N } = start(J) :- assign(J, M), release(J, M, R), horizon(N).

% calculate completion time.
&sum{ start(J); D; S } = completion(J) :- assign(J, M), next(JB, J, M), duration(J, M, D), setup(JB, J, M, S).

% completion time starts after release + duration time.
&sum{ completion(J) } >= (R+D) :- assign(J, M), release(J, M, R), duration(J, M, D).

% start time starts after release time.
&sum{ start(J); -R } >= 0 :- assign(J, M), release(J, M, R).

% start time starts after previous job.
&sum{ start(J); -completion(JB) } >= 0 :- assign(J, M), next(JB, J, M).

% makespan is max completion time.
&sum{ completion(J); -makespan } <= 0 :- job(J).


&minimize{ makespan }.

#show assign/2.
#show first/2.
#show next/3.
