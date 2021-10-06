% assign jobs to capable machines.
{ assign(J, M) : capable(M, J) } = 1 :- job(J).

% pick first and last job for each machine.
{ first(J, M) : capable(M, J) } = 1 :- assign(_, M).
{ last(J, M) : capable(M, J) } = 1 :- assign(_, M).
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