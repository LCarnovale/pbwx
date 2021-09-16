=== Params ===
excite_t : 3000ns
pi_h : 400ns
tau : 2000ns
!=============
8: 0 excite_t pi_h + tau + pi_h # Green Laser
7:   excite_t pi_h tau pi_h     # MW
!=== Comments
The + represents leaving the pin in the same state as 
the previous one for the next frame duration