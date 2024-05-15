from domain.PDDLObject import PDDLObject
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

    def setPainted(self, p):
        self.__painted = p

    @PDDLPredicate
    def painted(self: 'CubeSide'):
        return self.isPainted()

    @PDDLPredicate
    def up(self: 'CubeSide'):
        return self.isUp()

    def __str__(self):
        return f"CubeSide:{self.__painted, self.__up}"
