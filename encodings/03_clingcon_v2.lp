#include "sequence_dependency_2_slot.lp".

&dom{ 0..N } = span(M) :- machine(M), horizon(N).
&diff{ span(M) - makespan } <= 0 :- machine(M).

&minimize{ makespan }.