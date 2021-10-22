=== Params ===
excite_t : 3000ns
green_delay: 550ns
green_fall: 50ns
ir_hold: 0.3ms
ir_fall: 50us
pol_time : 15us
rf_fall : 25ns
tau_on : 20ns
!=============
#             0                             1                                         2                            3                         4                      5                            6
#        Trig + wait           pol + tau/RF + wait 30ns                            hold + ir fall           Polarise + wait             First  pol       normalisation, no MW                    Deadtime
0 (Trig) :  0 200 100        |                                                |                          |                           |              |                                            | 20us # Trig       
1 (Green):                   | green_fall+tau_on+tau_off+rf_fall excite_t     |                          | 0 pol_time green_delay    | 0 excite_t   | green_fall+tau_on+tau_off+rf_fall excite_t | # Green
2 (IR)   :                   |                                                | excite_t ir_hold ir_fall |                           |              |                                            | # IR
4 (MW-X) :                   | green_fall+green_delay+tau_off tau_on          |                          |                           |              |                                            | # MW-X
!=== Structure        
2, 3, 0, 4, (1, 5)^N, 6
!=== Comments
