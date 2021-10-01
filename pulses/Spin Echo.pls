=== Params ===
excite_t : 3000ns
green_fall: 340ns
ir_hold: 0.2ms
ir_fall: 15us
tau : 400ns
pi_h : 400ns
pi : 800ns
!=============
#  Wait for IR off   Trig        polarise, wait, spinecho, wait                                   hold 
0:  ir_fall        |  excite_t+green_fall 20 100 |                                                                                   # Trig       
1:                 | 0 excite_t green_fall | 0 excite_t green_fall + pi_h + tau + pi + tau + pi_h + 30ns   |                   # Green
2:                 |           |                                                               | 0 ir_hold ir_fall # IR
4:                 |           | excite_t + green_fall pi_h tau pi tau pi_h 30ns               |                   # MW-X
!=== Structure
0, 1, 2^N, 3
!=== Comments