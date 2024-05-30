from unified_planning.shortcuts import Not, And, Exists
from AIROB.domain import PDDLObject
from AIROB.domain.decorators import PDDLEffect, PDDLPrecondition, PDDLPredicate, PDDLType, PDDLAction


@PDDLType
class Dryer(PDDLObject):
    def __init__(self, idx):
        super().__init__()
        self.turnedOn = False
        self.picked = False
        self.loaded = False
        self.idx = idx

    def get_id(self) -> str:
        return f"Dryer_{self.idx}"

    def isLoaded(self):
        return self.loaded

    @PDDLPredicate()
    def loaded(self: 'Dryer'):
        return self.isLoaded()

    @PDDLPrecondition(lambda dryer, env:
                      And(Not(dryer.loaded()),
                          Not(Exists(Dryer.loaded(env.var(Dryer)), env.var(Dryer)))))
    @PDDLEffect(lambda dryer: dryer.loaded(), True)
    @PDDLAction()
    def load(dryer: 'Dryer'):
        print(f"Loading dryer {dryer.idx}")
        dryer.loaded = True

    @PDDLPrecondition(lambda dryer: And(dryer.loaded(),
                                        Not(dryer.turnedOn()),
                                        Not(dryer.picked())))
    @PDDLEffect(lambda dryer: dryer.loaded(), False)
    @PDDLAction()
    def unload(dryer: 'Dryer'):
        print(f"Unloading dryer {dryer.idx}")
        dryer.loaded = False

    @PDDLPrecondition(lambda dryer:
                      And(Not(dryer.turnedOn()), dryer.loaded(), dryer.picked()))
    @PDDLEffect(lambda dryer: dryer.turnedOn(), True)
    @PDDLAction()
    def turnOn(dryer: 'Dryer'):
        print(f"Turning on dryer {dryer.idx}")
        dryer.turnedOn = True

    @PDDLPrecondition(lambda dryer:
                      And(dryer.turnedOn(), dryer.loaded(), dryer.picked()))
    @PDDLEffect(lambda dryer: dryer.turnedOn(), False)
    @PDDLAction()
    def turnOff(dryer: 'Dryer'):
        print(f"Turning off dryer {dryer.idx}")
        dryer.turnedOn = False

    @PDDLPredicate()
    def turnedOn(self: 'Dryer'):
        return self.isTurnedOn()

    def isTurnedOn(self):
        return self.turnedOn

    def setTurnedOn(self, on):
        self.turnedOn = on

    @PDDLPredicate()
    def picked(self: 'Dryer'):
        return self.isPicked()

    def isPicked(self: 'Dryer'):
        return self.picked

    def setPicked(self, p):
        self.picked = p