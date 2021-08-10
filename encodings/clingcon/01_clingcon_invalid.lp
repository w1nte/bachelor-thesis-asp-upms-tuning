% we assign each job to one capable machine.
{ assign(J, M) : capable(M, J) } = 1 :- job(J).

% set domain from release time to horizon.
&dom{R..T} = start(J) :- horizon(T), assign(J, M), release(J, M, R).

% jobs and their setup time must not overlap.
:- assign(J1, M), assign(J2, M), duration(J1, M, D1), duration(J2, M, D2), setup(J1, J2, M, S), &sum{start(J2); -start(J1)} <= D1+S, &sum{start(J1); -start(J2)} <= 0.

% calculate completion time
&sum{start(J);D} = compl(J) :- assign(J, M), duration(J, M, D).

% calculate makespan
&diff{ compl(J) - makespan } <= 0 :- job(J).

&minimize{ makespan }.


% This approach doesn't find the best schedule.
% In comparison to the former approaches this encodings makespan is probably correct but not optimal.
% I assume the constraint isn't strongth enough because I ignored the sequence dependency.
% Consider this example: There are 3 jobs and one machine. 
% The best schedule is j1->j2->j3, the worst j1->j3->j2 because of the large setup time j1->j3.
% But because I ignored the sequence dependency, the constraint above deletes the solution j1->j2->j3 and prefers j1->j3->j2.