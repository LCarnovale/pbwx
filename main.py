import sys
import tkinter as tk

import pulse_src.load_pulse as lp
# import pulse_src as pls
import pulse_src.pulse_utils as pls
import src.Boxes
import src.PulseFrames
from src.Boxes import *
from src.pulse_instance import PulseManager as PM

PULSE_FOLDER = "pulses"
IR_WHEN_OFF = True
IR_ON_PLS = "IR_ON.pls"
WIDTH = 800
HEIGHT = 600
src.PulseFrames.WIDTH = 500
src.PulseFrames.HEIGHT = HEIGHT


class AppFrame(tk.Tk):
    def __init__(self, *args, **kwargs):
        global PULSE_FOLDER
        super(AppFrame, self).__init__(*args, **kwargs)
        self.title("Pulse manager")

        try:
            os.listdir(PULSE_FOLDER)
        except FileNotFoundError:
            try:
                PULSE_FOLDER = sys.path[0] + "/./" + PULSE_FOLDER
                os.listdir(PULSE_FOLDER)
            except:
                raise FileNotFoundError("Unable to find pulse folder.")

        self.pls_controller = pls.SequenceProgram("Main sequence")
        PM.set_controller(self.pls_controller)
        self.geometry(f"{WIDTH}x{HEIGHT}")
        self.init_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        PM.register(self)
        if IR_WHEN_OFF:
            self.notify(event=PM.Event.STOP)
    
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
        main_panel.add(vbox_left, stretch="always", width=300)
        main_panel.add(vbox_right, stretch="always",width=500)

        # Pulse select panel
        select_pulse_pane = SelectPulseFrame(vbox_left, PULSE_FOLDER, self.pls_controller, padx=5, pady=5, width=50)
        select_pulse_pane.pack(fill=tk.BOTH)
        vbox_left.add(select_pulse_pane)
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
        # button_pane.grid_columnconfigure(2, weight=1)
        btn_size = {"width":10, "height":5}
        # prog_start_btn = tk.Button(button_pane, text="Program & Start", command=self.prog_and_start, **btn_size)
        # prog_start_btn.grid(row=0, column=0)
        start_btn = tk.Button(button_pane, text="Start", command=edit_params_bs.start_seq, **btn_size)
        start_btn.grid(row=0, column=0)
        stop_btn = tk.Button(button_pane, text="Stop", command=edit_params_bs.stop_seq, **btn_size)
        stop_btn.grid(row=0, column=1)

        vbox_right.add(button_pane, stretch="never")


    def OnQuit(self, e):
        self.Close()

    def notify(self, event=None, data=None):
        if event == PM.Event.STOP:
            if IR_WHEN_OFF:
                # Restart IR sequence
                print("Restoring Trap-on state")
                original = PM.get_pulse()
                pulse = lp.read_pulse_file(PULSE_FOLDER+"/"+IR_ON_PLS)
                # Set this as the pulse, don't notify because we don't want
                # to change anything on the frontend.
                PM.set_pulse(pulse, notify=False)
                err = PM.program(notify=False)
                if err:
                    raise Exception("Failed to program IR_ON.pls, program can not continue.")
                PM.start(notify=False)
                # Restore original
                PM.set_pulse(original, notify=False)
        if event == PM.Event.PROGRAM:
            if data:
                # Programming failed.
                self.notify(event=PM.Event.STOP)
    def prog_and_start(self, *args):
        # Get current pulse
        PM.stop(notify=False)
        PM.program(notify=True)
        PM.start(notify=True)
def main():
    frame = AppFrame()
    tk.mainloop()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        SetParameterFrame.kill_threads()
        raise e
