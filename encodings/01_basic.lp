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
int(1..H) :- horizon(H).

% we calculate the processing time for each job.
processing(J, T) :- first(J, M), duration(J, M, T).
processing(J, T1+T2) :- next(I, J, M), duration(J, M, T1), setup(I, J, M, T2).

% we calculate the start time for each job.
start(J, T) :- first(J, M), release(J, M, T).
start(J1, T) :- int(T), next(J2, J1, M), T=#max{T1 : release(J1, M, T1); T2 : complete(J2, T2)}.

% we calculate the completion time for each job.
complete(J, T1+T2) :- start(J, T1), processing(J, T2).

% we define the machine span, total makespan and minimize
span(M,T) :- last(J,M), complete(J,T).
makespan(M) :- M = #max{ T : span(_,T) }.
#minimize{ M : makespan(M) }.


#show makespan/1.
#show span/2.