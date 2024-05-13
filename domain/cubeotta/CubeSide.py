from unified_planning.shortcuts import Not, And

from domain.PDDLObject import PDDLObject
from domain.decorators.PDDLAction import PDDLAction
from domain.decorators.PDDLEffect import PDDLEffect
from domain.decorators.PDDLPrecondition import PDDLPrecondition
from domain.decorators.PDDLPredicate import PDDLPredicate, PDDLPredicateDefault
from domain.decorators.PDDLType import PDDLType


@PDDLType
class CubeSide(PDDLObject):
    def __init__(self, idx):
        super().__init__()
        self.__painted = False
        self.__index = idx

    @PDDLPredicate
    def painted(self: 'CubeSide'):
        return self.__painted

    @PDDLPredicate
    def connected(self: 'CubeSide', oth: 'CubeSide'):
        return abs(self.__index - oth.__index) == 1

    @PDDLPredicate
    def up(self: 'CubeSide'):
        return self.__index == 0

    @PDDLPrecondition(lambda _self: And(Not(CubeSide.painted(_self)), CubeSide.up(_self)))
    @PDDLEffect(lambda _self: CubeSide.painted(_self), True)
    @PDDLAction
    def paint(self: 'CubeSide'):
        self.__painted = True

    @PDDLPrecondition(lambda _self, _oth: And(Not(CubeSide.up(_oth)), CubeSide.up(_self), CubeSide.connected(_self, _oth)))
    @PDDLEffect(lambda _self, _oth: CubeSide.up(_oth), True)
    @PDDLEffect(lambda _self, _oth: CubeSide.up(_self), False)
    @PDDLAction
    def turn_cube(self: 'CubeSide', oth: 'CubeSide'):
        self.__index, oth.__index = oth.__index, self.__index

    def __str__(self):
        return f"{self.__index, self.__painted}"
