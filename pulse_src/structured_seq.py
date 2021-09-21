from .pulse_utils import RawSequence, AbstractSequence

class StructuredSequence:
    def __init__(self, *children, structure:str=None):
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
        for c in self.children:
            try:
                params.update(c.params)
            except AttributeError:
                pass
        return params


    def eval(self, **kw_params) -> RawSequence:
        total = None
        for idx, reps in zip(self._struct_order, self._reps):
            # Get the relevant child.
            c = self.children[idx]
            c = c.eval(**kw_params)
            
            if type(reps) is str:
                try:
                    reps = int(kw_params[reps])
                except KeyError:
                    raise ValueError("Value for repetitions parameter %s must be supplied." % reps)
            for i in range(reps):
                total = total + c
        return total

    def plot_sequence(self, **kw_params):
        seq = self.eval(**kw_params)
        seq.plot_sequence()

if __name__ == "__main__":
    A = StructuredSequence(1, 2, 3, structure="0, 1^N, 0^M, 2")
