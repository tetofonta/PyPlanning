from unified_planning.shortcuts import Not, And, Exists
from AIROB.domain import PDDLObject
from AIROB.domain.decorators import PDDLEffect, PDDLPrecondition, PDDLPredicate, PDDLType, PDDLAction, PDDLActionMessage


@PDDLType
class Brush(PDDLObject):
    def __init__(self, idx):
        super().__init__()
        self.hasColor = False
        self.color = None
        self.picked = False
        self.loaded = False
        self.idx = idx

    def get_id(self) -> str:
        return f"Brush_{self.idx}"

    def isLoaded(self):
        return self.loaded

    @PDDLPredicate()
    def loaded(self: 'Brush'):
        return self.isLoaded()

    @PDDLPrecondition(lambda brush, env:
                      And(Not(brush.loaded()),
                          Not(Exists(Brush.loaded(env.var(Brush)), env.var(Brush)))))
    @PDDLEffect(lambda brush: brush.loaded(), True)
    @PDDLAction(True)
    def load(brush: 'Brush'):
        print(f"Loading brush {brush.idx}")
        brush.loaded = True

    @PDDLActionMessage("Brush_load")
    def load_message(brush: 'Brush'):
        return f"Please load the brush {brush.idx}"

    @PDDLPrecondition(lambda brush: And(brush.loaded(),
                                        Not(brush.hasColor()),
                                        Not(brush.picked())))
    @PDDLEffect(lambda brush: brush.loaded(), False)
    @PDDLAction(True)
    def unload(brush: 'Brush'):
        print(f"Unloading brush {brush.idx}")
        brush.loaded = False

    @PDDLActionMessage("Brush_unload")
    def unload_message(brush: 'Brush'):
        return f"Please unload the brush {brush.idx}"

    @PDDLPrecondition(lambda brush, color: And(brush.loaded(),
                                               Not(brush.hasColor()),
                                               brush.picked(),
                                               Not(color.empty())
                                               ))
    @PDDLEffect(lambda brush: brush.hasColor(), True)
    @PDDLAction()
    def pickColor(brush: 'Brush', color: 'Color'):
        print(f"Picking color {color.name} with brush {brush.idx}")
        brush.color = color
        brush.hasColor = True

    @PDDLPrecondition(lambda brush: And(brush.loaded(),
                                        brush.hasColor(),
                                        brush.picked()
                                        ))
    @PDDLEffect(lambda brush: brush.hasColor(), False)
    @PDDLAction()
    def clearBrush(brush: 'Brush'):
        print(f"Clearing brush {brush.idx}")
        brush.color = None
        brush.hasColor = False

    @PDDLPredicate()
    def hasColor(self: 'Brush'):
        return self.hasColor

    def setHasColor(self, c):
        self.hasColor = c

    def setColor(self, c):
        self.color = c

    @PDDLPredicate()
    def picked(self: 'Brush'):
        return self.isPicked()

    def isPicked(self: 'Brush'):
        return self.picked

    def setPicked(self, p):
        self.picked = p
