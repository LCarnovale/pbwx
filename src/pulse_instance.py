from enum import Enum
from pulse_src.pulse_utils import RawSequence, SequenceProgram, init_board



_instance = None
class PulseManager:
    Event = Enum(
        value="Event",
        names="PULSE CONTROLLER START STOP PROGRAM"   # New pulse, controller
    )
    def __init__(self, pulse:RawSequence=None, controller:SequenceProgram=None):
        global _instance
        if _instance is not None:
            raise RuntimeError("Cannot initialise multiple instances of PulseManager.")
        init_board()
        self.pulse = pulse
        self.controller = controller
        self.observers = []
        self.vars = {}
        _instance = self

    def notify(self, event=None, data=None):
        for obj in self.observers:
            obj.notify(event=event, data=data)

    @staticmethod
    def set_param_default(**kw_params):
        _instance.pulse.set_param_default(**kw_params)

    @staticmethod
    def register(observer):
        _instance.observers.append(observer)

    @staticmethod
    def init():
        global _instance
        if _instance is None:
            _instance = PulseManager()
    
    @staticmethod
    def get_pulse():
        return _instance.pulse

    @staticmethod
    def set_pulse(pulse:RawSequence, notify=True):
        """ Set the `pulse` attribute of the PulseManager instance.
        If `notify=True` (default), notify all observers."""
        if _instance.controller is not None and pulse is not None:
            pulse.set_controller(_instance.controller)
        _instance.pulse = pulse
        if notify: 
            _instance.notify(event=PulseManager.Event.PULSE)

    @staticmethod
    def set_controller(controller:SequenceProgram, notify=True):
        """ Set the `controller` attribute of the PulseManager instance.
        If `notify=True` (default), notify all observers."""
        _instance.controller = controller
        if _instance.pulse:
            _instance.pulse.set_controller(controller)
        if notify:
            _instance.notify(event=PulseManager.Event.CONTROLLER)

    @staticmethod
    def program(*args, notify=True, stopping=False, **kwargs):
        """ Call `program_seq(*args, **kwargs)` on the attached pulse object.
        
        if `notify=True` (default), then notify all observers with an Event.PROGRAM event.

        if `stopping=True` (default `False`), then `stop()` will be called first, without notifying.
        """
        if stopping:
            _instance.stop(notify=False)
        ret = _instance.pulse.program_seq(*args, **kwargs)
        if notify:
            _instance.notify(event=PulseManager.Event.PROGRAM, data=ret)

    @staticmethod
    def start(notify=True):
        print("O-O-O  Sequence RUNNING  O-O-O ")
        _instance.pulse.start()
        if notify:
            _instance.notify(event=PulseManager.Event.START)

    @staticmethod
    def stop(notify=True):
        print("|-|-|  Sequence STOPPED  |-|-| ")
        if _instance.pulse is not None:
            _instance.pulse.stop()
        elif _instance.controller is not None:
            _instance.controller.stop()
        if notify:
            _instance.notify(event=PulseManager.Event.STOP)

    @staticmethod
    def get_var(name):
        return _instance.vars[name]
    
    @staticmethod
    def set_var(name, value):
        _instance.vars[name] = value



PulseManager.init()


    