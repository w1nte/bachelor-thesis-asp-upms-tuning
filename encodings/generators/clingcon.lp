% assign each job to one machine.
{ assign(J, M) : capable(M, J) } = 1 :- job(J).

% set start domain from release to horizon.
&dom{ R..N } = start(J, M) :- assign(J, M), release(J, M, R), horizon(N).

% define before relation.
before(J1, J2, M) :- &sum{ start(J1, M); -start(J2, M) } < 0, assign(J1, M), assign(J2, M).

% pick first job for each machine.
{ first(J, M) : assign(J, M) } = 1 :- machine(M).
:- first(J, M), before(JB, J, M).

% pick last job for each machine.
{ last(J, M) : assign(J, M) } = 1 :- machine(M).
:- last(J, M), before(J, JB, M).

% pick an immediate predecessor.
1 { next(J1, J2, M) : before(J1, J2, M) } 1 :- assign(J2, M), not first(J2, M).
1 { next(J2, J1, M) : before(J2, J1, M) } 1 :- assign(J2, M), not last(J2, M).
