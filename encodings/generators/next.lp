% assign jobs to capable machines
{ assign(J, M) : capable(M, J) } = 1 :- job(J).

% pick first and last job for each 
{ first(J, M) : capable(M, J) } = 1 :- assign(_, M).
{ last(J, M) : capable(M, J) } = 1 :- assign(_, M).
:- first(J, M), not assign(J, M).
:- last(J, M), not assign(J, M).

% define next relation
{ next(J1, J2, M) : capable(M, J2), J1 != J2  } = 1 :- assign(J1, M), not last(J1, M).
:- next(J1, J2, M), not assign(J1, M).
reach(J1, M) :- first(J1, M).
reach(J2, M) :- reach(J1, M), next(J1, J2, M).
:- assign(J, M), not reach(J, M).

#show next/3. 