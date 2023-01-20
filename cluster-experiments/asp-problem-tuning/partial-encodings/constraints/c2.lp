% completion time must be greater than previous completion times.
&diff{ completion(JAB) - completion(J) } <= -(S+D) :- before(JAB, J, M), next(JB, J, M), setup(JB, J, M, S), duration(J, M, D).