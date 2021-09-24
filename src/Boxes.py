import tkinter as tk
import tkinter.ttk as ttk
import os
import sys
from threading import Thread

from pulse_src import load_pulse as loader
from pulse_src import pulse_utils as pu
from .PulseFrames import PulseShapeFrame, RepetitionsFrame
import socket
from sock import PulseCommunicator, HOST, PORT
from main import IR_WHEN_OFF, IR_ON_PLS
_SelPF_instance = None
class SelectPulseFrame(tk.LabelFrame):
    def __init__(self, parent, root_folder, controller, *args, **kwargs):
        """ Provide a parent object and a path in `root_folder` 
        for the folder to look for `.pls` files
        """
        global _SelPF_instance
        super(SelectPulseFrame, self).__init__(parent, *args, text='Select Pulse Sequence', **kwargs)
        self.root_folder = root_folder
        self.parent = parent
        self.selected_file = tk.StringVar(self)
        self.selected_file.trace_add("write", self.load_pulse)
        self.pls_controller = controller
        # self.seq = pulse_sequence

        self.init_UI()
        _SelPF_instance = self
        
    def init_UI(self):
        try:
            pulse_list = os.listdir(self.root_folder)
        except FileNotFoundError:
            try:
                self.root_folder = sys.path[0] + "/./" + self.root_folder
                pulse_list = os.listdir(self.root_folder)
            except:
                raise FileNotFoundError("Unable to find pulse folder.")
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
            print("Error loading pulse file %s" % path)
            print("Error: %s" % e)
        else:
            print("Loaded pulse:", self.pulse)
            SetParameterFrame.send_pulse_object(self.pulse)
            RepetitionsFrame.send_pulse_object(self.pulse)
            PulseShapeFrame.send_pulse_object(self.pulse)
        


def is_num(x, *args):
    print("x:", x)
    print("args:", args)
    try:
        float(x)
    except:
        return False
    else:
        return True

_SPF_instance = None
class SocketThread(Thread):
    def __init__(self):
        super(SocketThread, self).__init__(group=None)
        self.socket = socket.socket()
        self.socket.bind((HOST, PORT))
        self.do_wait = True
        self.send_buffer = None
        self.conn = None
        self.killed = False

    def stop_wait(self):
        self.do_wait = False

    def kill(self):
        self.socket.close()
        self.killed = True

    def run(self):
        # Wait for data to be received
        self.socket.listen()
        while True:
            print("Socket thread waiting for connection.")
            self.conn, addr = self.socket.accept()
            print("Socket thread connected.")
            if self.do_wait:
                try:
                    data = self.conn.recv(8)
                except:
                    print("Socket receive failed, the other end probably closed.")
                    break
                if len(data) == 0:
                    print("Stream ended")
                    break
                if "START" in str(data):
                    print("Received start request")
                    _SPF_instance.start_seq()
                elif "STOP" in str(data):
                    print("Received stop request")
                    self.stop_wait()
                    _SPF_instance.stop_seq()
                elif "EXIT" in str(data):
                    print("Received exit request")
                    self.stop_wait()
                    self.kill()
                    break
                else:
                    print("Received unknown message: %s" % str(data))

            if self.killed:
                break
            
    def send_info(self, raw_seq, byte_order="big"):
        # Send pulse length:
        if self.conn:
            length = raw_seq.length_ns
            length = int(length).to_bytes(16, byte_order)
            self.conn.send(length)
        else:
            print("No connection to send data on yet")

class SetParameterFrame(tk.LabelFrame):
    _instance = None
    def __init__(self, parent, pls_controller, *args, **kwargs):
        global _SPF_instance
        super(SetParameterFrame, self).__init__(parent, *args, text="Parameter Controls", **kwargs)
        self.pls_controller = pls_controller
        self.parent = parent
        self.to_remove = [] # UI elements to remove when switching pulses
        self.params = {}
        self.pulse = None
        self.init_UI()
        _SPF_instance = self
        # Open and make socket
        # self.pc = PulseCommunicator()
        self.sock_thread = SocketThread()
        self.sock_thread.start()
        if IR_WHEN_OFF:
            # Load IR on:
            try:
                ir_on = loader.read_pulse_file(IR_ON_PLS)
            except:
                new_pls = _SelPF_instance.root_folder + "/" + IR_ON_PLS
                ir_on = loader.read_pulse_file(new_pls)

            self.ir_pulse = ir_on
            type(self).program_a_pulse(ir_on)
            self.start_seq()

    def __del__(self):
        self.sock_thread.kill()

    def init_UI(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.init_param_list()

    @staticmethod
    def send_pulse_object(pulse_obj=None):
        _SPF_instance.init_param_list(pulse_obj)
        _SPF_instance.pulse = pulse_obj
        
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
            print("param vars:", param_vars)
            lbl_vars = {k:tk.StringVar(name=k+"_lbl", value=str((int(v) if v is not None else 0)))
                for k, v in self.params.items()}
            def _update_param(param_key, params, param_vars, lbl_vars):
                # params, param_vars, lbl_vars = dicts
                new_value = param_vars[param_key].get()
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
                    (lambda name, *args: _update_param(name, self.params, param_vars, lbl_vars))
                )
                # Create row
                lbl = tk.Label(self, text=k)
                lbl.grid(row=row+n, column=0, sticky=tk.W+tk.E)
                box = ttk.Entry(self, text=v, #increment=1,
                    validate="focusout", textvariable=var)
                box.grid(row=row+n, column=1, sticky=tk.W+tk.E)
                set_lbl = tk.Label(self, text=var.get(), textvariable=lbl_vars[k])
                set_lbl.grid(row=row+n, column=2, sticky=tk.W+tk.E)
                self.to_remove.append(lbl)
                self.to_remove.append(box)
                self.to_remove.append(set_lbl)
            
            plot_btn = tk.Button(self, text="Plot", command=self.plot_params)
            plot_btn.grid(row=row+n+1, column=1, sticky=tk.W+tk.E)
            self.to_remove.append(plot_btn)
            prog_btn = tk.Button(self, text="Program", command=self.program_pulse)
            prog_btn.grid(row=row+n+2, column=1, sticky=tk.W+tk.E)
            self.to_remove.append(prog_btn)

    def plot_params(self, *args):
        print(self.params)
        self.pulse.plot_sequence(**self.params)

    @staticmethod
    def program_a_pulse(pulse, params, *args):
        try:
            raw_seq = pulse.eval(**params)
        except:
            print("Sequence parameters have not all been specified.")
        else:
            pu.init_board()
            raw_seq.program_seq(pu.actions.Branch(0))
        # Send to client
        try:
            _SPF_instance.sock_thread.send_info(raw_seq)
        except Exception as e:
            print("Failed to send info to client, message: " + str(e))


    def program_pulse(self, *args, pulse=None):
        SetParameterFrame.program_a_pulse(self.pulse, self.params)

    def start_seq(self, *args):
        self.pls_controller.stop() # This is fine to run even if already stopped.
        print("Starting sequence")
        self.pls_controller.run()

    def stop_seq(self, *args):
        print("Stopping sequence")
        self.pls_controller.stop()
        if IR_WHEN_OFF:
            type(self).program_a_pulse(self.ir_pulse)
            self.start_seq()

            

    
class PulseToolsBox(tk.LabelFrame):
    def __init__(self, parent, *args, **kwargs):
        super(PulseToolsBox, self).__init__(parent, *args, **kwargs) 
        self.parent = parent

        self.init_UI()

    def init_UI(self):
        tabs = ttk.Notebook(self)
        pulse_shape_tab = PulseShapeFrame(tabs)
        repetitions_tab = RepetitionsFrame(tabs)
        tabs.add(pulse_shape_tab, text="Pulse Shape")
        tabs.add(repetitions_tab, text="Repetitions")
        tabs.pack(fill=tk.BOTH, expand=True)