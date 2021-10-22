import socket
import sys
import time
import tkinter as tk
import tkinter.font as tf
from threading import Thread
from pulse_src.spinapi import DBG_MODE

import pulse_src.load_pulse as lp
import pulse_src.pulse_utils as pls
import src.Boxes
import src.PulseFrames
from sock import HOST, PORT
from src.Boxes import *
from src.led_indicator import IndicatorLED
from src.pulse_instance import PulseManager as PM

PULSE_FOLDER = "pulses"
IR_WHEN_OFF = True
IR_ON_PLS = "IR_ON.pls"
WIDTH = 900
HEIGHT = 600
src.PulseFrames.WIDTH = 600
src.PulseFrames.HEIGHT = HEIGHT

_app_instance = None
class AppFrame(tk.Tk):
    def __init__(self, *args, **kwargs):
        global PULSE_FOLDER
        global _app_instance
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
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.trap_state = tk.BooleanVar(self, False) # Is the trapping laser on?
        self.pb_running = tk.BooleanVar(self, False)   # Is the pulse blaster running?
        self.prog_ready = tk.BooleanVar(self, False) # Program ready and waiting for labview to accept.
        self.ir_when_off = tk.BooleanVar(self, IR_WHEN_OFF) # Run IR_ON.pls during downtime? 
        self.wait_for_LV = tk.BooleanVar(self, True) # Wait for labview to accept programs?
        if DBG_MODE:
            self.wait_for_LV.set(False)
        self.LV_connected = tk.BooleanVar(self, False)
        self.err_light = tk.BooleanVar(self, False)

        self.sock_thread = SocketThread(self.LV_connected)
        self.sock_thread.start()

        self.init_ui()
        PM.register(self)
        if IR_WHEN_OFF:
            self.notify(event=PM.Event.STOP)

        _app_instance = self
    
    def kill_threads(self):
        self.sock_thread.kill()
    
    def on_close(self):
        self.kill_threads()
        print("Goodbye")
        self.destroy()

    def init_ui(self):
        # Main window pane
        main_panel = tk.PanedWindow(self, relief=tk.RAISED, orient=tk.HORIZONTAL)
        main_panel.pack(fill=tk.BOTH, expand=True)

        # Left | Right panes
        vbox_left = tk.PanedWindow(main_panel, relief=tk.RAISED, orient=tk.VERTICAL)
        vbox_right = tk.PanedWindow(main_panel, relief=tk.RAISED, orient=tk.VERTICAL)
        main_panel.add(vbox_left, stretch="always", width=WIDTH-src.PulseFrames.WIDTH)
        main_panel.add(vbox_right, stretch="always",width=src.PulseFrames.WIDTH)

        # Pulse select panel
        select_pulse_pane = SelectPulseFrame(self, vbox_left, PULSE_FOLDER, self.pls_controller, padx=5, pady=5, width=50)
        select_pulse_pane.pack(fill=tk.BOTH)
        vbox_left.add(select_pulse_pane)
        # Parameter panel
        edit_params_bs = SetParameterFrame(self, vbox_left, self.pls_controller)
        # Pulse tools panel
        pulse_tools_bs = PulseToolsBox(self, vbox_right)

        vbox_left.add(edit_params_bs, stretch="always")
        vbox_right.add(pulse_tools_bs, stretch="always")

        button_pane = tk.Frame(vbox_right)
        button_pane.pack(fill=tk.BOTH, expand=False)
        button_pane.grid_columnconfigure(0, weight=1)
        button_pane.grid_columnconfigure(1, weight=1)
        button_pane.grid_columnconfigure(2, weight=1)
        button_pane.grid_columnconfigure(3, weight=1)
        # prog_start_btn = tk.Button(button_pane, text="Program & Start", command=self.prog_and_start, **btn_size)
        # prog_start_btn.grid(row=0, column=0)
        variables = [
            self.trap_state, self.pb_running, self.prog_ready, self.LV_connected
        ]
        var_lbls = [
            "Trap on", "PB Running", "Program ready", "LV connected"
        ]
        row_n = 0
        # Error indicator
        err_ind = IndicatorLED(button_pane, "Error", self.err_light, width=120)
        err_ind.mapping.update({True:"red"})
        err_ind.grid(row=row_n, column=0, sticky=tk.W+tk.E)
        clear_err_f = lambda *args : self.err_light.set(False)
        # Error clear button
        err_clear_btn = tk.Button(button_pane, text="Clear", command=clear_err_f)
        err_clear_btn.grid(row=row_n, column=1, sticky=tk.W)
        row_n += 1
        n = 0
        n_cols = 4
        for var, lbl in zip(variables, var_lbls):
            indicator = IndicatorLED(button_pane, lbl, var, width=120)
            if var == self.prog_ready:
                indicator.mapping.update({True:"orange"})
            indicator.grid(row=row_n, column=n % n_cols, sticky=tk.W+tk.E)
            n += 1
            if n % n_cols == 0:
                row_n += 1
        row_n += 1

        # Add ir-when-off checkbox
        ir_chkbox = tk.Checkbutton(button_pane, text="IR when off?", variable=self.ir_when_off)
        ir_chkbox.grid(row=row_n, column=1, sticky=tk.W+tk.E) # Place above STOP button
        # Add wait for labview checkbox
        lv_chkbox = tk.Checkbutton(button_pane, text="Wait for labview?", variable=self.wait_for_LV)
        lv_chkbox.grid(row=row_n, column=2, sticky=tk.W+tk.E)
        row_n += 1
        font = tf.Font(size=24, weight="bold")
        btn_size = {"width":10, "height":1, "font":font}
        start_btn = tk.Button(button_pane, text="Start", command=edit_params_bs.start_seq, state=tk.DISABLED, **btn_size)
        start_btn.grid(row=row_n, column=0, sticky=tk.W+tk.E)
        self.start_btn = start_btn
        stop_btn = tk.Button(button_pane, text="Stop", command=edit_params_bs.stop_seq, state=tk.ACTIVE, **btn_size)
        stop_btn.grid(row=row_n, column=1, sticky=tk.W+tk.E)
        self.stop_btn = stop_btn
        close_btn = tk.Button(button_pane, text="Disconnect", command=self.close_controller, **btn_size)
        close_btn.grid(row=row_n, column=2, sticky=tk.W+tk.E)
        con_btn = tk.Button(button_pane, text="Reconnect", command=self.open_controller, **btn_size)
        con_btn.config(state="disabled")
        con_btn.grid(row=row_n, column=3, sticky=tk.W+tk.E)

        vbox_right.add(button_pane, stretch="never")

    def indicate_error(self):
        " Light up front panel error light " 
        self.err_light.set(True)

    def OnQuit(self, e):
        self.Close()

    def notify(self, event=None, data=None):
        if event == PM.Event.PULSE:
            if PM.get_pulse() is not None:
                self.start_btn.config(state=tk.ACTIVE)
                self.stop_btn.config(state=tk.ACTIVE)
            else:
                self.start_btn.config(state=tk.DISABLED)
                self.stop_btn.config(state=tk.DISABLED)
        if event == PM.Event.START:
            self.pb_running.set(True)
        if event == PM.Event.STOP:
            self.trap_state.set(False)
            self.pb_running.set(False)

            if self.ir_when_off.get():
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
                self.pb_running.set(True)
                self.trap_state.set(True)
                # Restore original
                PM.set_pulse(original, notify=False)
        if event == PM.Event.PREPROGRAM:
            if self.wait_for_LV.get():
                self.prog_ready.set(True)
                print("Waiting for LV to be ready for data...")
                # TODO: Move this out of the main thread
                while not self.sock_thread.con_alive:
                    continue
                print("LV detected.")

        if event == PM.Event.PROGRAM:
            # The trap will probably not be on now.
            self.trap_state.set(False)
            self.prog_ready.set(False)
            self.pb_running.set(False)
            if data:
                # Programming failed.
                self.notify(event=PM.Event.STOP)
                self.err_light.set(True)
            else:
                # Send to client
                try:
                    pulse = PulseManager.get_pulse()
                    self.sock_thread.send_info(pulse)
                except Exception as e:
                    self.err_light.set(True)
                    print("Failed to send info to client, message: " + str(e))
        if self.pb_running.get():
            # self.stop_btn.config(state=tk.ACTIVE)
            self.start_btn.config(state=tk.DISABLED)
        else:
            # self.stop_btn.config(state=tk.DISABLED)
            self.start_btn.config(state=tk.ACTIVE)
                    
    def prog_and_start(self, *args):
        # Get current pulse
        PM.stop(notify=False)
        PM.program(notify=True)
        PM.start(notify=True)

    def close_controller(self, *args):
        self.err_light.set(True)
        print("!! PB Connection closed !!")
        self.pls_controller.close()

    def open_controller(self, *args):
        print("** PB Connection opened **")
        self.pls_controller.init()
        
class SocketThread(Thread):
    def __init__(self, connected_var:tk.Variable=None):
        super(SocketThread, self).__init__(group=None)
        self.socket = socket.socket()
        self.socket.bind((HOST, PORT))
        self.do_wait = True
        self.send_buffer = None
        self.conn = None
        self.connected_var = connected_var
        self.killed = False
        self._con_alive = False

    @property
    def con_alive(self):
        return self._con_alive
    
    @con_alive.setter
    def con_alive(self, value:bool):
        self._con_alive = value
        if self.connected_var is not None:
            try:
                self.connected_var.set(value)
            except RuntimeError as e:
                print("Unable to set connection status: " + str(e))

    def stop_wait(self):
        self.do_wait = False

    def kill(self):
        self.socket.close()
        self.killed = True

    def run(self):
        # Wait for data to be received
        self.socket.listen()
        if self.con_alive:
            self.con_alive = False
        
        print("Socket thread waiting for connection.")
        while True:
            if self.killed:
                break
            try:
                if not self.con_alive:
                    self.socket.settimeout(1)
                    self.conn, addr = self.socket.accept()
            except socket.timeout:
                continue
            except:
                print("Socket died. Ending socket thread.")
                self.kill()
                break
            else:
                self.con_alive = True
                print("Socket thread connected.")
            while self.do_wait:
                try:
                    self.conn.settimeout(1)
                    data = self.conn.recv(8)
                except socket.timeout:
                    continue
                except:
                    print("Connection Closed.")
                    self.con_alive = False
                    break
                if len(data) == 0:
                    print("Stream ended (received no data)")
                    self.con_alive = False
                    break
                if "START" in str(data):
                    print("Received start request")
                    PulseManager.start()
                elif "STOP" in str(data):
                    print("Received stop request")
                    # self.stop_wait()
                    PulseManager.stop()
                elif "EXIT" in str(data):
                    print("Received exit request")
                    # PulseManager.stop()
                    self.stop_wait()
                    self.kill()
                    self.con_alive = False
                    break
                else:
                    print("Received unknown message: %s" % str(data))

            
    def send_info(self, raw_seq, byte_order="big"):
        # Send pulse length:
        if self.conn:
            length = raw_seq.length_ns
            length = int(length).to_bytes(16, byte_order)
            self.conn.send(length)
        else:
            print("No connection to send data on yet")

frame = None
def main():
    global frame
    frame = AppFrame()
    tk.mainloop()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        if frame is not None:
            frame.kill_threads()
        raise e
    # finally:
    #     input("Enter to close")
