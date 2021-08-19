% include solution generator.
#include "../generators/slots.lp".

% set the time domain.
int(1..H) :- horizon(H).

% each job calculates the processing time.
processing(J, T) :- first(J, M), duration(J, M, T).
processing(J, T1+T2) :- next(I, J, M), duration(J, M, T1), setup(I, J, M, T2).

% each job calculates the start time.
start(J, T) :- first(J, M), release(J, M, T).
start(J1, T) :- int(T), next(J2, J1, M), T=#max{T1 : release(J1, M, T1); T2 : complete(J2, T2)}.

% each job calculates the completion time.
complete(J, T1+T2) :- start(J, T1), processing(J, T2).

% define the machine span, total makespan and minimize
span(M,T) :- last(J,M), complete(J,T).
makespan(M) :- M = #max{ T : span(_,T) }.
#minimize{ M : makespan(M) }.


#show makespan/1.
#show assign/2.
#show first/2.
#show next/3.
