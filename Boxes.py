import wx
import os
import sys

class SelectPulseStaticBox(wx.StaticBoxSizer):
    def __init__(self, root_folder, parent, *args, **kwargs):
        sb = wx.StaticBox(parent, label="Select Pulse Sequence")
        super(SelectPulseStaticBox, self).__init__(sb, wx.VERTICAL, *args, **kwargs)
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
        cb = wx.ComboBox(self.parent, choices=pulse_list, style=wx.CB_READONLY)
        browse_btn = wx.Button(self.parent, label="Browse")

        self.Add(cb, flag=wx.LEFT|wx.TOP, border=10)
        self.Add(browse_btn, flag=wx.LEFT|wx.BOTTOM, border=10)


class SetParameterBox(wx.StaticBoxSizer):
    def __init__(self, parent, *args, **kwargs):
        sb = wx.StaticBox(parent, label="Parameters")
        super(SetParameterBox, self).__init__(sb, wx.VERTICAL, *args, **kwargs)
        self.parent = parent

        self.init_UI()

    def init_UI(self):
        tb = wx.StaticText(self.parent, label="Static Text Field")
        self.Add(tb)
    
class PulseToolsBox(wx.StaticBoxSizer):
    def __init__(self, parent, *args, **kwargs):
        sb = wx.StaticBox(parent, label="Pulse Tools")
        super(PulseToolsBox, self).__init__(sb, *args, **kwargs) # Leaving out wx.V/H because it doesn't matter
        self.parent = parent

        self.init_UI()

    def init_UI(self):
        tb = wx.StaticText(self.parent, label="Another static text field.")
        self.Add(tb)