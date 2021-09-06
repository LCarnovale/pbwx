import tkinter as tk

class PulseShapeCanvas(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super(PulseShapeCanvas, self).__init__(parent, **kwargs)
        