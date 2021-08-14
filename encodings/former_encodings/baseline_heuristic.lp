
% assign jobs to capable machines
1 { assign(J,M) : capable(M,J) } 1 :- job(J).

% pick first and last job for each 
1 { first(J,M) : assign(J,M) } 1 :- assign(_,M).
1 { last(J,M) : assign(J,M) } 1 :- assign(_,M).

% define before relation
before(J1,J2,M) | before(J2,J1,M) :- assign(J1,M), assign(J2,M), J1 < J2.
:- first(J1,M), before(J2,J1,M).
:- last(J1,M), before(J1,J2,M). 

% pick an immediate predecessor
1 { next(J1,J2,M) :  before(J1,J2,M)  } 1 :- assign(J2,M), not first(J2,M).
1 { next(J2,J1,M) :  before(J2,J1,M)  } 1 :- assign(J2,M), not last(J2,M).

% each jobs starts after its release
&diff{ 0 - completion(J1) } <= -(T+D+S) :- assign(J1,M), next(J3,J1,M), setup(J3,J1,M,S), duration(J1,M,D), release(J1,M,T).  

% each jobs starts after all predecessors
&diff{ completion(J2) - completion(J1) } <= -(P+S) :- before(J2,J1,M), next(J3,J1,M), setup(J3,J1,M,S), duration(J1,M,P).

% makespan is max completion time
&diff{ completion(J) - makespan } <= 0 :- job(J).

% redundant constraints
&diff{ completion(J2) - completion(J1) } <= -P :- before(J2,J1,M), duration(J1,M,P).
&diff{ 0 - completion(J1) } <= -(T+D) :- assign(J1,M), duration(J1,M,D), release(J1,M,T). 

#heuristic assign(J,M) : duration(J,M,D), maxDuration(J,F), W=F-D. [W@2,true]
maxDuration(J,M) :- job(J), M = #max{ D : duration(J,_,D) }.

#heuristic next(J,K,M) : setup(J,K,M,S), maxSetup(K,M,T), capable(J,M), capable(K,M), W=T-S. [W@1,true]
maxSetup(J,M,S) :- job(J), machine(M), S = #max{ T : setup(_,J,M,T) }.


#show next/3.
#show assign/2.


