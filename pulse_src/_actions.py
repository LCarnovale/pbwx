import abc

from .spinapi import Inst


def enum(**enums):
    return type('Enum', (), enums)


Targets = enum(
    START = 10000
)

class Action(abc.ABC):
    def set_target(self, target):
        self.target = target

    @abc.abstractmethod
    def get_inst(self):
        pass

    @abc.abstractmethod
    def get_inst_data(self):
        pass
        
class Continue(Action):
    def __init__(self):
        self.set_target(None)
    def get_inst(self):
        return Inst.CONTINUE
    def get_inst_data(self):
        return 0

CTN = Continue()   

class Branch(Action):
    def __init__(self, target):
        self.set_target(target)
    def get_inst(self):
        return Inst.BRANCH
    def get_inst_data(self):
        return self.target

class LoopBegin(Action):
    def __init__(self, count):
        self.count = count
    def get_inst(self):
        return Inst.LOOP
    def get_inst_data(self):
        return self.count

class LoopEnd(Action):
    def __init__(self):
        self.set_target(None)
    def get_inst(self):
        return Inst.END_LOOP
    def get_inst_data(self):
        return 0 

LE = LoopEnd()
