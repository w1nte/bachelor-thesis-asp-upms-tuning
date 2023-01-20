% prefer machines where job duration is low.
#heuristic assign(J, M) : duration(J, M, D), maxDuration(J, T), L=T-D. [L@h2,true]
maxDuration(J, M) :- job(J), M = #max{ D : duration(J,_,D) }.
