=== Params ===
excite_t : 3000ns
green_fall: 340ns
ir_hold: 1ms
ir_fall: 20us
tau : 400ns
pol_time : 10us
!=============
#    0                             1                              2                      3
#   Trig + wait         pol + tau/RF + wait 30ns      last pol + hold + ir fall   Polarise + wait
0:  0 20 green_fall |                              |                          |                           # Trig       
1:                  | 0 excite_t green_fall+tau+30 | 0 excite_t               | 0 pol_time green_fall+100 # Green
2:                  |                              | excite_t ir_hold ir_fall |                           # IR
4:                  | excite_t+green_fall tau 30   |                          |                           # MW-X
!=== Structure
2, 3, 0, 1^N, 2
!=== Comments