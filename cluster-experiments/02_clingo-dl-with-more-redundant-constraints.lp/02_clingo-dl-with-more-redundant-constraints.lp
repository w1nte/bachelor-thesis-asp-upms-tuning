% assign jobs to capable machines
{ assign(J, M) : capable(M, J) } = 1 :- job(J).

% pick first and last job for each 
{ first(J, M) : assign(J, M) } = 1 :- assign(_, M).
{ last(J, M) : assign(J, M) } = 1 :- assign(_, M).

% define before relation
before(J1, J2, M) | before(J2, J1, M) :- assign(J1, M), assign(J2, M), J1 < J2.
:- first(J1, M), before(J2, J1, M).
:- last(J1, M), before(J1, J2, M). 

% pick an immediate predecessor
{ next(J1, J2, M) : before(J1,J2,M) } = 1 :- assign(J2, M), not first(J2, M).
{ next(J2, J1, M) : before(J2,J1,M) } = 1 :- assign(J2, M), not last(J2, M).

% completion time starts after the jobs processing time and immediate predecessors completion time.
&diff{ completion(JB) - completion(J) } <= -(S+D) :- next(JB, J, M), setup(JB, J, M, S), duration(J, M, D).

% completion time starts after setup + duration + release time.
&diff{ 0 - completion(J) } <= -(R+D+S) :- assign(J, M), release(J, M, R), duration(J, M, D), next(JB, J, M), setup(JB, J, M, S).

% completion time starts after duration + release time.
&diff{ 0 - completion(J) } <= -(R+D) :- assign(J, M), release(J, M, R), duration(J, M, D).

% makespan is max completion time.
&diff{ completion(J) - makespan } <= 0 :- job(J).

% completion time must be between zero and horizon.
&diff{ 0 - completion(J) } < 0 :- job(J).
&diff{ completion(J) - 0 } <= H :- job(J), horizon(H).

% previous completion times are always smaller.
&diff{ completion(JB) - completion(J) } < -D :- before(JB, J, M), duration(J, M, D).

% completion time must be greater than previous completion times.
&diff{ completion(JAB) - completion(J) } <= -(S+D) :- before(JAB, J, M), next(JB, J, M), setup(JB, J, M, S), duration(J, M, D).

% completion time is max completion time before + setup + duration + release.
&diff{ completion(J) - completion(JB) } <= (R+S+D) :- next(JB, J, M), setup(JB, J, M, S), duration(J, M, D), release(J, M, R).


#show first/2.
#show next/3.
