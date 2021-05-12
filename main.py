import wx

from Boxes import *

PULSE_FOLDER = "pulses"

class AppFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(AppFrame, self).__init__(*args, **kwargs)

        self.init_ui()
    
    def init_ui(self):
        panel = wx.Panel(self)

        # fgs = wx.FlexGridSizer(2, 2, 10, 10)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        vbox_left = wx.BoxSizer(wx.VERTICAL)
        vbox_right = wx.BoxSizer(wx.VERTICAL)
        
        select_pulse_bs = SelectPulseStaticBox(PULSE_FOLDER, panel)
        edit_params_bs = SetParameterBox(panel)
        pulse_tools_bs = PulseToolsBox(panel)


        vbox_left.Add(select_pulse_bs, proportion=0,
            flag=wx.LEFT|wx.TOP|wx.RIGHT|wx.EXPAND, border=10)

        vbox_left.Add(edit_params_bs, proportion=1,
            flag=wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND, border=10)

        vbox_right.Add(pulse_tools_bs,
            flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)

        button_hbox = wx.BoxSizer(wx.HORIZONTAL)
        button_start = wx.Button(panel, label="START")
        button_stop = wx.Button(panel, label="STOP")
        button_hbox.Add(button_start, proportion=0)
        button_hbox.Add(button_stop, proportion=1)
        vbox_right.Add(button_hbox, flag=wx.ALIGN_CENTER_HORIZONTAL)

        panel.SetSizer(hbox)

        hbox.Add(vbox_left, flag=wx.EXPAND|wx.LEFT|wx.TOP|wx.BOTTOM, proportion=0, border=5)
        hbox.Add(vbox_right, flag=wx.EXPAND|wx.RIGHT|wx.TOP|wx.BOTTOM, proportion=1, border=5)

        ## Menu

        menubar = wx.MenuBar()
        file_menu = wx.Menu()
        file_item = file_menu.Append(wx.ID_EXIT, 'Quit', 'Quit the app')
        menubar.Append(file_menu, '&File')
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.OnQuit, file_item)

    def OnQuit(self, e):
        self.Close()

def main():
    app = wx.App(redirect=True, filename="log.txt")
    frame = AppFrame(None)
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()