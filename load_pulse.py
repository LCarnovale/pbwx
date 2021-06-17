import numpy as np
from astropy import units as u
try:
    import pbwx.pulse_utils as pu
except ImportError:
    try:
        import pulse_utils as pu
    except ImportError:
        raise ImportError("Unable to import pulse_utils")


def read_pulse_file(filename):
    """ Read data from a file and create a pulse object. """
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()

    pulse = pu.AbstractSequence(None)

    found_symbols = {}
    # Get the parameter values
    for line in lines:
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
            try:
                val = u.Quantity(word)
                if str(val.unit) == '':
                    val *= 1*u.ns
            except (ValueError, TypeError):
                # Try keep it as a symbol
                val = word
                if val not in found_symbols:
                    print(f"Found symbol: {val}")
                    found_symbols.append(val)
            else:
                val = int(val / u.ns) # Convert to value in nanoseconds
            finally:
                seq[i] = val
        pulse.add_seq([bit], [seq])
    return pulse

if __name__ == "__main__":
    p = read_pulse_file("pbwx/pulses/test.pls")
    p.set_controller(pu.SequenceProgram())
    pu.init_board()
    print(p.flag_seqs)
    # p.set_param_default(tau=300., pi_h=400.)
    p.evaluate_params('tau', 'pi_h', 'pi')
    print(p.flag_seqs)
    p.program_seq()
    p.plot_sequence()

    

    