from os import read
from .structured_seq import parse_complex_structure
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
    # sections = {k:None for k in ["PARAMS", "SEQ", "STRUCT"]}
    # pu.AbstractSequence(None)

    found_symbols = {}
    # Get the parameter values
    for line in lines:
        line = ignore_comments(line)
        if not line: continue
        if "!" in line: break
        if "=" in line: continue
        sym, value = line.split(":")
        sym, value = sym.strip(), value.strip()
        if sym not in found_symbols:
            print(f"Found symbol: {sym}")
            if "." not in value:
                dtype = int
            else:
                dtype = float
            found_symbols[sym] = u.Quantity(value, dtype=dtype)

    pulses = []


    # Go through each line
    in_params_block = True
    structure = None
    for ln, line in enumerate(lines):
        line = ignore_comments(line)
        if not line: continue
        if in_params_block:
            if "!" in line:
                in_params_block = False
            continue
        if "!" in line:
            # When we find the second ! we are entering the structure or 
            # comments section, either way we are done reading the sequence
            if "structure" in line.lower():
                structure = lines[ln+1]
                structure = structure.replace("\n", "")
                print("Found structure: ", structure)
            break
        # After this point we know we are in the sequence part of the file
        bit, seq = line.split(":")
        bit = int(bit)
        seq = seq.replace(",", " ")
        seq = seq.replace("+", " 0 ")
        seq = seq.split()
        # Begin with the first sequence, increase after each '|' character
        seq_num = 0
        seq_all = [[]]
        for i, word in enumerate(seq):
            if seq_num >= len(seq_all):
                # Create a new sequence list if there isn't already enough
                seq_all.append(list())
            try:
                if word == '|':
                    # Move onto the next sequence
                    seq_num += 1
                    continue
                if "." not in word:
                    dtype = int
                else:
                    dtype = float
                val = u.Quantity(word, dtype=dtype)
                if str(val.unit) == '':
                    val *= u.ns
            except (ValueError, TypeError):
                # Try keep it as a symbol
                val = word
                if val not in found_symbols:
                    print(f"Found symbol: {val}")
                    found_symbols[val] = None
            else:
                val = round(val.to("ns").value) # Convert to value in nanoseconds
            finally:
                if word != "|":
                    seq_all[seq_num].append(val)
        while seq_num >= len(pulses):
            new_pulse = pu.AbstractSequence(None)
            new_pulse.set_param_default(**found_symbols)
            pulses.append(new_pulse)
        for seq, pulse in zip(seq_all, pulses):
            pulse.add_seq([bit], [seq])
    if len(pulses) == 1:
        return pulse
    else:
        struct_pulse = parse_complex_structure(pulses, structure)
        return struct_pulse


if __name__ == "__main__":
    # p = read_pulse_file("pulses/Ramsey.pls")
    # p.set_controller(pu.SequenceProgram())
    # pu.init_board()
    # print(p.flag_seqs)
    # # p.set_param_default(tau=300., pi_h=400.)
    # # p.evaluate_params('tau', 'pi_h', 'pi')
    # # p.evaluate_params(excite_t=2*u.us, tau=12)
    # print(p.flag_seqs)
    # p.program_seq(tau=300)
    # p.program_seq(tau=0.6*u.us, end_action=actions.LE)
    # e1 = p.eval(tau=100)
    # for tau in range(200, 1000, 100):
    #     eN = p.eval(tau=tau)
    #     e1 = e1 + eN
    # # e2 = p.eval(tau=600)
    # # s = e1 + e2
    # e1.plot_sequence()
    
    p = read_pulse_file("pulses/CPMG-2.pls")
    # a = p.eval(N=5)
    # p = read_pulse_file("pulses/test.pls")
    a = p.eval(N=4, M=64, tau=np.linspace(12, 2000, 64))
    a.plot_sequence()

    

    