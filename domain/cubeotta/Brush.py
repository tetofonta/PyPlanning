from unified_planning.shortcuts import Not, And, Exists
from domain.PDDLObject import PDDLObject
from domain.cubeotta.Color import Color
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
        self.__color = None
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

    @PDDLPrecondition(lambda brush, color: And(brush.loaded(),
                                               Not(brush.hasColor()),
                                               brush.picked(),
                                               Not(color.empty())
                                               ))
    @PDDLEffect(lambda brush: brush.hasColor(), True)
    @PDDLAction
    def pickColor(brush: 'Brush', color: 'Color'):
        print(f"Picking color {color.name} with brush {brush.idx}")
        brush.__color = color
        brush.__hasColor = True

    @PDDLPrecondition(lambda brush: And(brush.loaded(),
                                        brush.hasColor(),
                                        brush.picked()
                                        ))
    @PDDLEffect(lambda brush: brush.hasColor(), False)
    @PDDLAction
    def clearBrush(brush: 'Brush'):
        print(f"Clearing brush {brush.idx}")
        brush.__color = None
        brush.__hasColor = False

    @PDDLPredicate
    def hasColor(self: 'Brush'):
        return self.__hasColor

    def setHasColor(self, c):
        self.__hasColor = c

    def setColor(self, c):
        self.__color = c

    @PDDLPredicate
    def picked(self: 'Brush'):
        return self.isPicked()

    def isPicked(self: 'Brush'):
        return self.__picked

    def setPicked(self, p):
        self.__picked = p
