import os
import tkinter as tk
import tkinter.ttk as ttk

from pulse_src import load_pulse as loader

from src.extras import parse_val

from .pulse_instance import PulseManager
from .PulseFrames import RepetitionsFrame

_SelPF_instance = None
class SelectPulseFrame(tk.LabelFrame):
    def __init__(self, main_app, parent, root_folder, controller, *args, **kwargs):
        """ Provide a parent object and a path in `root_folder` 
        for the folder to look for `.pls` files
        """
        global _SelPF_instance
        super(SelectPulseFrame, self).__init__(parent, *args, text='Select Pulse Sequence', **kwargs)
        self.root_folder = root_folder
        self.main = main_app
        self.parent = parent
        self.selected_file = tk.StringVar(self)
        self.selected_file.trace_add("write", self.load_pulse)
        self.pls_controller = controller
        # self.seq = pulse_sequence

        self.init_UI()
        _SelPF_instance = self
        
    def init_UI(self):
        pulse_list = os.listdir(self.root_folder)
        cb = ttk.Combobox(self, values=pulse_list, state="readonly", 
            textvariable=self.selected_file)
        browse_btn = tk.Button(self, text="Browse", width=8,
            command=lambda:print(self.selected_file.get()))

        cb.grid(row=0, column=0, sticky=tk.W+tk.E)
        browse_btn.grid(row=1, column=0, sticky=tk.W+tk.E)

    def load_pulse(self, *args):
        path = self.root_folder + "/" + self.selected_file.get()
        try:
            with open(path, "r") as f:
                self.pulse = loader.read_pulse_file(path)
                self.pulse.set_controller(self.pls_controller)
        except Exception as e:
            self.main.indicate_error()
            print("Error loading pulse file %s" % path)
            print("Error: %s" % e)
        else:
            print("Loaded pulse:", self.pulse)
            PulseManager.set_pulse(self.pulse)
        


def is_num(x, *args):
    try:
        float(x)
    except:
        return False
    else:
        return True

_SPF_instance = None


class SetParameterFrame(tk.LabelFrame):
    _instance = None
    def __init__(self, main, parent, pls_controller, *args, **kwargs):
        global _SPF_instance
        super(SetParameterFrame, self).__init__(parent, *args, text="Parameter Controls", **kwargs)
        PulseManager.register(self)
        self.pls_controller = pls_controller
        self.main = main
        self.parent = parent
        self.to_remove = [] # UI elements to remove when switching pulses
        self.params = {}
        self.pulse = None
        self.init_UI()
        _SPF_instance = self
        # Open and make socket
        # self.pc = PulseCommunicator()

    # def __del__(self):
        # self.kill_threads()

    # @staticmethod
    # def kill_threads(*args):
    #     _SPF_instance.sock_thread.kill()
        

    def init_UI(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.init_param_list()

    def notify(self, event=None, data=None):
        if event == PulseManager.Event.PULSE:
            pulse_obj = PulseManager.get_pulse()
            self.init_param_list(pulse_obj)
            self.pulse = pulse_obj
        # if event == PulseManager.Event.PROGRAM:
        #     # Send to client
        #     try:
        #         pulse = PulseManager.get_pulse()
        #         self.sock_thread.send_info(pulse)
        #     except Exception as e:
        #         print("Failed to send info to client, message: " + str(e))

        
    def init_param_list(self, pulse_obj=None):
        for e in self.to_remove:
            e.grid_forget()
        if pulse_obj is None:
            tb = tk.Label(self, text="Select a pulse file")
            tb.grid(row=0, column=0, sticky=tk.W+tk.E)
            self.to_remove = [tb]
        else:
            self.params = pulse_obj.params.copy()
            param_vars = {k:tk.StringVar(name=k, value=str((int(v) if v is not None else 0)))
                for k, v in self.params.items()}
            lbl_vars = {k:tk.StringVar(name=k+"_lbl", value=str((int(v) if v is not None else 0)))
                for k, v in self.params.items()}
            def _update_param(param_key, param_vars, lbl_vars):
                # param_vars, lbl_vars = dicts
                new_value = param_vars[param_key].get()
                try:
                    new_value = parse_val(new_value, out_as="ns", rounding=True, out_type=int)
                except Exception as e:
                    pass
                else:
                    lbl_vars[param_key].set(str(new_value))
                    self.params[param_key] = new_value
                    PulseManager.set_param_default(**{param_key: new_value})
            # self.param_vals.update(**params)
            n = 1 # Starting row
            self.to_remove = []
            for i, l in enumerate(["Parameter", "New", "Set"]):
                lbl = tk.Label(self, text=l)
                lbl.grid(row=0, column=i)
                self.to_remove.append(lbl)
                
            for row, (k, v) in enumerate(self.params.items()):
                # Create variable
                var = param_vars[k]
                # Bind variable to row
                # if len(var.trace_info()) != 0:
                #     # If the same pulse sequence is loaded again the 
                #     # same variable and trace will be loaded, don't add another
                #     # trace to it. 
                #     print(var, "already has a trace")
                # For some reason the program seems to work better without this

                var.trace_add(
                    "write", 
                    (lambda name, *args: _update_param(name, param_vars, lbl_vars))
                )
                # Store the var here so the repitions panel can get it
                PulseManager.set_var(k, var)
                # Create row
                ## Parameter name
                lbl = tk.Label(self, text=k)
                lbl.grid(row=row+n, column=0, sticky=tk.W+tk.E)
                ## New Value
                box = ttk.Entry(self, text=v, #increment=1,
                    validate="focusout", textvariable=var)
                box.grid(row=row+n, column=1, sticky=tk.W+tk.E)
                ## Set Value
                set_lbl = tk.Label(self, text=var.get(), textvariable=lbl_vars[k])
                set_lbl.grid(row=row+n, column=2, sticky=tk.W+tk.E)

                self.to_remove.append(lbl)
                self.to_remove.append(box)
                self.to_remove.append(set_lbl)
            
            plot_btn = tk.Button(self, text="Plot", command=self.plot_params)
            plot_btn.grid(row=row+n+1, column=1, sticky=tk.W+tk.E)
            prog_btn = tk.Button(self, text="Program", command=self.program_pulse)
            prog_btn.grid(row=row+n+2, column=1, sticky=tk.W+tk.E)
            prog_start_btn = tk.Button(self, text="Prog & Start", command=self.prog_and_start)
            prog_start_btn.grid(row=row+n+3, column=1, sticky=tk.W+tk.E)
            self.to_remove.append(plot_btn)
            self.to_remove.append(prog_btn)
            self.to_remove.append(prog_start_btn)


    def plot_params(self, *args):
        self.pulse.plot_sequence(**self.params)

    def prog_and_start(self, *args, stopping=True):
        self.program_pulse()
        self.start_seq()

    # @staticmethod
    # def program_a_pulse(pulse, params, *args, stopping=False):
    #     try:
    #         raw_seq = pulse.eval(**params)
    #     except:
    #         print("Sequence parameters have not all been specified.")
    #     else:
    #         PulseManager.set_pulse(raw_seq, notify=False)
    #         PulseManager.program(stopping=stopping)



    def program_pulse(self, *args, pulse=None, stopping=False):
        original = PulseManager.get_pulse()
        if pulse is None:
            pulse = self.pulse
        raw_pulse = pulse.eval(**self.params)
        try:
            PulseManager.set_pulse(raw_pulse, notify=False)
            PulseManager.program(stopping=True)
            PulseManager.set_pulse(original, notify=False) 
        except Exception as e:
            self.main.indicate_error()
            raise e

    def start_seq(self, *args):
        # self.pls_controller.stop() # This is fine to run even if already stopped.
        print("Starting sequence")
        try:
            PulseManager.start()
        except Exception as e:
            self.main.indicate_error()
            raise e

    def stop_seq(self, *args):
        print("Stopping sequence")
        try:
            PulseManager.stop()
        except Exception as e:
            self.main.indicate_error()
            raise e

            

    
class PulseToolsBox(tk.LabelFrame):
    def __init__(self, main_app, parent, *args, **kwargs):
        super(PulseToolsBox, self).__init__(parent, *args, **kwargs) 
        self.main = main_app
        self.parent = parent

        self.init_UI()

    def init_UI(self):
        # tabs = ttk.Notebook(self)
        # pulse_shape_tab = PulseShapeFrame(tabs)
        repetitions_tab = RepetitionsFrame(self.main, self, text="Repetitions")
        # tabs.add(pulse_shape_tab, text="Pulse Shape")
        # tabs.add(repetitions_tab, text="Repetitions")
        repetitions_tab.pack(fill=tk.BOTH, expand=True)

class PinControls(tk.LabelFrame):
    def __init__(self, main_app, parent, n_cols=4, *args, **kwargs):
        super(PinControls, self).__init__(parent, *args,)
        self.parent = parent
        self.main = main_app
        self.n_cols = n_cols
        self.def_label = tk.Label(self, text="Select a pulse")

    def update_ui(self):
        pulse = PulseManager.get_pulse()

        if pulse is None:
            self.def_label.grid(row=0, column=0)
        else:
            self.def_label.grid_forget()
            
    