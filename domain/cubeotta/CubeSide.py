from unified_planning.shortcuts import And, Not

from domain.PDDLObject import PDDLObject
from domain.decorators.PDDLAction import PDDLAction
from domain.decorators.PDDLEffect import PDDLEffect
from domain.decorators.PDDLPrecondition import PDDLPrecondition
from domain.decorators.PDDLPredicate import PDDLPredicate
from domain.decorators.PDDLType import PDDLType


@PDDLType
class CubeSide(PDDLObject):
    def __init__(self, up: bool, idx: int, cube_ref: int):
        super().__init__()
        self.__painted = False
        self.__up = up
        self.idx = idx
        self.cube = cube_ref

    def isPainted(self: 'CubeSide'):
        return self.__painted

    def isUp(self: 'CubeSide'):
        return self.__up

    def setUp(self, up):
        self.__up = up

    @PDDLPredicate
    def painted(self: 'CubeSide'):
        return self.isPainted()

    @PDDLPredicate
    def up(self: 'CubeSide'):
        return self.isUp()

    @PDDLPrecondition(lambda cube, side: And(
        Not(side.painted()),
        side.up(),
        cube.cube_has_side(side),
        cube.loaded()))
    @PDDLEffect(lambda cube, side: side.painted(), True)
    @PDDLAction
    def paint(side: 'CubeSide', cube: 'Cube'):
        print(f"Painting side {side.idx} of cube {side.cube} (Side was {'up' if side.isUp() else 'down'})")
        side.__painted = True

    def __str__(self):
        return f"CubeSide:{self.__painted, self.__up}"
