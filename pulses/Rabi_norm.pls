=== Params ===
excite_t : 3000ns
green_fall: 460ns
ir_hold: 0.2ms
ir_fall: 50us
tau : 20ns
pol_time : 15us
!=============
#             0                             1                              2                      3                         4                              5              
#        Trig + wait           pol + tau/RF + wait 30ns      last pol + hold + ir fall   Polarise + wait            Deadtime and last pol    normalisation, no MW     
0 (Trig) :  0 200 100        |                              |                          |                           | 30us                  |                              # Trig       
1 (Green):                   | 0 excite_t green_fall+tau+30 |                          | 0 pol_time green_fall     | 0 excite_t            | 0 excite_t green_fall+tau+30 # Green
2 (IR)   :                   |                              | excite_t ir_hold ir_fall |                           |                       |                              # IR
4 (MW-X) :                   | excite_t+green_fall tau 30   |                          |                           |                       |                              # MW-X
!=== Structure        
2, 3, 0, (1, 5)^N, 4
!=== Comments