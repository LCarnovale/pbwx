=== Params ===
excite_t : 3000ns
green_delay: 550ns
green_fall: 100ns
ir_hold: 0.2ms
ir_fall: 40us
pol_time : 15us
rf_fall : 50ns
tau : 50ns
!=============
#             0                             1                              2                            3                         4                      5                  6
#        Trig + wait           pol + tau/RF + wait 30ns                 hold + ir fall           Polarise + wait             First  pol       normalisation, no MW          Deadtime
0 (Trig) :  0 200 100        |                                     |                          |                           |              |                                  | 20us # Trig       
1 (Green):                   | green_fall+tau+rf_fall excite_t     |                          | 0 pol_time green_delay    | 0 excite_t   | green_fall+tau+rf_fall excite_t  | # Green
2 (IR)   :                   |                                     | excite_t ir_hold ir_fall |                           |              |                                  | # IR
4 (MW-X) :                   | green_fall+green_delay tau          |                          |                           |              |                                  | # MW-X
!=== Structure        
2, 3, 0, 4, (1, 5)^N, 6
!=== Comments

\/ \/ This is the normal Rabi v2 sequence \/ \/ 
=== Params ===
excite_t : 3000ns
green_delay: 460ns
green_fall: 30ns
ir_hold: 0.2ms
ir_fall: 50us
pol_time : 15us
rf_fall: 20ns
tau : 20ns
!=============
#               0                             1                                  2                       3                     4             5
#          Trig + wait                  tau/RF + pol                       hold + ir fall          Polarise + wait           First pol      Deadtime
0 (Trig) :  0 200 100        |                                      |                          |                           |             | 20us
1 (Green):                   | green_fall+tau+rf_fall green_fall+excite_t   |                          | 0 pol_time green_delay    | 0 excite_t  |
2 (IR)   :                   |                                      | excite_t ir_hold ir_fall |                           |             |
4 (MW-X) :                   | green_fall+green_delay tau           |                          |                           |             |
!=== Structure
2, 3, 0, 4, 1^N, 5
!=== Comments
green_delay is the time delay before seeing the green laser respond to a pulse 