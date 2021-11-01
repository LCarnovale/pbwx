from enum import Enum
from pulse_src.pulse_utils import PulseBlasterError, RawSequence, SequenceProgram, init_board
    

class PulseManagerException(Exception):
    """ Common base class for exceptions in this module. """
    def __init__(self, message):
        super().__init__(message)
    
_instance = None
class PulseManager:
    """ Singleton instance for the PulseManager class. """
    pulse_name = None

    Event = Enum(
        value="Event",
        names="PULSE CONTROLLER START STOP PROGRAM PREPROGRAM"   # New pulse, controller
    )
    def __init__(self, pulse:RawSequence=None, controller:SequenceProgram=None):
        global _instance
        if _instance is not None:
            raise PulseManagerException("Cannot initialise multiple instances of PulseManager.")
        init_board()
        self.pulse = pulse
        self.controller = controller
        self.observers = []
        self.vars = {}
        # self.pulse_name = None
        _instance = self

    # def __new__(cls, *args, **kwargs):
    #     global _instance
    #     if _instance is None:
    #         _instance = super().__new__(cls)
    #     return _instance

    def notify(self, event=None, data=None):
        for obj in self.observers:
            obj.notify(event=event, data=data)

    def _set_param_default(self, **kwargs):
        self.pulse.set_param_default(**kwargs)

    @staticmethod
    def set_param_default(**kw_params):
        _instance.pulse.set_param_default(**kw_params)

    def _register(self, observer):
        self.observers.append(observer)

    @staticmethod
    def register(observer):
        _instance.observers.append(observer)

    @staticmethod
    def init():
        global _instance
        if _instance is None:
            _instance = PulseManager()
    
    def _get_pulse(self):
        return self.pulse
    
    @staticmethod
    def get_pulse():
        return _instance.pulse

    def _set_pulse(self, pulse:RawSequence, notify=True):
        if self.controller is not None and pulse is not None:
            pulse.set_controller(self.controller)

        self.pulse = pulse
        if notify:
            self.notify(event=PulseManager.Event.PULSE)

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
        
        if `notify=True` (default), then notify all observers, first with an
        EVENT.PREPROGRAM event before programming, and then with an Event.PROGRAM event
        after programming, with `data` being set to the return value of the program call.

        if `stopping=True` (default `False`), then `stop()` will be called first, without notifying.
        """
        if notify:
            _instance.notify(event=PulseManager.Event.PREPROGRAM)
        if stopping:
            _instance.stop(notify=False)
        err = None
        try:
            _instance.pulse.program_seq(*args, **kwargs)
        except PulseBlasterError as e:
            err = e
            print("Programming failed, Error: %s, message: %s" % (type(e), e))
        finally:
            if notify:            
                _instance.notify(event=PulseManager.Event.PROGRAM, data=err)

    @staticmethod
    def start(notify=True, allow_controller_start=False):
        """ Send a start request to the attached pulse.
        
        If `allow_controller_start=True` (default `False`), and there is no
        attached pulse, then the controller will be sent a start request.

        If the pulse and/or controller is None, a PulseManagerException will be raised. """
        if _instance.pulse is not None:
            print("O-O-O Sequence STARTED O-O-O")
            _instance.pulse.start()
        else:
            if not allow_controller_start:
                raise PulseManagerException("No pulse attached.")            
            else:
                if _instance.controller is not None:
                    print("O-O-O Sequence STARTED O-O-O")
                    _instance.controller.run()
                else:
                    raise PulseManagerException("No controller attached.")
     
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


    