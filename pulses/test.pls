=== Params ===
t: 100ns
deadt: 440ns
!=============
#    0                 1     2
#   Trig + wait             Wait/deadtime
6:  0 100ns   |        | deadt   # Trig       
1:          | 0 t t  | 0 100ns # Green
2:          |        |         # IR
!=== Structure
0, 1^N, 2
!=== Comments
Pin 6 is wired 