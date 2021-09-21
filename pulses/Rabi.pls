=== Params ===
excite_t : 3.0us
green_fall: 10ns
tau : 400ns
!=============
#   Trig   
0:  0 10 |                           # Trig       
1:       | 0 excite_t green_fall+tau # Green
2:       |                           # IR
4:       | excite_t+green_fall tau   # MW-X
!=== Structure
0, 1^N
!=== Comments