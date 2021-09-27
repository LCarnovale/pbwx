=== Params ===
excite_t : 3000ns
green_fall: 10ns
ir_hold: 1ms
ir_fall: 10us
tau : 400ns
pi_h : 400ns
pi : 800ns
!=============
#   Trig   
0:  0 10 |                                                  |                   # Trig       
1:       | 0 excite_t green_fall + pi_h + tau+pi+tau+pi_h   |                   # Green
2:       |                                                  | 0 ir_hold ir_fall # IR
4:       |   excite_t+green_fall   pi_h   tau pi tau pi_h   |                   # MW-X
!=== Structure
0, 1^N, 2
!=== Comments