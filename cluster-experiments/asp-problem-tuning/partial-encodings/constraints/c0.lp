% completion time must be between zero and horizon.
&diff{ 0 - completion(J) } < 0 :- job(J).
&diff{ completion(J) - 0 } <= H :- job(J), horizon(H).