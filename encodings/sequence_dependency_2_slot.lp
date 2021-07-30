% slots
% -------------------------------------------------------------

% we assign each job to one capable machine.
{ assign(J, M) : capable(M, J) } = 1 :- job(J).

% we calculate the number of jobs per machine.
number_of_jobs(M, N) :- machine(M), N = #count{J : assign(J, M)}.

% we assign each job to a slot of a machine dependent job list.
{ assign(J, M, 1..N) } = 1 :- assign(J, M), number_of_jobs(M, N).
:- assign(J1, M, I), assign(J2, M, I), J1!=J2.

% we define next, first and last.
next(J1, J2, M) :- assign(J1, M, I), assign(J2, M, I+1).
first(J, M) :- assign(J, M, 1).
last(J, M) :- assign(J, M, _), not next(J, _, M).

%{ before(J1, J2, M) : assign(J1, M, _) } = N :- assign(J2, M, N).

#show next/3.