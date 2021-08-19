% prefer short setup times.
#heuristic next(J1, J2, M) : setup(J1, J2, M, S), maxSetup(J2, M, T), capable(J1, M), capable(J2, M), L=T-S. [L@1,true]
maxSetup(J, M, S) :- job(J), machine(M), S = #max{ T : setup(_, J, M, T) }.
