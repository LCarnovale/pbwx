import tkinter as tk

from src.Boxes import *
# import pulse_src as pls
import pulse_src.pulse_utils as pls

PULSE_FOLDER = "pulses"
IR_WHEN_OFF = True
IR_ON_PLS = "IR_ON.pls"
class AppFrame(tk.Tk):
    def __init__(self, *args, **kwargs):
        super(AppFrame, self).__init__(*args, **kwargs)
        self.title("Pulse manager")
        self.pls_controller = pls.SequenceProgram("Main sequence")
        self.init_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def on_close(self):
        SetParameterFrame.kill_threads()
        print("Goodbye")
        self.destroy()

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
        select_pulse_pane = SelectPulseFrame(vbox_left, PULSE_FOLDER, self.pls_controller, padx=5, pady=5, width=50)
        select_pulse_pane.pack(fill=tk.BOTH, expand=True)
        vbox_left.add(select_pulse_pane, stretch="always")
        # Parameter panel
        edit_params_bs = SetParameterFrame(vbox_left, self.pls_controller)
        # Pulse tools panel
        pulse_tools_bs = PulseToolsBox(vbox_right)

        vbox_left.add(edit_params_bs, stretch="always")
        vbox_right.add(pulse_tools_bs, stretch="always")

        button_pane = tk.Frame(vbox_right)
        button_pane.pack(fill=tk.BOTH, expand=False)
        button_pane.grid_columnconfigure(0, weight=1)
        button_pane.grid_columnconfigure(1, weight=1)
        start_btn = tk.Button(button_pane, text="Start", command=edit_params_bs.start_seq)
        start_btn.grid(row=0, column=0)
        stop_btn = tk.Button(button_pane, text="Stop", command=edit_params_bs.stop_seq)
        stop_btn.grid(row=0, column=1)
        vbox_right.add(button_pane, stretch="never")


    def OnQuit(self, e):
        self.Close()


def main():
    frame = AppFrame()
    tk.mainloop()

if __name__ == '__main__':
    main()