% prefer early release times.
#heuristic assign(J, M) : release(J, M, R), maxRelease(J, T), L=T-R. [L@h1,true]
maxRelease(J, T) :- job(J), T = #max{ R : release(J, _, R)}.
