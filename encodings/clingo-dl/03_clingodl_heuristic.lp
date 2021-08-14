% imports the solutions generator. This encoding needs assign/2, next/3 and before/3.
#include "../generators/before_relation.lp".

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

#include "../heuristics/prefer_short_durations.lp".
#include "../heuristics/prefer_short_setuptimes.lp".
#include "../heuristics/prefer_early_release.lp".

#show assign/2.