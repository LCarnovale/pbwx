import wx
import tkinter as tk

from Boxes import *

PULSE_FOLDER = "pulses"

class AppFrame(tk.Tk):
    def __init__(self, *args, **kwargs):
        super(AppFrame, self).__init__(*args, **kwargs)
        self.title("Pulse manager")
        self.init_ui()
    
    def init_ui(self):
        main_panel = tk.PanedWindow(self, relief=tk.RAISED, orient=tk.HORIZONTAL)
        main_panel.pack(fill=tk.BOTH, expand=True)

        vbox_left = tk.PanedWindow(self, relief=tk.RAISED, orient=tk.VERTICAL)
        vbox_right = tk.PanedWindow(self, relief=tk.RAISED, orient=tk.VERTICAL)
        main_panel.add(vbox_left, stretch="always")
        main_panel.add(vbox_right, stretch="always")

        select_pulse_pane = SelectPulseFrame(vbox_left, PULSE_FOLDER, padx=5, pady=5, width=50)
        select_pulse_pane.pack(fill=tk.BOTH, expand=True)
        vbox_left.add(select_pulse_pane, stretch="always")
        # select_pulse_pane.grid_columnconfigure(0, weight=1)
        edit_params_bs = SetParameterFrame(vbox_left)
        pulse_tools_bs = PulseToolsBox(vbox_right)

        vbox_left.add(edit_params_bs, stretch="always")
        vbox_right.add(pulse_tools_bs, stretch="always")
        # vbox_left.Add(select_pulse_pane, proportion=0,
        #     flag=wx.LEFT|wx.TOP|wx.RIGHT|wx.EXPAND, border=10)

        # vbox_left.Add(edit_params_bs, proportion=1,
        #     flag=wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND, border=10)

        # vbox_right.Add(pulse_tools_bs,
        #     flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)

        # button_hbox = wx.BoxSizer(wx.HORIZONTAL)
        # button_start = wx.Button(main_panel, label="START")
        # button_stop = wx.Button(main_panel, label="STOP")
        # button_hbox.Add(button_start, proportion=0)
        # button_hbox.Add(button_stop, proportion=1)
        # vbox_right.Add(button_hbox, flag=wx.ALIGN_CENTER_HORIZONTAL)

        # main_panel.SetSizer(hbox)

        # hbox.Add(vbox_left, flag=wx.EXPAND|wx.LEFT|wx.TOP|wx.BOTTOM, proportion=0, border=5)
        # hbox.Add(vbox_right, flag=wx.EXPAND|wx.RIGHT|wx.TOP|wx.BOTTOM, proportion=1, border=5)

        # ## Menu

        # menubar = wx.MenuBar()
        # file_menu = wx.Menu()
        # file_item = file_menu.Append(wx.ID_EXIT, 'Quit', 'Quit the app')
        # menubar.Append(file_menu, '&File')
        # self.SetMenuBar(menubar)

        # self.Bind(wx.EVT_MENU, self.OnQuit, file_item)

    def OnQuit(self, e):
        self.Close()

def main():
    # app = wx.App(redirect=True, filename="log.txt")
    frame = AppFrame()
    # frame.Show()
    tk.mainloop()

if __name__ == '__main__':
    main()