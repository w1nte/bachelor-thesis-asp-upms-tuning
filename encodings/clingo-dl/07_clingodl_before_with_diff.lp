{ assign(J, M) : capable(M, J) } = 1 :- job(J).

% define before relation
before(J1, J2, M) :- &diff{ completion(J1) - completion(J2) } < 0, assign(J1, M), assign(J2, M).

% define first
{ first(J, M) : assign(J, M) } = 1 :- machine(M).
:- first(J, M), before(JB, J, M).

% define last
{ last(J, M) : assign(J, M) } = 1 :- machine(M).
:- last(J, M), before(J, JB, M).

% define next
1 { next(J1, J2, M) : before(J1, J2, M) } 1 :- assign(J2, M), not first(J2, M).
1 { next(J2, J1, M) : before(J2, J1, M) } 1 :- assign(J2, M), not last(J2, M).

% calculate completion time
&diff{ completion(JB) - completion(J) } <= -(S+D) :- next(JB, J, M), setup(JB, J, M, S), duration(J, M, D).

% job completes after setup + duration + release time.
&diff{ 0 - completion(J) } <= -(R+D+S) :- assign(J, M), release(J, M, R), duration(J, M, D), next(JB, J, M), setup(JB, J, M, S).

% job completes after duration + release time.
&diff{ 0 - completion(J) } <= -(R+D) :- assign(J, M), release(J, M, R), duration(J, M, D).

% makespan is max completion time.
&diff{ completion(J) - makespan } <= 0 :- job(J).

% completion time must be between zero and horizon.
&diff{ 0 - completion(J) } < 0 :- job(J).
&diff{ completion(J) - 0 } <= H :- job(J), horizon(H).

% previous completion times are always smaller.
&diff{ completion(JB) - completion(J) } < -D :- before(JB, J, M), duration(J, M, D).

% completion time must be greater than prev completion times.
&diff{ completion(JAB) - completion(J) } <= -(S+D) :- before(JAB, J, M), next(JB, J, M), setup(JB, J, M, S), duration(J, M, D).

% completion time is max completion time before + setup + duration + release.
&diff{ completion(J) - completion(JB) } <= (R+S+D) :- next(JB, J, M), setup(JB, J, M, S), duration(J, M, D), release(J, M, R).

#show assign/2.
