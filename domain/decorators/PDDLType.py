from domain.PDDLEnvironment import PDDLEnvironment
from domain.PDDLObject import PDDLObject


def PDDLType(cls):
    assert PDDLObject in cls.__mro__
    inst = PDDLEnvironment.get_instance()
    inst.set_type(cls)
    return cls
