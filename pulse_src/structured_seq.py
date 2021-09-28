from src.pulse_instance import PulseManager
from .pulse_utils import RawSequence, AbstractSequence, SequenceProgram
import re

def parse_complex_structure(children_list, structure):
    """ For parsing structures such as:
        structure="0, 1, (2, (0, 1)^M)^N, 3"
    """
    parts = re.split(r"\([\d\s\w\^,]*?\)", structure, maxsplit=1)
    if len(parts) == 1:
        # No more subparts
        return StructuredSequence(*children_list, structure=structure)
    else:
        A, B = parts
        An, Bn = len(A), len(B)
        sub_str = structure[An+1:-(Bn+1)]
        new_child = parse_complex_structure(children_list, sub_str)
        new_n = len(children_list)
        new_struct = A + str(new_n) + B
        return parse_complex_structure(children_list + [new_child], new_struct)



class StructuredSequence:
    def __init__(self, *children, controller:SequenceProgram=None, structure:str=None):
        """ If `structure` is not speicified, it is assumed to be each child
        one after the other, in the given order. 
        A structure can be specified as a string, such as:
            >>> A = RawSequence(...)
            >>> B = AbstractSequence(...)
            >>> M = StructuredSequence(A, B, structure="0,1^N,0")
        This will create a structured sequence where the order will be
        A, followed by B repeated N times, followed by A.
        N will be a parameter that can be evaluated at runtime with:
            >>> M.eval(N=5)
        Parameters in the child sequences can also be specified in the above call.

        Evaluation is recursive, so children sequences can also be `StructuredSequence`'s.

        The set of children can not be changed, it would be easier to create a new 
        structured sequence.

        Parameters for repetitions are stored under `rep_params`:
            >>> M.rep_params
            ['N']
        Parameters can be introduced with a new structure string:
            >>> M.parse_structure("0, 1^N, 0^M")
        Or using the property setter:
            >>> M.structure = "0, 1^N, 0^M" 
        This will set the first child to have 'M' repititions after 'N' reps of the second child. 
        Integers can also be used here to 
        set a fixed number of repetitions. Note that when parameters
        like these are being used, then a call to eval must specify the value of each.
        """
        self.children = children
        self.controller = controller
        self.parse_structure(structure)

    def parse_structure(self, structure):
        """
        Given a new structure string, interpret and apply this structure to the sequence.
        Indexes must match the order of the children supplied to the constructor.
            >>> M.parse_structure("0, 1^N, 0^M")
        Or using the structure setter:
            >>> M.structure = "0, 1^N, 0^M" 
        Will set the first child to have 'M' repititions after 'N' reps of the second child. 
        Integers can also be used here to 
        set a fixed number of repetitions. Note that when parameters
        like these are being used, then a call to eval must specify the value of each.
        """
        self.rep_params = []
        if structure is None:
            self._struct_order = list(range(len(self.children)))
            self._reps = [1 for _ in self.children]
            return
        terms = structure.split(',')
        self._reps = []
        self._struct_order = []
        for t in terms:
            t = t.strip()
            if "^" in t:
                # This is a repeated term
                idx, reps = t.split("^")
                idx = int(idx)
                try: 
                    reps = int(reps)
                except:
                    # Add the new parameter
                    self.rep_params.append(reps)
            else:
                idx = int(t)
                reps = 1
            try:
                self.children[idx]
            except:
                raise IndexError("Values in structure string must be valid indices, %d is invalid" % idx)
            self._reps.append(reps)
            self._struct_order.append(idx)
        self._structure = structure

    @property
    def structure(self):
        return self._structure

    @structure.setter
    def structure(self, struct:str):
        self.parse_structure(struct)

    @property
    def params(self):
        params = {k:None for k in self.rep_params}
        params.update(self.c_params)
        # for c in self.children:
        #     try:
        #         params.update(c.params)
        #     except AttributeError:
        #         pass
        return params

    @property
    def c_params(self):
        """ Parameters only of the children. No repetition parameters included."""
        params = {}
        for c in self.children:
            try:
                params.update(c.params)
            except AttributeError:
                pass
        return params



    def eval(self, **kw_params) -> RawSequence:
        total = None
        # Check for lists
        list_params = {}
        for k, v in kw_params.items():
            try:
                v[0]
            except:
                continue
            else:
                list_params[k] = v
                kw_params[k] = v[0]
        for idx, reps in zip(self._struct_order, self._reps):
            # Get the relevant child.
            child = self.children[idx]
            if not list_params:
                c = child.eval(**kw_params)
            
            if type(reps) is str:
                try:
                    reps = int(kw_params[reps])
                except KeyError:
                    raise ValueError("Value for repetitions parameter %s must be supplied." % reps)
            for i in range(reps):
                if list_params:
                    new_kw = kw_params.copy()
                    new_kw.update({k:v[i] for k, v in list_params.items()})
                    c = child.eval(**new_kw)
                total = total + c
        return total

    def set_controller(self, controller):
        self.controller = controller
        for c in self.children:
            c.set_controller(controller)

    def set_param_default(self, **kw_params):
        for c in self.children:
            c.set_param_default(**kw_params)


    def plot_sequence(self, **kw_params):
        seq = self.eval(**kw_params)
        seq.plot_sequence()

    def start(self):
        self.controller.run()

    def stop(self):
        self.controller.stop()

if __name__ == "__main__":
    A = StructuredSequence(1, 2, 3, structure="0, 1^N, 0^M, 2")
