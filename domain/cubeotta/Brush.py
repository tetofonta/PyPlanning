from unified_planning.shortcuts import Not, And, Exists
from domain.PDDLObject import PDDLObject
from domain.decorators.PDDLAction import PDDLAction
from domain.decorators.PDDLEffect import PDDLEffect
from domain.decorators.PDDLPrecondition import PDDLPrecondition
from domain.decorators.PDDLPredicate import PDDLPredicate
from domain.decorators.PDDLType import PDDLType


@PDDLType
class Brush(PDDLObject):
    def __init__(self, idx):
        super().__init__()
        self.__hasColor = False
        self.__picked = False
        self.__loaded = False
        self.idx = idx

    def isLoaded(self):
        return self.__loaded

    @PDDLPredicate
    def loaded(self: 'Brush'):
        return self.isLoaded()

    @PDDLPrecondition(lambda brush, env:
                      And(Not(brush.loaded()),
                          Not(Exists(Brush.loaded(env.var(Brush)), env.var(Brush)))))
    @PDDLEffect(lambda brush: brush.loaded(), True)
    @PDDLAction
    def load(brush: 'Brush'):
        print(f"Loading brush {brush.idx}")
        brush.__loaded = True

    @PDDLPrecondition(lambda brush: And(brush.loaded(),
                                        Not(brush.hasColor()),
                                        Not(brush.picked())))
    @PDDLEffect(lambda brush: brush.loaded(), False)
    @PDDLAction
    def unload(brush: 'Brush'):
        print(f"Unloading brush {brush.idx}")
        brush.__loaded = False

    @PDDLPredicate
    def hasColor(self: 'Brush'):
        return self.__hasColor

    @PDDLPredicate
    def picked(self: 'Brush'):
        return self.isPicked()

    def isPicked(self: 'Brush'):
        return self.__picked

    def setPicked(self, p):
        self.__picked = p