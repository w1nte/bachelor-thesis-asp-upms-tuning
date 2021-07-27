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
before(J1,J2,M) | before(J2,J1,M) :- assign(J1,M), assign(J2,M), J1 < J2.


% each jobs starts after its release
&diff{ 0 - compl(J1) } <= -(T+D+S) :- assign(J1,M), next(J3,J1,M), setup(J3,J1,M,S), duration(J1,M,D), release(J1,M,T).  

% each jobs starts after all predecessors
&diff{ compl(J2) - compl(J1) } <= -(P+S) :- before(J2,J1,M), next(J3,J1,M), setup(J3,J1,M,S), duration(J1,M,P).

% makespan is max completion time
&diff{ compl(J) - makespan } <= 0 :- job(J).

% redundant constraints
&diff{ compl(J2) - compl(J1) } <= -P :- before(J2,J1,M), duration(J1,M,P).
&diff{ 0 - compl(J1) } <= -(T+D) :- assign(J1,M), duration(J1,M,D), release(J1,M,T). 



% machine span for each machine
int(0..H) :- horizon(H).
1 { span(M,T) : int(T) } 1 :- machine(M).
&diff{ compl(J) - 0 } <= S :- assign(J,M), span(M,S).

makespan(M) :- int(M), M = #max{ S : span(_,S) }.
#minimize{ M : makespan(M) }.


#show makespan/1.
#show span/2.
