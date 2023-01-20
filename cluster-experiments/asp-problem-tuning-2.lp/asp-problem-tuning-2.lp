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
&diff{ 0 - completion(J) } <= -(R+D+S) :- release(J, M, R), duration(J, M, D), next(JB, J, M), setup(JB, J, M, S).

% completion time starts after duration + release time.
&diff{ 0 - completion(J) } <= -(R+D) :- assign(J, M), release(J, M, R), duration(J, M, D).

% makespan is max completion time.
&diff{ completion(J) - makespan } <= 0 :- job(J).

% completion time must be between zero and horizon.
&diff{ 0 - completion(J) } < 0 :- job(J).
&diff{ completion(J) - 0 } <= H :- job(J), horizon(H).

% previous completion times are always smaller.
&diff{ completion(JB) - completion(J) } < -D :- before(JB, J, M), duration(J, M, D).

% assign jobs to machine with the least jobs.
#heuristic assign(J, M) : capable(M, J), number_of_jobs(M, N), total_number_of_jobs(T), L=T-N. [L@3,true]
total_number_of_jobs(N) :- N = #count{ J : job(J) }.
number_of_jobs(M, N) :- machine(M), N = #count{ J : assign(J, M) }.

% prefer machines where job duration is low.
#heuristic assign(J, M) : duration(J, M, D), maxDuration(J, T), L=T-D. [L@0,true]
maxDuration(J, M) :- job(J), M = #max{ D : duration(J,_,D) }.

% prefer short setup times.
#heuristic next(J1, J2, M) : setup(J1, J2, M, S), maxSetup(J2, M, T), capable(J1, M), capable(J2, M), L=T-S. [L@0,true]
maxSetup(J, M, S) :- job(J), machine(M), S = #max{ T : setup(_, J, M, T) }.


#show first/2.
#show next/3.
