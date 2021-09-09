#include "01_clingodl.lp".
#include "../heuristics/prefer_short_durations.lp".
#include "../heuristics/prefer_short_setuptimes.lp".
#include "../heuristics/prefer_early_release.lp".


maxDuration(J, D) :- job(J), D = #max{ T : duration(J,_,T) }.
durationSum(S) :- S = #sum{ T,J : maxDuration(J, T) }.
numberOfMachines(N) :- N = #count{ M : machine(M) }.


lowerBoundary(L) :- L=c.
upperBoundary(U) :- horizon(H).
steps(S) :- S=f.

% set boundary domain.
int(I) :- I=L..U, 0=I\S, lowerBoundary(L), upperBoundary(U), steps(S).

% pick boundary.
{ boundary(I) : int(I) } = 1.

% expand the boundary upwards.
#heuristic boundary(I) : maxInt(M), int(I), L=M-I. [L@10,true]
maxInt(I) :- I = #max{ J : int(J) }.

% makespan is less or equal than boundary.
&diff{ makespan - 0 } <= Boundary :- assign(J, M), boundary(Boundary).


#show boundary/1.
#show int/1.