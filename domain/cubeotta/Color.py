from domain.PDDLObject import PDDLObject
from domain.decorators.PDDLPredicate import PDDLPredicate
from domain.decorators.PDDLType import PDDLType


@PDDLType
class Color(PDDLObject):
    def __init__(self, color):
        super().__init__()
        self.name = color
        self.__empty = False  # for the time being we assume that we never run out of color

    @PDDLPredicate
    def empty(self: 'Color'):
        return self.__empty
