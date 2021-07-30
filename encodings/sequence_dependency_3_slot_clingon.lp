% slots (clingcon)
% -------------------------------------------------------------

number_of_jobs(N) :- N = #count{J : job(J)}.
&dom{ 0..N } = assign(J) :- job(J), number_of_jobs(N).
&distinct{ assign(J) : job(J) }.

% I assume this solutions doesn't work. The sequence information is stored implicit in the assignment and I didn't find a way how to access this information.
% for instance: I have a job order in form of assign(J) (each job gets a unique number between 0 and number of all jobs), but given a job I can't access the prior or next job.