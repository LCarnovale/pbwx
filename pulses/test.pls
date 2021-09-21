=== Params ===
pi_h : 400ns
pi   : 800ns
tau  : 100ns
!=============
#0: 0 10  |                                                            # Trigger
#1: 200   | 0 excite_t IR_rise |                           |           # Green Laser
#2: 0 200 |            |                                   | 0 IR_rise # Trapping beam 
#3: 200   |            | pi_h+tau pi tau+tau pi tau+pi_h   |           # MW-Y
#4: 200   |            | 0 pi_h tau+pi+tau+tau+pi+tau pi_h |           # MW-X
0: 0 10 |                     # Trigger
1:      | 1us 1us tau         # Green
2:      | 10us  tau+20ns      # IR
!=== Structure
0, 1^N
!=== Comments
Should be: