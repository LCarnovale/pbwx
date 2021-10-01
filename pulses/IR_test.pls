=== Params ===
IR_on : 50us
green_delay : 40us
green_on : 40us
!=============
#    0                    1                         
#  Trig      start IR and green delay     deadtime
0:  0 20    |                           |  20us # Trig
1:          | green_delay green_on     350ns |  # Green
2:          | 0 IR_on 350ns                   |  # IR
!=== Structure
0, 1^N, 2
!=== Comments
This is meant to test the effect of IR on the NV PL