import wx
import tkinter as tk

from src.Boxes import *

PULSE_FOLDER = "pulses"

class AppFrame(tk.Tk):
    def __init__(self, *args, **kwargs):
        super(AppFrame, self).__init__(*args, **kwargs)
        self.title("Pulse manager")
        self.init_ui()
    
    def init_ui(self):
        # Main window pane
        main_panel = tk.PanedWindow(self, relief=tk.RAISED, orient=tk.HORIZONTAL)
        main_panel.pack(fill=tk.BOTH, expand=True)

        # Left | Right panes
        vbox_left = tk.PanedWindow(main_panel, relief=tk.RAISED, orient=tk.VERTICAL)
        vbox_right = tk.PanedWindow(main_panel, relief=tk.RAISED, orient=tk.VERTICAL)
        main_panel.add(vbox_left, stretch="always")
        main_panel.add(vbox_right, stretch="always")

        # Pulse select panel
        select_pulse_pane = SelectPulseFrame(vbox_left, PULSE_FOLDER, padx=5, pady=5, width=50)
        select_pulse_pane.pack(fill=tk.BOTH, expand=True)
        vbox_left.add(select_pulse_pane, stretch="always")
        # Parameter panel
        edit_params_bs = SetParameterFrame(vbox_left)
        # Pulse tools panel
        pulse_tools_bs = PulseToolsBox(vbox_right)

        vbox_left.add(edit_params_bs, stretch="always")
        vbox_right.add(pulse_tools_bs, stretch="always")

        button_pane = tk.Frame(vbox_right)
        button_pane.pack(fill=tk.BOTH, expand=False)
        button_pane.grid_columnconfigure(0, weight=1)
        button_pane.grid_columnconfigure(1, weight=1)
        start_btn = tk.Button(button_pane, text="Start")
        start_btn.grid(row=0, column=0)
        stop_btn = tk.Button(button_pane, text="Stop")
        stop_btn.grid(row=0, column=1)
        vbox_right.add(button_pane, stretch="never")


    def OnQuit(self, e):
        self.Close()

def main():
    # app = wx.App(redirect=True, filename="log.txt")
    frame = AppFrame()
    # frame.Show()
    tk.mainloop()

if __name__ == '__main__':
    main()