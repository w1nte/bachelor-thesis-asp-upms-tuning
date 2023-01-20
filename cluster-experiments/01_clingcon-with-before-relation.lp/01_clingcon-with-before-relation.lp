% assign jobs to capable machines
{ assign(J, M) : capable(M, J) } = 1 :- job(J).

% pick first and last job for each 
{ first(J, M) : assign(J, M) } = 1 :- assign(_, M).
{ last(J, M) : assign(J, M) } = 1 :- assign(_, M).

% define before relation
before(J1, J2, M) | before(J2, J1, M) :- assign(J1, M), assign(J2, M), J1 < J2.
:- first(J1, M), before(J2, J1, M).
:- last(J1, M), before(J1, J2, M). 

% pick an immediate predecessor
{ next(J1, J2, M) : before(J1,J2,M) } = 1 :- assign(J2, M), not first(J2, M).
{ next(J2, J1, M) : before(J2,J1,M) } = 1 :- assign(J2, M), not last(J2, M).

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

#show first/2.
#show next/3.
