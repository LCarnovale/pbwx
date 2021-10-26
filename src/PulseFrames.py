import numpy as np
from src.extras import parse_val
from src.pulse_instance import PulseManager
import tkinter as tk
import tkinter.ttk as ttk
from datetime import date
from . import Boxes
_PSF_instance = None
WIDTH = 1 # Will be set from main.py
HEIGHT = 1

PARAM_SAVE_FOLDER = "./saved_params/"
class PulseShapeFrame(ttk.Frame):
    def __init__(self, parent, **kwargs):
        global _PSF_instance
        super(PulseShapeFrame, self).__init__(parent, **kwargs)
        self.to_remove = []
        _PSF_instance = self
        PulseManager.register(self)
        self.init_UI()

    def notify(self, event=None, data=None):
        if event == PulseManager.Event.PULSE:
            pulse_obj = PulseManager.get_pulse()
            self.init_pulse_shapes(pulse_obj)

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
class RepetitionsFrame(tk.LabelFrame):
    def __init__(self, main_app, parent, **kwargs):
        global _RF_instance
        super(RepetitionsFrame, self).__init__(parent, **kwargs)
        self.main = main_app
        self.to_remove = []
        self.reps_num = tk.StringVar(self, "1")
        self.progression_type = tk.StringVar(self, "LIN") # LIN or LOG
        self.end_vars = {}
        self.start_vars = {}
        self.init_UI()
        PulseManager.register(self)
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
        self.prog_button = prog_button
        prog_button.grid(row=2, column=1, sticky=tk.W+tk.E)
        plot_button = tk.Button(rep_options, text="Plot",
            command=self.plot_sequence)
        plot_button.grid(row=3, column=1, sticky=tk.W+tk.E)
        prog_start_btn = tk.Button(rep_options, text="Prog and Start",
            command=self.prog_and_start)
        prog_start_btn.grid(row=4, column=1, sticky=tk.W+tk.E)

        reps_lin_radio.grid(row=1, column=1, sticky=tk.W)
        reps_log_radio.grid(row=1, column=2, sticky=tk.W)
        pane.add(param_list, stretch="always", width=WIDTH//2)
        pane.add(rep_options, stretch="always", width=WIDTH//2)
        self.param_list = param_list
        self.init_param_list()
        rep_options.grid_rowconfigure(5, minsize=20)
        row_n = 6

        # Save params controls
        self.exp_num_var = tk.StringVar(rep_options, "1")
        exp_number = tk.Spinbox(rep_options, textvariable=self.exp_num_var, 
            from_=1, to=999, increment=1)
        exp_number.grid(row=row_n, column=1, sticky=tk.W+tk.E)
        tk.Label(rep_options, text="Experiment number:").grid(row=row_n, column=0)
        
        save_btn = tk.Button(rep_options, text="Save Params", command=self.save_params)
        save_btn.grid(row=row_n+1, column=1, sticky=tk.W+tk.E)
        # Save pulse
        save_pls_btn = tk.Button(rep_options, text="Save Pulse", command=self.save_pulse)
        save_pls_btn.grid(row=row_n+2, column=1, sticky=tk.W+tk.E)




    def save_params(self, *args):
        n = self.exp_num_var.get()
        self.exp_num_var.set(str(int(n) + 1))
        
        today = date.today()
        f_name = f"{today}-{n}_params.txt"
        f_name = PARAM_SAVE_FOLDER + f_name

        # Get parameters
        pulse_obj = PulseManager.get_pulse()
        start_vars = pulse_obj.params

        end_vars = self.end_vars
        n_reps = int(self.reps_num.get())

        rep_mode = self.progression_type.get()
        body = f"Sequence: {PulseManager.pulse_name}"
        body += "\n----"
        body += "\n".join([f"{var}: {start_vars[var]} -> {end_vars[var]}" for (var) in start_vars if var in end_vars])
        body += "\n----"
        body += "\n" + "n_reps: " + str(n_reps)
        body += "\n" + "progression: " + str(rep_mode)

        try:
            with open(f_name, "w") as f:
                f.write(body)
        except IOError as e:
            print("Failed to sve parameters: " + str(e))
            self.main.indicate_error()
        else:
            pass

    def save_pulse(self, *args):
        n = self.exp_num_var.get()
        
        today = date.today()
        f_name = f"{today}-{n}_pulse.txt"
        f_name = PARAM_SAVE_FOLDER + f_name

        # Get pulse
        pulse = self.eval_pulse()
        try:
            pulse.save_txt(f_name)
        except IOError as e:
            print("Failed to save pulse: " + str(e))
            self.main.indicate_error()
        except Exception as e:
            print("Error: " + str(e))
            self.main.indicate_error()
        else:
            pass


    def notify(self, event=None, data=None):
        if event == PulseManager.Event.PULSE:
            pulse_obj = PulseManager.get_pulse()
            self.init_param_list(pulse_obj)
        if event == PulseManager.Event.START:
            self.prog_button.config(state=tk.DISABLED)
        if event == PulseManager.Event.STOP:
            self.prog_button.config(state=tk.ACTIVE)
        
    def init_param_list(self, pulse_obj=None):
        for e in self.to_remove:
            e.grid_forget()
        if pulse_obj is None:
            tb = tk.Label(self.param_list, text="Select a pulse file")
            tb.grid(row=0, column=0, sticky=tk.W+tk.E)
            self.to_remove = [tb]
        else:
            self.end_vars = {k:None for k in pulse_obj.c_params.keys()}
            try:
                rep_params = pulse_obj.rep_params
            except:
                rep_params = []
            param_list = [x for x in self.end_vars.items() if x[0] not in rep_params]
            param_vars = {k+"_reps":tk.StringVar(name=k+"_reps", value="const")
                for k, v in param_list}
            start_vars = {k:PulseManager.get_var(k) for k, _ in param_list}
            def _update_param(param_key, params, param_vars):
                # params, param_vars, lbl_vars = dicts
                new_value = param_vars[param_key].get()
                try:
                    if new_value == "":
                        new_value = "const"
                    else:
                        new_value = parse_val(new_value, out_as="ns", rounding=True, out_type=int)
                except:
                    pass
                else:
                    # lbl_vars[param_key].set(str(new_value))
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
                var.trace_add("write", (lambda name, *args: _update_param(name, self.end_vars, param_vars)))
                # else:
                #     pass
                #     print(var, "already has a trace")
                # Create row
                ## Parameter label
                lbl = tk.Label(self.param_list, text=k)
                lbl.grid(row=row+n, column=0, sticky=tk.W+tk.E)
                ## Start entry
                set_lbl = tk.Entry(self.param_list, text=var.get(), textvariable=start_vars[k])
                set_lbl.grid(row=row+n, column=1, sticky=tk.W+tk.E)
                ## End entry
                box = tk.Entry(self.param_list, text=v, 
                    validate="focusout", textvariable=var)
                box.grid(row=row+n, column=2, sticky=tk.W+tk.E)
                self.to_remove.append(lbl)
                self.to_remove.append(box)
                self.to_remove.append(set_lbl)
    def program_seq(self):
        # End values are in self.end_vars
        # If any are less than the original, that one is constant
        # Boxes.SetParameterFrame.program_pulse_reps(
        #     n_reps=int(self.reps_num.get()), 
        original = PulseManager.get_pulse()
        pulse = self.eval_pulse()
        try:
            PulseManager.set_pulse(pulse, notify=False)
            PulseManager.program(stopping=True)
            # Restore previous pulse
            PulseManager.set_pulse(original, notify=False)
        except Exception as e:
            self.main.indicate_error()
            raise e

    def prog_and_start(self, *args):
        self.program_seq()
        try:
            PulseManager.start()
        except Exception as e:
            self.main.indicate_error()
            raise e

    def eval_pulse(self):
        pulse_obj = PulseManager.get_pulse()
        try:
            rep_params = pulse_obj.rep_params
            # print(rep_params)
            rep_params[0]
        except:
            raise Exception("This sequence does not support repititions")
            # print("This sequence does not support repititions.")
            # return
        else:
            if len(rep_params) > 1:
                raise Exception("This sequence has too many outer repetition variables, there can only be 1.")
                # return
            else:
                rep_key = rep_params[0]
        start_vars = pulse_obj.params
        these_params = start_vars.copy()

        end_vars = self.end_vars
        n_reps = int(self.reps_num.get())
        these_params[rep_key] = n_reps

        rep_mode = self.progression_type.get()
        print("start:", these_params)
        print("end:", end_vars)
        print("Num reps:", n_reps)

        if rep_mode == 'LIN':
            axis_f = np.linspace
        else:
            axis_f = lambda start, stop, *args, **kwargs: np.logspace(*np.log10([start, stop]), *args, **kwargs)

        for key in end_vars:
            if key not in these_params: continue
            if end_vars[key] == 0: continue
            if end_vars[key] is None: continue
            if end_vars[key] != these_params[key]:
                try:
                    print("Making axis for:", key)
                    axis = axis_f(these_params[key], end_vars[key], n_reps, dtype=int)
                except:
                    print("Unable to create axis for %s" % key)
                    continue
                else:
                    these_params[key] = axis

        pulse = pulse_obj.eval(**these_params)
        return pulse

    def plot_sequence(self):
        pulse = self.eval_pulse()
        print(f"Pulse length: {pulse.length_ns/1e6:.2} ms / {pulse.inst_count} instructions")
        pulse.plot_sequence()
        
