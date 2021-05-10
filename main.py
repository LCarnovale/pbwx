import wx

from Boxes import SelectPulseStaticBox, SetParameterBox

PULSE_FOLDER = "pulses"

class AppFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(AppFrame, self).__init__(*args, **kwargs)

        self.init_ui()
    
    def init_ui(self):
        panel = wx.Panel(self)

        fgs = wx.FlexGridSizer(2, 2, 10, 10)

        # hbox = wx.BoxSizer(wx.HORIZONTAL)
        # vbox_left = wx.BoxSizer(wx.VERTICAL)
        # vbox_right = wx.BoxSizer(wx.VERTICAL)
        
        select_pulse_bs = SelectPulseStaticBox(PULSE_FOLDER, panel)
        edit_params_bs = SetParameterBox(panel)


        vbox_left.Add(select_pulse_bs, 
            flag=wx.LEFT|wx.TOP|wx.RIGHT|wx.EXPAND, border=10)

        vbox_left.Add(edit_params_bs, 
            flag=wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND, border=10)

        

        hbox.Add(vbox_left)
        hbox.Add(vbox_right)

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