% assign jobs to capable machines.
{ assign(J, M) : capable(M, J) } = 1 :- job(J).

% pick first and last job for each machine.
{ first(J, M) : assign(J, M) } = 1 :- assign(_, M).
{ last(J, M) : assign(J, M) } = 1 :- assign(_, M).
:- first(J, M), not assign(J, M).
:- last(J, M), not assign(J, M).

% define the immediate predecessor for each job.
{ next(J1, J2, M) : capable(M, J1), J1 != J2 } = 1 :- assign(J2, M), not first(J2, M).
{ next(J1, J2, M) : capable(M, J2), J1 != J2 } = 1 :- assign(J1, M), not last(J1, M).
:- next(J1, J2, M), not assign(J1, M).
:- next(J1, J2, M), not assign(J2, M).
reach(J1, M) :- first(J1, M).
reach(J2, M) :- reach(J1, M), next(J1, J2, M).
:- assign(J, M), not reach(J, M).

% completion time starts after the jobs processing time and immediate predecessors completion time.
&diff{ completion(JB) - completion(J) } <= -(S+D) :- assign(J, M), next(JB, J, M), setup(JB, J, M, S), duration(J, M, D).

% completion time starts after setup + duration + release time.
&diff{ 0 - completion(J) } <= -(R+D+S) :- assign(J, M), release(J, M, R), duration(J, M, D), next(JB, J, M), setup(JB, J, M, S).

% completion time starts after duration + release time.
&diff{ 0 - completion(J) } <= -(R+D) :- assign(J, M), release(J, M, R), duration(J, M, D).

% makespan is max completion time.
&diff{ completion(J) - makespan } <= 0 :- job(J).

#show first/2.
#show next/3.
