import threading

from spinapi import *
import numpy as np

SAFE_MODE = False

# # Configure the core clock
# pb_core_clock(500)

MIN_TIME = 5*ns

all_bits = 0xFFFFFF
TRIG = (1 << 7) # Trigger for oscilloscope
AOM  = (1 << 6) # RF source for AOM

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
            raise Exception("Another thread has the board in programming mode.")
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
        inst = (
            ctypes.c_int(flags), 
            ctypes.c_int(inst), 
            ctypes.c_int(inst_data), 
            (length)
        )
        # self.inst_seq.append(inst)
        print(inst)
        # print([type(x) for x in inst])
        if not SAFE_MODE:
            return pb_inst_pbonly(*inst)
        else:
            return 0


class PulseSequence:
    def __init__(self, controller, pre_delay=0, post_delay=0, loop=0, cycle=False):
        """ Create a Pulse Sequence object. 

        `controller` must be a SequenceProgram object, to allow communication to the board.

        Set `loop=0` for no looping, otherwise give the number of times
        this sequence should be repeated.

        Alternatively, set `cycle=True` to make the sequence branch back
        to the beginning, making an infinite loop.
        """
        self.controller = controller
        self.n_bits = 24
        self.pre_delay = pre_delay
        self.post_delay = post_delay
        self.loop = loop
        # self.end_time = 0
        self.sequence = []
        # self.start_addr = 0

    def add_raw(self, raw_seq):
        if type(raw_seq) is not RawSequence:
            raise TypeError("raw_seq must be a RawSequence object.")

        # # Create frames
        # t_ax, frames = raw_seq._merge_sequences()
        self.sequence.append(raw_seq)


        
        


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
    
    def program_seq(self):
        """ Program the Pulse Blaster board with the defined sequences.
        """
        t_ax, frames = self._merge_sequences()
        pins = [flags_to_number(f) for f in frames]
        if (self.post_delay < MIN_TIME):
            raise Exception("""Warning: The duration of the final frame is determined by
the value of self.post_delay, this must not be less than MIN_TIME.
Programming aborted.""")
        t_lens = (t_ax[1:] - t_ax[:-1])
        self.controller.prog_enter()

        err = 0
        try:
        # TODO: Loops? Jumps?
        # Add the starting frame
            if self.pre_delay > MIN_TIME:
                start = self.controller.add_instruction(
                    0x0, Inst.CONTINUE, 0, self.pre_delay
                )
            else:
                start = self.controller.add_instruction(
                    pins[0], Inst.CONTINUE, 0, t_lens[0]
                )
            # Add the other frames
            for p, dt in zip(pins[1:-1], t_lens[1:]):
                self.controller.add_instruction(
                    p, Inst.CONTINUE, 0, dt
                )
            # Add the final frame, which branches back to the beginning
            self.controller.add_instruction(
                pins[-1], Inst.BRANCH, start, self.post_delay
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

        

    def _merge_sequences(self):
        """ Merge the current sequences to create flag frames,
        intended to be used by the PulseSequence class. 
        """

        flag_seqs = []
        for f in range(self.n_bits):
            seq = self.flag_seqs[f]
            if seq is not None:
                flag_seqs.append(seq)
            else:
                flag_seqs.append([])
        
        t_ax, frames = merge_flag_seqs(flag_seqs)
        return t_ax, frames

    
    

# class LoopSequence(PulseSequence):

def flags_to_number(flags):
    """ Convert an array of flags to a number,
    assumes the array has only 0's and 1's, and that
    the left (0th) element is the least significant.
    """
    # TODO: Could change this to be a vector-able function?
    l = len(flags)
    a = np.arange(l)
    twos = 2**a
    return np.int32(sum(twos * flags))


def merge_flag_seqs(sequences):
    """ Merge sequences for individual flags to create a sequence
    of instructions to be used for the pulse blaster.

    sequences: list of corresponding times to toggle flags.
    eg;
    
        >>> t, frames = merge_flag_seqs([[0.1, 0.4], [0.3, 0.5]])
        >>> t
        [0.1, 0.3, 0.4, 0.5]
        >>> frames
        [[1, 0], [1, 1], [0, 1], [0, 0]]
    """
    # Make sure sequences is an array
    flat_seqs = np.unique(np.concatenate(sequences))
    # Sort time steps
    t_all = np.sort(flat_seqs)
    # Go through each time step and determine if each flag is on or off.
    frames = []
    for t in t_all:
        frame = []
        for flag in range(len(sequences)):
            seq = sequences[flag]
            toggles = len(np.flatnonzero(seq <= t))
            if toggles % 2 == 0:
                # The flag is off
                frame.append(0)
            else:
                # The flag is on
                frame.append(1)
        frames.append(frame)

    t_list = t_all.tolist()
    # Remove duplicates
    prev = None
    for i, f in enumerate(frames[-1::-1]):
        if prev == f:
            frames.pop(-i-1)
            t_list.pop(-i-1)
        else:
            prev = f
    frames = np.array(frames)
    t_all = np.array(t_list)
    return t_all, frames
