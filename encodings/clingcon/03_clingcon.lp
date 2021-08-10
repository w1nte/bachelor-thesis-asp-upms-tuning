% we assign each job to one capable machine.
{ assign(J, M) : capable(M, J) } = 1 :- job(J).

before(J1, J2, M) :- &sum{ start(J1); -start(J2) } < 0, assign(J1, M), assign(J2, M).
{ next(J1, J2, M) : before(J1,J2,M) } = 1 :- assign(J2, M).

&dom{ R..N } = start(J) :- assign(J, M), release(J, M, R), horizon(N).

% calculate completion time.
&sum{ start(J); D; S } = complete(J) :- assign(J, M), next(JB, J, M), duration(J, M, D), setup(JB, J, M, S).

&sum{ complete(J) } >= (R+D) :- assign(J, M), release(J, M, R), duration(J, M, D).

% start time must be after release time.
%&sum{ start(J); -R } >= 0 :- assign(J, M), release(J, M, R).

% start time must be after prev job.
&sum{ start(J); -complete(JB) } >= 0 :- assign(J, M), next(JB, J, M).

% makespan is max completion time.
&sum{ complete(J); -makespan } <= 0 :- job(J).


&minimize{ makespan }.

#show assign/2.