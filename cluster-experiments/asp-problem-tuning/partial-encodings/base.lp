% completion time starts after the jobs processing time and immediate predecessors completion time.
&diff{ completion(JB) - completion(J) } <= -(S+D) :- next(JB, J, M), setup(JB, J, M, S), duration(J, M, D).

% completion time starts after setup + duration + release time.
&diff{ 0 - completion(J) } <= -(R+D+S) :- release(J, M, R), duration(J, M, D), next(JB, J, M), setup(JB, J, M, S).

% completion time starts after duration + release time.
&diff{ 0 - completion(J) } <= -(R+D) :- assign(J, M), release(J, M, R), duration(J, M, D).

% makespan is max completion time.
&diff{ completion(J) - makespan } <= 0 :- job(J).