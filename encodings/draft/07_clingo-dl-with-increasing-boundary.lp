% Should be a improvement of the approach with boundary.
% The idea here is to force a low makespan at the beginning, but softening the boundary stepwise short after.

#include "../clingo-dl/01_clingo-dl-with-before-relation.lp".
#include "../heuristics/prefer_short_durations.lp".
#include "../heuristics/prefer_short_setuptimes.lp".
#include "../heuristics/prefer_early_release.lp".


maxDuration(J, D) :- job(J), D = #max{ T : duration(J,_,T) }.
durationSum(S) :- S = #sum{ T,J : maxDuration(J, T) }.
numberOfMachines(N) :- N = #count{ M : machine(M) }.


lowerBound(L) :- L=c.
upperBound(U) :- horizon(H).
steps(S) :- S=f.

% set boundary domain.
int(I) :- I=L..U, 0=I\S, lowerBound(L), upperBound(U), steps(S).

% pick boundary.
{ bound(I) : int(I) } = 1.

% expand the boundary upwards.
#heuristic bound(I) : maxInt(M), int(I), L=M-I. [L@10,true]
maxInt(I) :- I = #max{ J : int(J) }.

% makespan is less or equal than boundary.
&diff{ makespan - 0 } <= B :- assign(J, M), bound(B).


#show bound/1.
#show int/1.