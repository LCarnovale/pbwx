=== Params ===
excite_t : 3000ns
green_delay: 460ns
green_fall: 230ns
ir_hold: 0.2ms
ir_fall: 50us
pol_time : 15us
rf_fall: 20ns
tau_on : 20ns
!=============
#               0                             1                                          2                       3                     4             5
#          Trig + wait                  tau/RF + pol                               hold + ir fall          Polarise + wait           First pol      Deadtime
0 (Trig) :  0 200 100        |                                              |                          |                           |             | 20us
1 (Green):                   | green_fall+tau_on+tau_off+rf_fall excite_t   |                          | 0 pol_time green_delay    | 0 excite_t  |
2 (IR)   :                   |                                              | excite_t ir_hold ir_fall |                           |             |
4 (MW-X) :                   | green_fall+green_delay+tau_off tau_on        |                          |                           |             |
!=== Structure
2, 3, 0, 4, 1^N, 5
!=== Comments
green_delay is the time delay before seeing the green laser respond to a pulse 