import tkinter as tk

COLOUR_OFF = "#425442"
COLOUR_ON = "#00ff00"

class IndicatorLED(tk.PanedWindow):
    def __init__(self, parent, label_text, variable:tk.Variable, str_mapping=None,
            width=100, height=30, orient=tk.HORIZONTAL, **kwargs):
        """ Create a new Indicator LED element. 
        `label_text` will appear to the left of the LED.
        `variable` will influence the color of the indicator.
        `str_mapping` should be a dictionary mapping values of `variable` to
        colours. By default, `False`/`True`, as booleans or strings,
        will be mapped to `COLOUR_OFF`/`COLOUR_ON`, defined 
        in `led_indicator.py`. The dictionary should map a value of `variable` to a 
        valid colour to be used as a fill value for the indicator.
        
        Automatically adds a trace to the variable to update the indicator on writes to
        the variable."""
        super(IndicatorLED, self).__init__(parent, showhandle=False, width=width, height=height, **kwargs)
        self.label_txt = label_text
        self.var = variable
        self.width = width
        self.height = height
        if str_mapping is None:
            str_mapping = {
                True: COLOUR_ON,    "True": COLOUR_ON,
                False: COLOUR_OFF, "False": COLOUR_OFF,
            }
        self.mapping = str_mapping
        self.init_UI()
        # Create trace
        self.var.trace_add("write", self.trace_f)

    def trace_f(self, *args):
        val = self.var.get()
        try:
            fill = self.mapping[val]
        except KeyError:
            print("No mapping found for %s, type %s" % (val, type(val)))
            pass
        else:
            self.set_fill(fill)

    def init_UI(self):
        # Create label
        lbl = tk.Label(self, text=self.label_txt)
        self.add(lbl, stretch="never", width=self.width-self.height)
        
        canvas = tk.Canvas(self, width=self.height, height=self.height)
        self.canvas = canvas
        # Centre x, y
        self.add(canvas, stretch="never", width=self.height)
        c = canvas.winfo_width()
        h = canvas.winfo_height()
        print(c, h)
        c = self.height
        a, b = 0.1, .8
        self._oval = canvas.create_oval(a*c, a*c, b*c, b*c, fill=COLOUR_OFF)

    def set_fill(self, fill):
        if self.canvas is None:
            raise Exception("Canvas has not been initialized yet.")
        self.canvas.itemconfig(self._oval, fill=fill)