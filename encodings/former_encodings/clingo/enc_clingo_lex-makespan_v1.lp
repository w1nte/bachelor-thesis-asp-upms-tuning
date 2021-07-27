% assignment of jobs to machines
1 { assigned(J,M) : capable(M,J) } 1 :- job(J).

% total order of jobs on machines
before(J1,J2,M) | before(J2,J1,M) :- assigned(J1,M), assigned(J2,M), J1 < J2.
before(J1,J3,M) :- before(J1,J2,M), before(J2,J3,M).
first(J1,M) :- assigned(J1,M), #count{ J2 : before(J2,J1,M) } = 0.
last(J2,M)  :- assigned(J2,M), #count{ J1 : before(J2,J1,M) } = 0.
1 {next(J1,J2,M) : before(J1,J2,M)} 1 :- assigned(J2,M), not first(J2,M).
:- next(J1,J2,M), before(J1,J3,M), before(J3,J2,M).

% processing, start, and completion times for each job
int(0..H) :- horizon(H).
process(J,T) :- first(J,M), duration(J,M,T).
process(J2,D+S) :- next(J1,J2,M), duration(J2,M,D), setup(J1,J2,M,S).
start(J,T) :- int(T), first(J,M), release(J,M,T).
start(J2,T) :- int(T), next(J1,J2,M), T = #max{R: release(J2,M,R) ; C: compl(J1,C)}.
compl(J,S+P) :- int(T), start(J,S), process(J,P).

% machine span for each machine
span(M,T) :- int(T), last(J,M), compl(J,T).

% minimise the lexical makespan
#minimize{ T@T,M : span(M,T) }.


#show assigned/2.
#show next/3.
#show compl/2.
#show span/2.
