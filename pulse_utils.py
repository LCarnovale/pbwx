import threading
import numpy as np
from astropy import units as u
import matplotlib.pyplot as plt
from scipy import interpolate
import _actions as actions

from spinapi import *
# try:
# except ImportError:
#     raise Exception()
#     try:
#         from pbwx.spinapi import *
#     except ImportError as e:
#         e.msg = "Unable to find spinapi module in " \
#                 "pbwx package or local directory."
#         raise e
        
    

SAFE_MODE = True
if SAFE_MODE:
    print("SAFE_MODE is enabled, the board will not be programmed.")

# # Configure the core clock
# pb_core_clock(500)

MIN_TIME = 5*ns

all_bits = 0xFFFFFF
TRIG = (1 << 7) # Trigger for oscilloscope
AOM  = (1 << 6) # RF source for AOM

FLAG_ON  = 1
FLAG_OFF = 0

def init_board():

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
        """ Program the sequence into the board and begin running the sequence. """
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

    def add_instruction(self, flags:np.int32, inst:Inst, inst_data:np.int32, length:np.float64):
        check_board_init()
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
        # self.inst_seq.append(inst)
        print(f"[{flags:b}]", *inst[1:])
        # print([type(x) for x in inst])
        if not SAFE_MODE:
            return pb_inst_pbonly(*inst)
        else:
            return 0

class EmptyController:
    def __init__(self):
        pass

    def __call__(self):
        raise Exception("Controller for this pulse sequence has not yet been set.")

    def __getattribute__(self, name: str):
        self()

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

        Alternatively, set `cycle=True` to make the sequence branch back
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





class RawSequence(PulseSequence):
    def __init__(self, *args, **kwargs):
        super(RawSequence, self).__init__(*args, **kwargs)
        self.flag_seqs = { n:None for n in range(self.n_bits) }

    def add_seq(self, flags, sequences, t_rel=True):
        """ Add flag toggle times for a given flag.
        For example to turn flag 10 on at 1 second,
        then off at 2 seconds, give:
        ``
            ps.add_seq([10, ...], [[1, 2], ...])
        ``
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

        for flag, seq in zip(flags, sequences):
            current = self.flag_seqs[flag]
            if np.any(current):
                self.flag_seqs[flag] = np.concatenate([current, current[-1]*t_rel + seq])
            else:
                self.flag_seqs[flag] = seq
    
    def program_seq(self, end_action=None):
        """ Program the Pulse Blaster board with the defined sequences.
        """
        t_ax, frames = self._merge_sequences()
        pin_sets = [flags_to_number(f) for f in frames]
        # t_lens = (t_ax[1:] - t_ax[:-1])
        t_lens = t_ax
        self._controller.prog_enter()

        err = 0
        try:
            # TODO: Loops? Jumps?
            # Add the starting frame
            start = self.controller.add_instruction(
                pin_sets[0], Inst.CONTINUE, 0, t_lens[0]
            )
            # Add the other frames
            for p, dt in zip(pin_sets[1:-1], t_lens[1:-1]):
                self.controller.add_instruction(
                    p, Inst.CONTINUE, 0, dt
                )
            # Add the final frame, which branches back to the beginning
            self.controller.add_instruction(
                pin_sets[-1], Inst.BRANCH, start, t_lens[-1]
            )
        except Exception as e:
            err = 1
            raise e
        finally:
            if err:
                print("Aborting programming, exiting programming mode.")
            else:
                print("Programming completed successfully.")
            self.controller.prog_exit()

    def plot_sequence(self):
        t_ax, frames = self._merge_sequences()
        nonz_flags = np.array([k for k, v in self.flag_seqs.items() if v is not None])
        t_ax = t_ax.cumsum()
        if t_ax[0] != 0:
            t_ax = np.concatenate([[0], t_ax])
            frames = np.concatenate([frames[[0]], frames[:]], axis=0)
        flag_nums = np.arange(frames.shape[1])
        frames = frames[:,nonz_flags]
        flag_nums = flag_nums[nonz_flags]
        plot_shifts = np.arange(len(nonz_flags))
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

class AbstractSequence(RawSequence):
    """ A sequence which can be represented using parameters, 
    which can be assigned at the last minute before being executed,
    and remain undetermined until then. """
    def __init__(self, *args, **kwargs):
        super(AbstractSequence, self).__init__(*args, **kwargs)
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
            try:
                val.unit
                params[k] = val / u.ns + 0
            except:
                pass
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

    def program_seq(self, end_action=actions.CTN, **params):
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
        temp_params = self.params.copy()
        temp_params.update(**params)
        if None in temp_params.values():
            # Find missing params
            missing = []
            for p, v in temp_params.items():
                if v == None:
                    missing.append(p)

            raise ValueError("Values must be provided for: %s" % missing)

        # Create copy of original parameters
        original_seqs = {
            k:(seq.copy() if seq is not None else None) for k, seq in self.flag_seqs.items()
        }
        # Substitute params
        for k, seq in self.flag_seqs.items():
            if seq is None: continue
            for i, v in enumerate(seq):
                if v in temp_params:
                    seq[i] = temp_params[v]

        # Program
        super(AbstractSequence, self).program_seq()

        # Return original sequence
        self.flag_seqs = original_seqs

    def evaluate_params(self, *params, **kw_params):
        """ Evaluate the given parameters using the default values,
        or a value given here. eg,

        >>> absq.evaluate_params('tau', on_time=10.2)

        Will evaluate the sequence setting 'tau' to its default parameter
        and 'on_time' to 10.2.
        If 'tau' in this example doesn't have default value, a ValueError will be
        raised.
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

        for k, seq in self.flag_seqs.items():
            if seq is None:
                continue
            for i, value in enumerate(seq):
                if value in kw_params:
                    seq[i] = kw_params[value]



    
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
        print("pulse_utils.merge_flag_seqs: Warning: "
              "I haven't checked behaviour for relative_times=False")
    return t_all, frames.T
        
if __name__ == "__main__":
    print("Hello")
