
% assign jobs to capable machines
1 { assigned(J,M) : capable(M,J) } 1 :- job(J).

% pick first and last job for each 
1 { first(J,M) : assigned(J,M) } 1 :- assigned(_,M).
1 { last(J,M) : assigned(J,M) } 1 :- assigned(_,M).

% define before relation
before(J1,J2,M) | before(J2,J1,M) :- assigned(J1,M), assigned(J2,M), J1 < J2.
:- first(J1,M), before(J2,J1,M).
:- last(J1,M), before(J1,J2,M). 

% pick an immediate predecessor
1 { next(J1,J2,M) :  before(J1,J2,M)  } 1 :- assigned(J2,M), not first(J2,M).
1 { next(J2,J1,M) :  before(J2,J1,M)  } 1 :- assigned(J2,M), not last(J2,M).

% each jobs starts after its release
&diff{ 0 - compl(J1) } <= -(T+D+S) :- assigned(J1,M), next(J3,J1,M), setup(J3,J1,M,S), duration(J1,M,D), release(J1,M,T).  

% each jobs starts after all predecessors
&diff{ compl(J2) - compl(J1) } <= -(P+S) :- before(J2,J1,M), next(J3,J1,M), setup(J3,J1,M,S), duration(J1,M,P).

% makespan is max completion time
&diff{ compl(J) - makespan } <= 0 :- job(J).

% redundant constraints
&diff{ compl(J2) - compl(J1) } <= -P :- before(J2,J1,M), duration(J1,M,P).
&diff{ 0 - compl(J1) } <= -(T+D) :- assigned(J1,M), duration(J1,M,D), release(J1,M,T). 


int(0..H) :- horizon(H).
1 { makespan(T) : int(T) } 1.
&diff{ makespan - 0 } <= T :- makespan(T).

% minimise the makespan
#minimize{ T : makespan(T) }.


#show next/3.
#show assigned/2.
#show job/1.
#show machine/1.
#show setup/4.
#show duration/3.
#show release/3.
#show first/2.
#show span/2.