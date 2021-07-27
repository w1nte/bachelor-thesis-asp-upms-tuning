% assignment of jobs to machines
1 { assigned(J,M) : capable(M,J) } 1 :- job(J).

% total order of jobs on machines
before(J1,J2,M) | before(J2,J1,M) :- assigned(J1,M), assigned(J2,M), J1 < J2.
before(J1,J3,M) :- before(J1,J2,M), before(J2,J3,M).
first(J1,M) :- assigned(J1,M), #count{ J2 : before(J2,J1,M) } = 0.
last(J2,M)  :- assigned(J2,M), #count{ J1 : before(J2,J1,M) } = 0.
1 {next(J1,J2,M) : before(J1,J2,M)} 1 :- assigned(J2,M), not first(J2,M).
1 { next(J2,J1,M) :  before(J2,J1,M)  } 1 :- assigned(J2,M), not last(J2,M).

% processing, start, and completion times for each job
%int(0..H) :- horizon(H).
granularity(1).
int(F*G) :- F = 0..(H/G)+1, horizon(H), granularity(G).
process(J,T) :- first(J,M), duration(J,M,T).
process(J2,D+S) :- next(J1,J2,M), duration(J2,M,D), setup(J1,J2,M,S).


% the first job completion time
&diff{ 0 - compl(J) } <= -P :- first(J,M), duration(J,M,P).

% each jobs starts after its release
&diff{ 0 - compl(J) } <= -(T+D) :- assigned(J,M), duration(J,M,D), release(J,M,T).  

% each jobs starts after all predecessors
&diff{ compl(J2) - compl(J1) } <= -P :- before(J2,J1,M), process(J1,P).

% redundant constraints
&diff{ compl(J2) - compl(J1) } <= -P :- before(J2,J1,M), duration(J1,M,P).

% machine span for each machine
1 { span(M,T) : int(T) } 1 :- machine(M).
&diff{ compl(J) - 0 } <= S :- assigned(J,M), span(M,S).

% minimise the lexical makespan
#minimize{ T@T,M : span(M,T) }.


#show assigned/2.
#show next/3.
#show span/2.
