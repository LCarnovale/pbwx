import numpy as np
from astropy import units as u

from . import pulse_utils as pu
from . import _actions as actions

def ignore_comments(line:str):
    # Ignore any characters after a '#'
    try:
        end = line.index('#')
    except:
        return line
    else:
        return line[:end]

def read_pulse_file(filename):
    """ Read data from a file and create a pulse object. """
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()

    pulse = pu.AbstractSequence(None)

    found_symbols = {}
    # Get the parameter values
    for line in lines:
        line = ignore_comments(line)
        if "!" in line: break
        if "=" in line: continue
        sym, value = line.split(":")
        sym, value = sym.strip(), value.strip()
        if sym not in found_symbols:
            print(f"Found symbol: {sym}")
            found_symbols[sym] = u.Quantity(value)

    pulse.set_param_default(**found_symbols)


    # Go through each line
    in_params_block = True
    for line in lines:
        line = ignore_comments(line)
        if in_params_block:
            if "!" in line:
                in_params_block = False
            continue
        if "!" in line:
            # When we find the second ! we are entering the comments section
            break
        bit, seq = line.split(":")
        bit = int(bit)
        seq = seq.replace(",", " ")
        seq = seq.split()
        for i, word in enumerate(seq):
            if word == "+":
                word = "0"
            try:
                val = u.Quantity(word)
                if str(val.unit) == '':
                    val *= 1*u.ns
            except (ValueError, TypeError):
                # Try keep it as a symbol
                val = word
                if val not in found_symbols:
                    print(f"Found symbol: {val}")
                    found_symbols[val] = None
            else:
                val = int(val / u.ns) # Convert to value in nanoseconds
            finally:
                seq[i] = val
        pulse.add_seq([bit], [seq])
    return pulse

if __name__ == "__main__":
    p = read_pulse_file("pulses/Ramsey.pls")
    p.set_controller(pu.SequenceProgram())
    pu.init_board()
    print(p.flag_seqs)
    # p.set_param_default(tau=300., pi_h=400.)
    # p.evaluate_params('tau', 'pi_h', 'pi')
    # p.evaluate_params(excite_t=2*u.us, tau=12)
    print(p.flag_seqs)
    p.program_seq(tau=300)
    p.program_seq(tau=0.6*u.us, end_action=actions.LE)
    p.plot_sequence('excite_t', 'pi_h',tau=300)
    

    

    