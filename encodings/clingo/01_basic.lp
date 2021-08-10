% we generate the solutions.
#include "../generators/slots.lp".

% we set the time domain.
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