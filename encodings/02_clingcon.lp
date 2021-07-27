% we assign each job to one capable machine.
{ assign(J, M) : capable(M, J) } = 1 :- job(J).

% we calculate the number of jobs per machine.
number_of_jobs(M, N) :- machine(M), N = #count{J : assign(J, M)}.

&dom{0..N} = assign(J, M) :- assign(J, M), number_of_jobs(M, N).


#show number_of_jobs/2.
#show assign/2.