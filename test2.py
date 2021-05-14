# from pulse_utils import *

import pulse_utils as pu

import numpy as np

from spinapi import ns, us, ms
s = 1000*ms

cont = pu.SequenceProgram()
rs = pu.RawSequence(cont, post_delay=0.25*us)

TRIG = 7
AOM = 6

trig_seq = np.array([0,   1.,])*us
rf_seq   = (np.arange(9) * 0.25 + 0.25) * us
# trig_seq = rf_seq
# rf_seq   = np.array([0.5, 1., 1.3, 1.6, 1.9, 2.2, 2., 3.])*us

rs.add_seq(TRIG, trig_seq)
rs.add_seq(AOM, rf_seq)

pu.init_board()
rs.program_seq()


import time
try:
    cont.run()
    input("Running. Enter to stop.")
except Exception as e:
    print("An error occurred, stopping.")
    raise e
finally:
    cont.stop()
