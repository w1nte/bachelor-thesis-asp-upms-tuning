% assign jobs to machine with the least jobs.
#heuristic assign(J, M) : capable(M, J), number_of_jobs(M, N), total_number_of_jobs(T), L=T-N. [L@2,true]
total_number_of_jobs(N) :- N = #count{ J : job(J) }.
number_of_jobs(M, N) :- machine(M), N = #count{ J : assign(J, M) }.
