import tkinter as tk
import tkinter.ttk as ttk
from . import Boxes
_PSF_instance = None
class PulseShapeFrame(ttk.Frame):
    def __init__(self, parent, **kwargs):
        global _PSF_instance
        super(PulseShapeFrame, self).__init__(parent, **kwargs)
        self.to_remove = []
        _PSF_instance = self
        self.init_UI()

    @staticmethod
    def send_pulse_object(pulse_obj=None):
        _PSF_instance.init_pulse_shapes(pulse_obj)

    def init_UI(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=10)
        self.init_pulse_shapes()

    def init_pulse_shapes(self, pulse_obj=None):
        for e in self.to_remove:
            e.grid_forget()
        if pulse_obj is None:
            lbl = tk.Label(self, text="Select a pulse file")
            lbl.grid(row=0, column=0, sticky=tk.W+tk.E)
            self.to_remove = [lbl]
        else:
            lbl1 = tk.Label(self, text="Pin")
            lbl2 = tk.Label(self, text="Pulse Shape")
            lbl1.grid(row=0, column=0, sticky=tk.W+tk.E)
            lbl2.grid(row=0, column=1, sticky=tk.W+tk.E)
            self.to_remove = [lbl1, lbl2]


        
_RF_instance = None
class RepetitionsFrame(ttk.Frame):
    def __init__(self, parent, **kwargs):
        global _RF_instance
        super(RepetitionsFrame, self).__init__(parent, **kwargs)
        self.to_remove = []
        self.reps_num = tk.StringVar(self, "1")
        self.progression_type = tk.StringVar(self, "LIN") # LIN or LOG
        self.end_vars = {}
        self.start_vars = {}
        self.init_UI()
        _RF_instance = self

    def init_UI(self):
        # Parameter list | Repition options
        pane = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True)

        param_list = tk.Frame(pane)
        # param_list.grid(row=0, column=0, sticky=tk.W+tk.E)
        param_list.grid_columnconfigure(0, weight=1)
        param_list.grid_columnconfigure(1, weight=1)
        param_list.grid_columnconfigure(2, weight=1)
        rep_options = tk.Frame(pane)
        # rep_options.grid(row=0, column=0, sticky=tk.W+tk.E)
        rep_options.grid_columnconfigure(0, weight=2)
        rep_options.grid_columnconfigure(1, weight=1)
        rep_options.grid_columnconfigure(2, weight=1)
        # param_list.pack(fill=tk.BOTH, expand=True)
        # rep_options.pack(fill=tk.BOTH, expand=True)
        num_reps_lbl = tk.Label(rep_options, text="Number of Repitions")
        num_reps_lbl.grid(row=0, column=0, sticky=tk.E)
        num_reps_box = tk.Entry(rep_options, text=1, 
            textvariable=self.reps_num)
        num_reps_box.grid(row=0, column=1, columnspan=2, sticky=tk.W+tk.E)
        reps_type_lbl = tk.Label(rep_options, text="Progression mode:")
        reps_type_lbl.grid(row=1, column=0, sticky=tk.E)
        reps_lin_radio = tk.Radiobutton(rep_options, text="Linear", value="LIN", 
            variable=self.progression_type)
        reps_log_radio = tk.Radiobutton(rep_options, text="Log", value="LOG", 
            variable=self.progression_type)

        prog_button = tk.Button(rep_options, text="Program",
            command=self.program_seq)
        prog_button.grid(row=2, column=1, sticky=tk.W+tk.E)
        reps_lin_radio.grid(row=1, column=1, sticky=tk.W)
        reps_log_radio.grid(row=1, column=2, sticky=tk.W)
        label1 = tk.Label(param_list, text="Parameter list")
        label1.grid(row=0, column=0, sticky=tk.W)
        pane.add(param_list, stretch="always")
        pane.add(rep_options, stretch="always")
        self.param_list = param_list
        self.init_param_list()

        # options = tk.Frame(pane, background="green")
        # label2 = tk.Label(options, text="Repition Options")
        # label2.grid(row=0, column=0, sticky=tk.E)
        # pane.add(options, stretch="always")
        # options.pack(fill=tk.BOTH, expand=True)
        # self.options_pane = options


    @staticmethod
    def send_pulse_object(pulse_obj=None):
        _RF_instance.init_param_list(pulse_obj)
        
    def init_param_list(self, pulse_obj=None):
        for e in self.to_remove:
            e.grid_forget()
        if pulse_obj is None:
            tb = tk.Label(self.param_list, text="Select a pulse file")
            tb.grid(row=0, column=0, sticky=tk.W+tk.E)
            self.to_remove = [tb]
        else:
            self.end_vars = pulse_obj.params.copy()
            param_list = list(self.end_vars.items())
            param_vars = {k+"_reps":tk.StringVar(name=k+"_reps", value=str((int(v) if v is not None else 0)))
                for k, v in param_list}
            # TODO: I don't think lbl_vars is actually needed here?
            lbl_vars = {k+"_reps":tk.StringVar(name=k+"_reps_lbl", value=str((int(v) if v is not None else 0)))
                for k, v in param_list}
            def _update_param(param_key, params, param_vars, lbl_vars):
                # params, param_vars, lbl_vars = dicts
                new_value = param_vars[param_key].get()
                print("updating", param_key)
                try:
                    new_value = float(new_value)
                except:
                    pass
                else:
                    lbl_vars[param_key].set(str(new_value))
                    # :-5 to remove the '_reps' tag at the end of each name
                    self.end_vars[param_key[:-5]] = new_value

            # self.param_vals.update(**params)
            n = 1 # Starting row
            self.to_remove = []
            for i, l in enumerate(["Parameter", "Start", "End"]):
                lbl = tk.Label(self.param_list, text=l)
                lbl.grid(row=0, column=i)
                self.to_remove.append(lbl)
                
            for row, (k, v) in enumerate(param_list):
                # Create variable
                var = param_vars[k+"_reps"]
                # Bind variable to row
                # if len(var.trace_info()) == 0:
                    # If the same pulse sequence is loaded again the 
                    # same variable and trace will be loaded, don't add another
                    # trace to it. 
                var.trace_add("write", (lambda name, *args: _update_param(name, self.end_vars, param_vars, lbl_vars)))
                # else:
                #     pass
                #     print(var, "already has a trace")
                # Create row
                lbl = tk.Label(self.param_list, text=k)
                lbl.grid(row=row+n, column=0, sticky=tk.W+tk.E)
                box = tk.Entry(self.param_list, text=v, 
                    validate="focusout", textvariable=var)
                box.grid(row=row+n, column=2, sticky=tk.W+tk.E)
                set_lbl = tk.Label(self.param_list, text=var.get(), textvariable=tk.StringVar(name=k+"_lbl"))
                set_lbl.grid(row=row+n, column=1, sticky=tk.W+tk.E)
                self.to_remove.append(lbl)
                self.to_remove.append(box)
                self.to_remove.append(set_lbl)
    def program_seq(self):
        # End values are in self.end_vars
        # If any are less than the original, that one is constant

        Boxes.SetParameterFrame.program_pulse_reps(
            n_reps=int(self.reps_num.get()), end_vars=self.end_vars)
