from unified_planning.shortcuts import Not, And, Exists
from domain.PDDLObject import PDDLObject
from domain.decorators.PDDLAction import PDDLAction
from domain.decorators.PDDLEffect import PDDLEffect
from domain.decorators.PDDLPrecondition import PDDLPrecondition
from domain.decorators.PDDLPredicate import PDDLPredicate
from domain.decorators.PDDLType import PDDLType


@PDDLType
class Dryer(PDDLObject):
    def __init__(self, idx):
        super().__init__()
        self.__turnedOn = False
        self.__picked = False
        self.__loaded = False
        self.idx = idx

    def isLoaded(self):
        return self.__loaded

    @PDDLPredicate
    def loaded(self: 'Dryer'):
        return self.isLoaded()

    @PDDLPrecondition(lambda dryer, env:
                      And(Not(dryer.loaded()),
                          Not(Exists(Dryer.loaded(env.var(Dryer)), env.var(Dryer)))))
    @PDDLEffect(lambda dryer: dryer.loaded(), True)
    @PDDLAction
    def load(dryer: 'Dryer'):
        print(f"Loading dryer {dryer.idx}")
        dryer.__loaded = True

    @PDDLPrecondition(lambda dryer: And(dryer.loaded(),
                                        Not(dryer.turnedOn()),
                                        Not(dryer.picked())))
    @PDDLEffect(lambda dryer: dryer.loaded(), False)
    @PDDLAction
    def unload(dryer: 'Dryer'):
        print(f"Unloading dryer {dryer.idx}")
        dryer.__loaded = False

    @PDDLPrecondition(lambda dryer:
                      And(Not(dryer.turnedOn()), dryer.loaded(), dryer.picked()))
    @PDDLEffect(lambda dryer: dryer.turnedOn(), True)
    @PDDLAction
    def turnOn(dryer: 'Dryer'):
        print(f"Turning on dryer {dryer.idx}")
        dryer.__turnedOn = True

    @PDDLPrecondition(lambda dryer:
                      And(dryer.turnedOn(), dryer.loaded(), dryer.picked()))
    @PDDLEffect(lambda dryer: dryer.turnedOn(), False)
    @PDDLAction
    def turnOff(dryer: 'Dryer'):
        print(f"Turning off dryer {dryer.idx}")
        dryer.__turnedOn = False

    @PDDLPredicate
    def turnedOn(self: 'Dryer'):
        return self.isTurnedOn()

    def isTurnedOn(self):
        return self.__turnedOn

    def setTurnedOn(self, on):
        self.__turnedOn = on

    @PDDLPredicate
    def picked(self: 'Dryer'):
        return self.isPicked()

    def isPicked(self: 'Dryer'):
        return self.__picked

    def setPicked(self, p):
        self.__picked = p