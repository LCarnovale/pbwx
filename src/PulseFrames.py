import tkinter as tk
import tkinter.ttk as ttk
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
        self.init_UI()
        _RF_instance = self

    def init_UI(self):
        # Parameter list | Repition options
        pane = tk.PanedWindow(self, orient=tk.HORIZONTAL)

        param_list = tk.Frame(pane, background="red")
        param_list.grid_columnconfigure(0, weight=1)
        param_list.grid_columnconfigure(1, weight=1)
        param_list.grid_columnconfigure(2, weight=1)
        label1 = tk.Label(param_list, text="Parameter list")
        label1.grid(row=0, column=0, sticky=tk.W)
        pane.add(param_list, stretch="always")
        param_list.pack(fill=tk.BOTH, expand=True)

        self.param_list = param_list
        self.init_param_list()

        options = tk.Frame(pane, background="green")
        label2 = tk.Label(options, text="Repition Options")
        label2.grid(row=0, column=0, sticky=tk.E)
        pane.add(options, stretch="always")
        options.pack(fill=tk.BOTH, expand=True)
        self.options_pane = options


    @staticmethod
    def send_pulse_object(pulse_obj=None):
        _RF_instance.init_param_list(pulse_obj)
        
    def init_param_list(self, pulse_obj=None):
        for e in self.to_remove:
            e.grid_forget()
        if pulse_obj is None:
            tb = tk.Label(self, text="Select a pulse file")
            tb.grid(row=0, column=0, sticky=tk.W+tk.E)
            self.to_remove = [tb]
        else:
            self.params = pulse_obj.params.copy()
            param_list = list(self.params.items())
            param_vars = {k+"_reps":tk.StringVar(name=k+"_reps", value=str((int(v) if v is not None else 0)))
                for k, v in param_list}
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
                    self.params[param_key] = new_value

            # self.param_vals.update(**params)
            n = 1 # Starting row
            self.to_remove = []
            for i, l in enumerate(["Parameter", "Start", "End"]):
                lbl = tk.Label(self, text=l)
                lbl.grid(row=0, column=i)
                self.to_remove.append(lbl)
                
            for row, (k, v) in enumerate(param_list):
                # Create variable
                var = param_vars[k+"_reps"]
                # Bind variable to row
                if len(var.trace_info()) == 0:
                    # If the same pulse sequence is loaded again the 
                    # same variable and trace will be loaded, don't add another
                    # trace to it. 
                    var.trace_add("write", lambda name, *args: _update_param(name, self.params, param_vars, lbl_vars))
                else:
                    print(var, "already has a trace")
                # Create row
                lbl = tk.Label(self, text=k)
                lbl.grid(row=row+n, column=0, sticky=tk.W+tk.E)
                box = tk.Entry(self, text=v, 
                    validate="focusout", textvariable=var)
                box.grid(row=row+n, column=2, sticky=tk.W+tk.E)
                set_lbl = tk.Label(self, text=var.get(), textvariable=tk.StringVar(name=k+"_lbl"))
                set_lbl.grid(row=row+n, column=1, sticky=tk.W+tk.E)
                self.to_remove.append(lbl)
                self.to_remove.append(box)
                self.to_remove.append(set_lbl)
