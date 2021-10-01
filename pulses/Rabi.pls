=== Params ===
excite_t : 3000ns
green_fall: 340ns
ir_hold: 0.2ms
ir_fall: 20us
tau : 400ns
pol_time : 3us
!=============
#    0                             1                              2                      3
#   Trig + wait         pol + tau/RF + wait 30ns      last pol + hold + ir fall   Polarise + wait           Deadtime and last pol
0:  0 20 100        |                              |                          |                           | 60us          # Trig       
1:                  | 0 excite_t green_fall+tau+30 |                          | 0 pol_time green_fall     | 0 excite_t    # Green
2:                  |                              | excite_t ir_hold ir_fall |                           |     # IR
4:                  | excite_t+green_fall tau 30   |                          |                           |     # MW-X
!=== Structure
2, 3, 0, 1^N, 4
!=== Comments