=== Params ===
excite_t : 3000ns
pi_h : 400ns
pi : 800ns
tau : 2000ns
green_rise_t : 10ns
IR_rise : 10us
hold_time : 1ms
!========          Init pol                                          Hold particle
0: 0 10          |                                                                       # Trigger
1:               | 0 excite_t |                                   |                      # Green Laser
2: 0 200 IR_rise |            |                                   | 0 hold_time IR_rise  # Trapping beam 
3:               |            | pi_h+tau pi tau+tau pi tau+pi_h   |                      # MW-Y
4:               |            | 0 pi_h tau+pi+tau+tau+pi+tau pi_h |                      # MW-X
!=== Structure
0, (1, 2^N)^M, 3
!=== Comments
Based on fig 1 from https://journals.aps.org/prb/abstract/10.1103/PhysRevB.86.045214
The + represents leaving the pin in the same state as 
the previous one for the duration of that frame