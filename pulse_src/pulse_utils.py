import threading

import matplotlib.pyplot as plt
import numpy as np
from astropy import units as u
from scipy import interpolate

from . import _actions as actions
from .spinapi import *

# try:
# except ImportError:
#     raise Exception()
#     try:
#         from pbwx.spinapi import *
#     except ImportError as e:
#         e.msg = "Unable to find spinapi module in " \
#                 "pbwx package or local directory."
#         raise e
        
    
LOG_PROG = True
LOG_FILE = "logs/program_log"
log_n = 0
SAFE_MODE = False
if SAFE_MODE:
    print("SAFE_MODE is enabled, the board will not be programmed.")

# # Configure the core clock
# pb_core_clock(500)

MIN_TIME = 5 # ns

all_bits = 0xFFFFFF
TRIG = (1 << 7) # Trigger for oscilloscope
AOM  = (1 << 6) # RF source for AOM

FLAG_ON  = 1
FLAG_OFF = 0

def init_board():
    """ Call this before using any other functions in this program. """
    if SequenceProgram.board_initialised:
        # No need to initialise twice
        return
    print("Using SpinAPI Library version %s" % pb_get_version())
    print("Found %d boards in the system.\n" % pb_count_boards())

    if pb_init() != 0:
        print("Error initializing board: %s" % pb_get_error())
        input("Please press a key to continue.")
        exit(-1)
    # Enable log file
    pb_set_debug(0)
    # Select the (only) board
    pb_select_board(0)
    # Configure the core clock
    pb_core_clock(500)

    SequenceProgram.board_initialised = True
    
def check_board_init():
    if not SequenceProgram.board_initialised:
        raise Exception("The board has not yet been initialised (call 'init_board()')")


class SequenceProgram(threading.Thread):
    prog_mode = False
    running = False
    board_initialised = False

    def __init__(self, name=None):
        threading.Thread.__init__(self)#, group=None)
        if name is None:
            name = "Untitled Sequence"
        self.name = name
        self.in_prog = False
        self.inst_seq = []


    def run(self):
        """ Begin running the sequence currently programmed on the board. 
        If programming mode is enabled, `self.prog_exit()` will be called 
        before starting the sequence."""
        check_board_init()

        if self.in_prog:
            self.prog_exit()            

        if SequenceProgram.prog_mode:
            raise Exception("Another thread has the board in programming mode.")

        if SequenceProgram.running:
            raise Exception("The board is already running a sequence.")
        
        SequenceProgram.running = True
        pb_reset()
        if not SAFE_MODE:
            pb_start()
        

    def prog_enter(self):
        """ Enter programming mode """
        check_board_init()

        if SequenceProgram.running:
            raise Exception("The board is currently running a sequence.")

        if SequenceProgram.prog_mode:
            raise Exception("The board is already in programming mode.")

        if self.in_prog:
            # Nothing to do
            # This should never happen? We wouldn't get past the previous exception?
            pass

        self.in_prog = True
        SequenceProgram.prog_mode = True
        pb_start_programming(PULSE_PROGRAM)

    def stop(self):
        if SequenceProgram.running:
            pb_stop()
            SequenceProgram.running = False

    def prog_exit(self):
        if self.in_prog:
            self.in_prog = False
            SequenceProgram.prog_mode = False

            pb_stop_programming()
        elif SequenceProgram.prog_mode:
            raise Exception("Another thread has the board in programming mode.")
        # else: the board is not currently in programming mode.

    def add_instruction(self, flags:np.int32, inst:Inst, inst_data:np.int32, length:np.float64,
            log=None):
        check_board_init()
        if length < MIN_TIME:
            raise Exception("Instruction too short - must be at least %d nanoseconds." % MIN_TIME)
        if not self.in_prog:
            raise Exception("Must be in programming mode before adding instructions.")
        try:
            inst = (
                ctypes.c_int(flags), 
                ctypes.c_int(inst), 
                ctypes.c_int(inst_data), 
                (length)
            )
        except Exception as e:
            raise TypeError("Type conversion failed. Values:\n" 
                f"flags: 0b{flags:b}\n"
                f"inst:  {inst}\n"
                f"inst_data:  {inst_data}\n"
                f"length:  {length}\n"
                "Message: "+str(e))
        self.inst_seq.append(inst)
        if log is not None:
            log.write(f"[{flags:08b}] inst: {inst[1].value} inst_data: {inst[2].value} dt: {inst[3]} \n")
        # print([type(x) for x in inst])
        if not SAFE_MODE:
            return pb_inst_pbonly(*inst)
        else:
            return 0

    def get_flag_data(self, flag):
        """ Flag should be an integer representing the bit in interest.
        Returns the sequence as so far programmed for that bit.
        
        Example:
            >>> sp.get_flag_data(1)
            ([0, 1, 5, 6, 10, 12, 13], [0, 1, 0, 0, 1, 0, 1])
        
        Where each of the returned arrays are numpy arrays.

        Output is optimised such that
            >>> s = sp.get_flag_data(1)
            >>> plt.plot(*s, drawstyle='steps-pre')
        Will produce a visual plot of the programmed instructions.
        """
        flag_b = 2**flag
        # Get time values from all instructions
        t_ax = [x[3] for x in self.inst_seq]
        # Get flags of all instructions
        flags = np.array([x[0].value for x in self.inst_seq])
        # Find which flags have the required bit enabled
        vals = (flags & flag_b) // flag_b
        # Convert time axis to cumulative values with a zero at the start.
        t_ax = np.concatenate([[0], np.cumsum(t_ax)], axis=0)
        vals = np.concatenate([[vals[0]], vals], axis=0)
        return t_ax, vals
class EmptyController:
    def __init__(self):
        pass

    def __call__(self):
        raise Exception("Controller for this pulse sequence has not yet been set.")

    def __getattribute__(self, name: str):
        self()
    
    def __eq__(self, other):
        if type(other) != type(self):
            if other is None:
                return True
            else:
                return False
        else:
            return False

class DebugController:
    def __init__(self, name="DebugController"):
        self.name = name
        pass

    def __call__(self, *args, **kwargs):
        self.calling
    
    def __getattr__(self, name: str):
        print(f"{self.name}: {name}")
        return DebugController(name=self.name+"."+name)


class PulseSequence:
    def __init__(self, controller, loop=0, cycle=False):
        """ Create a Pulse Sequence object. 

        `controller` must be a SequenceProgram object, to allow communication to the board.
        It can if needed be left as `None`, but must be set via
        `ps.set_controller()` before making any programming calls.

        Set `loop=0` for no looping, otherwise give the number of times
        this sequence should be repeated.

        Alternatively, set `cycle=True` (default `False`) to make the sequence branch back
        to the beginning, making an infinite loop.
        """
        if controller == None:
            controller = EmptyController()
        self._controller = controller
        self.n_bits = 24
        self.loop = loop
        self.cycle = cycle             
        self._sequence = []            # Sequence of pulse objects

    def set_controller(self, controller):
        self._controller = controller

    def add_raw(self, raw_seq):
        if type(raw_seq) is not RawSequence:
            raise TypeError("raw_seq must be a RawSequence object.")

        # # Create frames
        # t_ax, frames = raw_seq._merge_sequences()
        self._sequence.append(raw_seq)

    
    @property
    def controller(self):
        return self._controller
    
    @property
    def c_params(self):
        try:
            return self.params
        except:
            return {}

    def start(self):
        self._controller.run()

    def stop(self):
        self._controller.stop()


class Marker:
    def __init__(self):
        # self._mark = mark
        # self._sequence = sequence
        self._ref = None

    @property
    def ref(self):
        if self._ref is None:
            raise ValueError("marker has not been set")
        else:
            return self._ref


class RawSequence(PulseSequence):
    def __init__(self, controller, *args, save_refs=True, **kwargs):
        super(RawSequence, self).__init__(controller, *args, **kwargs)
        self.flag_seqs = { n:None for n in range(self.n_bits) }
        self.save_refs = save_refs
        self.markers = {}

    def get_marker(self, frame):
        """ Get a marker object for the specified frame. The first frame
        is frame 0.
        """
        m = Marker()
        self.markers[frame] = m
        return m
    
    def concat(self, other, stretch=True, toggle_odd=True):
        """ Returns a new sequence which is this one followed by the other sequence.
        If `stretch=True` (default) then sequences for flags which are shorter than the
        longest sequence in this sequence are 'stretched', ie they are made to continue
        their last state until the end of the last frame.
        If `toggle_odd=True` (default) then if a sequence in this object has an odd 
        number of toggles, an extra zero-length toggle will be added to make sure each next
        sequence is consistent. 

        `concat` also mapped to the python add magic method, ie:
            >>> A = RawSequence()
            >>> B = RawSequence()

            >>> C = A.concat(B)
        is equivalent to:
            >>> C = A + B
        """
        this_flags = {k:(v.copy() if v else None) for k, v in self.flag_seqs.items()}
        other_flags = {k:(v.copy() if v else None) for k, v in other.flag_seqs.items()}
        new_seq = {k:None for k in self.flag_seqs}
        if stretch:
            # work out the end time:
            times = [sum(seq) for seq in this_flags.values() if seq is not None]
            end_time = max(times)
        for key in this_flags:
            th_seq = this_flags[key] # This_seq
            if th_seq is not None: 
                th_seq = th_seq.copy()
            ot_seq = other_flags[key] # Other_seq
            if ot_seq is not None:
                ot_seq = ot_seq.copy()
            # None + None
            if th_seq is None and ot_seq is None: continue
            # None + [...]
            if th_seq is None and ot_seq is not None:
                new_seq[key] = [end_time, 0] + ot_seq
                continue
            t_full = sum(th_seq)
            if toggle_odd:# and ot_seq is not None:
                if len(th_seq) % 2 != 0:
                    # If prev seq finishes on an ON, add an 
                    # OFF for the rest of the sequence
                    th_seq.append(0)
            if stretch:
                # Assuming toggle_odd=True, the next term will be an OFF
                if end_time > t_full:
                    th_seq += [end_time-t_full, 0]
            if ot_seq is None:
                new_seq[key] = th_seq.copy()
            else:
                new_seq[key] = th_seq + ot_seq
            # Otherwise they are both defined
        new = RawSequence(self.controller, save_refs=self.save_refs)
        new.flag_seqs = new_seq

        return new
                
                
    def eval(self, **kwargs):
        """ No functino for a raw sequence. Just returns itself."""
        return self 


    def __add__(self, other):
        if other is None or other == 0:
            return self
        return self.concat(other)

    def __radd__(self, other):
        if other is None or other == 0:
            return self
        if isinstance(other, RawSequence):
            return other.concat(self)
        else:
            raise TypeError("Cannot r-add these types.")

    def add_seq(self, flags, sequences, t_rel=True):
        """ Add flag toggle times for a given flag.
        For example to turn flag 10 on at 1 second,
        then off at 2 seconds, give:
        ``
            ps.add_seq([10, ...], [[1, 2], ...])
        ``
        If units are present they will be converted to nanoseconds and
        then to scalars.
        
        Set `t_rel` to False if the times given are absolute,
        if `t_rel` is True (default) then if there is already
        an existing sequence for a given flag, the new one will
        be assumed to be relative to the end of the existing sequence.
        ie a value of 10 seconds will be 10 seconds + the end of the
        existing sequence.
        """
        try:
            flags[0]
        except TypeError:
            flags = [flags]
            sequences = [sequences]

        for sequence in sequences:
            if not sequence: continue
            for i in range(len(sequence)):
                try:
                    sequence[i] = sequence[i].to('ns').value 
                except:
                    pass

        for flag, seq in zip(flags, sequences):
            current = self.flag_seqs[flag]
            if np.any(current):
                self.flag_seqs[flag] = np.concatenate([current, current[-1]*t_rel + seq])
            else:
                self.flag_seqs[flag] = seq
    
    def program_seq(self, end_action=None):
        """ Program the Pulse Blaster board with the defined sequences.

        `end_action` must be an Action type from `_actions.py`, or `None` (default), 
        which is equivalent to the Branch instrunction.

        Returns 0 on success, or 1 on failure.
        """
        global log_n
        t_ax, frames = self._merge_sequences()
        pin_sets = [flags_to_number(f) for f in frames]
        # t_lens = (t_ax[1:] - t_ax[:-1])
        t_lens = t_ax
        self._controller.prog_enter()
        if end_action is None:
            # Assume we just want to end the sequence and loop back
            end_action = actions.Branch(0)
        err = 0
        n_insts = 0
        if LOG_PROG:
            log = open(f"{LOG_FILE}_{log_n}", "w")
        try:
            # TODO: Loops? Jumps?
            # Add the starting frame
            start = self.controller.add_instruction(
                pin_sets[0], Inst.CONTINUE, 0, t_lens[0], log=log
            )
            refs = [start]
            n_insts += 1
            # Add the other frames
            for p, dt in zip(pin_sets[1:-1], t_lens[1:-1]):
                refs.append(
                    self.controller.add_instruction(
                        p, Inst.CONTINUE, 0, dt, log=log
                    )
                )
                n_insts += 1
            # Add the final frame, which branches back to the beginning
            refs.append(
                self.controller.add_instruction(
                    pin_sets[-1], end_action.inst, start, t_lens[-1], log=log
                )
            )
            n_insts += 1

        except Exception as e:
            err = 1
            raise e
        else:
            if self.save_refs:
                self._refs = refs
        finally:
            if err:
                print("Aborting programming, exiting programming mode.")
            else:
                print("Programming completed successfully. Sequence length: %.2f ms / %d instructions" % (self.length_ns / 1e6, n_insts))
            self.controller.prog_exit()
            if LOG_PROG:
                log.close()
                log_n += 1
            return err

    def plot_sequence(self):
        # Get frame flags (ie on/off values for each frame, for each flag)
        t_ax, frames = self._merge_sequences()
        # Pick the flags which are not all zeros
        nonz_flags = np.array([k for k, v in self.flag_seqs.items() if v is not None])
        # Turn time axis into one we can plot
        t_ax = t_ax.cumsum()
        if t_ax[0] != 0:
            # If the time axis doesn't start at zero, add a t=0 frame
            t_ax = np.concatenate([[0], t_ax])
            frames = np.concatenate([frames[[0]], frames[:]], axis=0)
        # Get flag numbers to show on plot
        flag_nums = np.arange(frames.shape[1])
        # Exclude frames which are all zero
        frames = frames[:,nonz_flags]
        flag_nums = flag_nums[nonz_flags]
        # Vertically separate each flag to make it look better
        plot_shifts = np.arange(len(nonz_flags)) * 1.1
        plt.plot(t_ax, frames + plot_shifts, drawstyle='steps-pre')
        plt.legend([str(i) for i in flag_nums])
        plt.show()

    def _merge_sequences(self):
        """ Merge the current sequences to create flag frames,
        intended to be used by the PulseSequence class. 
        """

        # self.flag_seqs is a dict. Create a list of (probably mostly empty)
        # sequences for all required bits. (Maybe just store self.flag_seqs as a list?)
        flag_seqs = []
        for f in range(self.n_bits):
            seq = self.flag_seqs[f]
            if seq is not None:
                flag_seqs.append(seq)
            else:
                flag_seqs.append([])
        
        t_ax, frames = merge_flag_seqs(flag_seqs)
        return t_ax, frames

    def add_raw(self, *args, **kwargs):
        raise NotImplementedError(f"add_raw() not available for subtype {type(self)}")

    @property
    def refs(self):
        if self.save_refs:
            try:
                return self._refs
            except AttributeError:
                return None
        
        raise Exception("No programming has been done and hence no refs exist yet.")
    
    @property
    def length_ns(self):
        lengths = [sum(x) for x in self.flag_seqs.values() if x is not None]
        return max(lengths)

        


def extract_ns(value):
    """ If `value` is a Quantity, convert to nanoseconds and return dimensionless value,
    otherwise just return value. In any case if `value` is dimensionless or a unit of time
    then the output will be dimensionless nanoseconds. Non time units will raise an error."""
    try:
        value.unit
    except:
        return value
    else:
        # The +0 isn't needed but it will catch out non-time units being provided
        return round(value.to("ns").value)


class AbstractSequence(RawSequence):
    """ A sequence which can be represented using parameters, 
    which can be assigned at the last minute before being executed,
    and remain undetermined until then. """
    def __init__(self, controller, *args, **kwargs):
        super(AbstractSequence, self).__init__(controller, *args, **kwargs)
        self.params = {}

    def set_param_default(self, **params):
        """ Provide a parameter and a value as a keyword argument
        to set the default value for that parameter. eg:

        Units of time can be provided, otherwise values will be assumed
        to be in nanoseconds.

        >>> absq.set_param_default(tau=1e2)

        On programming the sequence, if no new value is 
        provided for that parameter, the default will be used. """
        for k, val in params.items():
            params[k] = extract_ns(val)
        self.params.update(**params)

    def add_seq(self, flags, sequences, t_rel=True):
        """ Add flag toggle times, flags must be integers,
        sequences must be a list of lists of strings (to make a new parameter)
        and floats. eg:

        >>> absq.add_seq([1, 3], [[1., 'on_time'], [0., 1., 'off_time']])
        """

        # Ensure flags is a list
        try:
            flags[0]
        except TypeError:
            flags = [flags]
            sequences = [sequences]

        for flag, seq in zip(flags, sequences):
            current = self.flag_seqs[flag]
            if current:
                self.flag_seqs[flag] += seq
            else:
                self.flag_seqs[flag] = seq
            for x in seq:
                if type(x) == str:
                    if x not in self.params:
                        # Add the new parameter
                        self.params[x] = None

    def program_seq(self, end_action=actions.CNT, **params):
        """ Program the sequence to the board. Provide values
        for parameters as keyword arguments, eg:

        >>> absq.program_seq(tau=1e2)

        This will substitute parameters in sequences for the
        given value. If a parameter has not been assigned a default
        value, it must be given a value here, otherwise a ValueError
        will be raised.

        After evaluating and programming, the original parameterised sequence
        will be restored.
        """
        # Check params
        # self.evaluate_params(**params)

        temp_params = self.params.copy()
        temp_params.update(**params)
        if None in temp_params.values():
            # Find missing params
            missing = []
            for p, v in temp_params.items():
                if v == None:
                    missing.append(p)

            raise ValueError("Values must be provided for: %s" % missing)

        # Convert units to scalars
        for k, v in temp_params.items():
            temp_params[k] = extract_ns(v)

        # Create copy of original parameters
        original_seqs = {
            k:(seq.copy() if seq is not None else None) for k, seq in self.flag_seqs.items()
        }
        # Substitute params
        for k, seq in self.flag_seqs.items():
            # Skip empty sequences
            if seq is None: continue
            # Otherwise go through sequence and replace symbols
            for i, v in enumerate(seq):
                if v in temp_params:
                    seq[i] = temp_params[v]

        # Program
        super(AbstractSequence, self).program_seq(end_action=end_action)

        # Return original sequence
        self.flag_seqs = original_seqs

    def eval(self, **kw_params) -> RawSequence:
        """ Completely evaluate the sequence, using the given parameter 
        values, or the default values, in that order of preference.
        
        A `RawSequence` object is returned.
        """
        new_params = self.params.copy()
        new_params.update(kw_params)
        if None in new_params.items():
            bad_params = [k for k, v in new_params.items() if v is None]
            raise ValueError('The following parameters do not have default values and need to be specified:\n%s'%bad_params)

        # Create a copy for the new sequences, note this is a shallow copy,
        # the references to the sequence lists is probably being re-used.
        new_sequence = self.flag_seqs.copy()
        for k, seq in self.flag_seqs.items():
            if seq is None:
                continue
            new_sequence[k] = seq.copy()
            for i, value in enumerate(seq):
                if value in new_params:
                    val = new_params[value]
                    new_sequence[k][i] = extract_ns(val)

        ret = RawSequence(self.controller, save_refs=self.save_refs) 
        ret.flag_seqs = new_sequence
        return ret

    def evaluate_params(self, *params, **kw_params):
        """ Evaluate the given parameters using the default values,
        or a value given here. eg,

        >>> absq.evaluate_params('tau', on_time=1e2)

        Will evaluate the sequence setting 'tau' to its default parameter
        and 'on_time' to 100.
        If 'tau' in this example doesn't have default value, a ValueError will be
        raised.

        Units can be specified, if not then nanoseconds is assumed.

        Returns a new `AbstractSequence`.
        """
        # temp_params = self.params.copy()
        # temp_params.update(**kw_params)
        bad_params = []

        for p in params:
            if p in self.params:
                kw_params[p] = self.params[p]
            if kw_params.get(p, None) is None:
                bad_params.append(p)
            
        if bad_params:
            raise ValueError(f"The following parameters require a value to be set for them: {bad_params}")

        new_sequence = self.flag_seqs.copy()

        for k, seq in self.flag_seqs.items():
            if seq is None:
                continue
            for i, value in enumerate(seq):
                new_sequence[k] = seq.copy()
                if value in kw_params:
                    val = kw_params[value]
                    new_sequence[k][i] = extract_ns(val)
        ret = AbstractSequence(self.controller, save_refs=self.save_refs)
        ret.flag_seqs = new_sequence
        return ret

    def plot_sequence(self, *params, **kw_params):
        raw_seq = self.eval(**kw_params)
        raw_seq.plot_sequence()
    
# class LoopSequence(PulseSequence):

def flags_to_number(flags):
    """ Convert an array of flags to a number,
    assumes the array has only FLAG_OFF's and FLAG_ON's, and that
    the left (0th) element is the least significant.
    """
    # TODO: Could change this to be a vector-able function?
    l = len(flags)
    a = np.arange(l)
    twos = 2**a
    return np.int32(sum(twos * (flags == FLAG_ON).astype(int)))


def merge_flag_seqs(sequences, relative_times=True):
    """ Merge sequences for individual flags to create a sequence
    of instructions to be used for the pulse blaster.

    All flags start as FLAG_OFF. If you want a flag to be turned on immediately,
    set the first time delta in its sequence to 0. 0-length time frames will
    be removed from the end result.

    By default assumes that times are relative to the previous time value,
    ie [1., 2., 3.] lasts for 6 seconds.
    
    If you have provided the absolute times, 
    where [1., 2., 3.] would be a 3 second sequence,
    then set `relative_times` to `False`.

    If some sequences are longer than others, all
    sequences will be padded with `FLAG_OFF`.


    sequences: list of corresponding times to toggle flags.
    eg;
    
        >>> t, frames = merge_flag_seqs([[0.1, 0.3], [0.3, 0.2]])
        >>> t
        [0.1, 0.2, 0.1, 0.1]
        >>> frames
        [[0, 0], [1, 0], [1, 1], [0, 1]]
    """        
    # Perform cum sum if needed:
    if relative_times:
        sequences = [np.cumsum(sequence) for sequence in sequences]
    # Try pre-emptively remove zero length frames:
    for i, seq in enumerate(sequences):
        # Mask of which values to keep
        fin_mask = np.ones(len(seq), dtype=np.bool8)
        # If two adjacent values are equal then remove both
        skip_flag = False
        for k, t in enumerate(seq[:-1]):
            if skip_flag:
                # Skip the second of two consecutive values
                # This is important because a third consecutive value 
                # should not be removed (ie only even quantities should be removed)
                skip_flag = False
                continue
            if t == seq[k+1]:
                fin_mask[k] = False
                fin_mask[k+1] = False
                skip_flag = True
                
        sequences[i] = seq[fin_mask]

    # Make sure sequences is an array
    flat_seqs = np.unique(np.concatenate(sequences))
    # Sort time steps
    t_all = np.sort(flat_seqs)
    frames = []
    toggles_full = ([(FLAG_ON if i%2 else FLAG_OFF) for i in range(len(t_all))])
    for seq in sequences:
        if len(seq) == 0:
            frames.append(np.full(t_all.shape, FLAG_OFF))
            continue
        toggles = toggles_full[:len(seq)]
        interp = interpolate.interp1d(
            seq, toggles, kind="next", 
            fill_value=(FLAG_OFF, FLAG_OFF),
            bounds_error=False
        )
        frame = interp(t_all)
        frames.append(frame)

    frames = np.array(frames)
    if relative_times:
        t_all = np.diff(t_all, prepend=0)
        nonz_ts = t_all != 0
        frames = frames[:, nonz_ts]
        t_all = t_all[nonz_ts]
    else:
        print("pulse_utils.merge_flag_seqs(): Warning: "
              "I haven't checked behaviour for relative_times=False")
    return t_all, frames.T
        
if __name__ == "__main__":
    print("Hello there")
