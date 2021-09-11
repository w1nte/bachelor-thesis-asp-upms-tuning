% assign jobs to capable machines.
{ assign(J, M) : capable(M, J) } = 1 :- job(J).

% calculate the number of jobs for each machine.
number_of_jobs(M, N) :- machine(M), N = #count{J : assign(J, M)}.

% define machine slots
slot(M, S) :- number_of_jobs(M, N), S=1..N.

% assign each job to a slot of a machine dependent job list.
{ assign(J, M, S) : slot(M, S) } = 1 :- assign(J, M), number_of_jobs(M, N).
:- assign(J1, M, I), assign(J2, M, I), J1 != J2.

% pick first and last job for each machine.
first(J, M) :- assign(J, M, 1).
last(J, M) :- assign(J, M, _), not next(J, _, M).

% define the immediate predecessor for each job.
next(J1, J2, M) :- assign(J1, M, I), assign(J2, M, I+1).

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
