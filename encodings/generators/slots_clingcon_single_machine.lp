% slot method for clingcon, but for only one machine.
% -------------------------------------------------------------

job(1..3).

number_of_jobs(N) :- N = #count{J : job(J)}.
&dom{ 1..N } = assign(J) :- job(J), number_of_jobs(N).
&distinct{ assign(J) : job(J) }.

next(J1, J2) :- &sum{ assign(J1); -assign(J2) } = -1, job(J1), job(J2).

#show next/2. 