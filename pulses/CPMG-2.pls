=== Params ===
excite_t : 3000ns
pi_h : 400ns
pi : 800ns
tau : 2000ns
green_rise_t : 10ns
IR_rise : 10ns
!========   Init pol     
8: 200   | 0 excite_t IR_rise |                                   | # Green Laser
7: 200   |            | 0 pi_h tau+pi+tau+tau+pi+tau pi_h | # MW-X
6: 200   |            | pi_h+tau pi tau+tau pi tau+pi_h   | # MW-Y
0: 0 200 |            |                                   | 0 IR_rise # Trapping beam 
!=== Structure
0, 1, 2^N, 3
!=== Comments
Based on fig 1 from https://journals.aps.org/prb/abstract/10.1103/PhysRevB.86.045214
The + represents leaving the pin in the same state as 
the previous one for the duration of that frame