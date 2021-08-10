{ assign(J, M) : capable(M, J) } = 1 :- job(J).

&dom{ R..N } = start(J) :- assign(J, M), release(J, M, R), horizon(N).

before(J1, J2, M) :- &sum{ start(J1); -start(J2) } < 0, assign(J1, M), assign(J2, M).
{ first(J, M) : assign(J, M) } = 1.
:- first(J, M), before(JB, J, M).
{ last(J, M) : assign(J, M) } = 1.
:- last(J, M), before(J, JB, M).
{ next(J1,J2,M) : before(J1,J2,M) } = 1 :- assign(J2,M), not first(J2,M).
{ next(J2,J1,M) : before(J2,J1,M) } = 1 :- assign(J2,M), not last(J2,M).

&distinct{ start(J) : job(J) }.

#show first/2.
#show before/3.
#show next/3.