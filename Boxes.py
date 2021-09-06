import wx
import tkinter as tk
import tkinter.ttk as ttk
import os
import sys

class SelectPulseFrame(tk.LabelFrame):
    def __init__(self, parent, root_folder, *args, **kwargs):
        super(SelectPulseFrame, self).__init__(parent, *args, text='Select Pulse Sequence', **kwargs)
        self.root_folder = root_folder
        self.parent = parent

        self.init_UI()
        
    def init_UI(self):
        try:
            pulse_list = os.listdir(self.root_folder)
        except FileNotFoundError:
            try:
                pulse_list = os.listdir(sys.path[0] + "/./" + self.root_folder)
            except:
                raise FileNotFoundError("Unable to find pulse folder.")
        cb = ttk.Combobox(self, values=pulse_list, state="readonly")
        browse_btn = tk.Button(self, text="Browse", width=8,
            command=lambda:print("Browsin'"))

        cb.grid(row=0, column=0, sticky=tk.W+tk.E)
        browse_btn.grid(row=1, column=0, sticky=tk.W+tk.E)


class SetParameterFrame(tk.LabelFrame):
    def __init__(self, parent, *args, **kwargs):
        super(SetParameterFrame, self).__init__(parent, *args, text="Parameter Controls", **kwargs)
        self.parent = parent

        self.init_UI()

    def init_UI(self):
        tb = tk.Label(self, text="Static Text Field")
        tb.grid(row=0, column=0, sticky=tk.W)
    
class PulseToolsBox(tk.LabelFrame):
    def __init__(self, parent, *args, **kwargs):
        super(PulseToolsBox, self).__init__(parent, *args, **kwargs) # Leaving out wx.V/H because it doesn't matter
        self.parent = parent

        self.init_UI()

    def init_UI(self):
        tb = tk.Label(self, text="Another static text field.")
        tb.grid(row=0, column=0, sticky=tk.W)