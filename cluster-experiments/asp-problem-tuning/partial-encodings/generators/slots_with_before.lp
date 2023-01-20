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

{ before(J1, J2, M) : assign(J1, M, _) } = N :- assign(J2, M, N).
