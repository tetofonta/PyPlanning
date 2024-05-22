from unified_planning.shortcuts import Not, And
from AIROB.domain import PDDLObject
from AIROB.domain.decorators import PDDLEffect, PDDLPrecondition, PDDLPredicate, PDDLType, PDDLAction


@PDDLType
class CubeSide(PDDLObject):
    def __init__(self, up: bool, idx: int, cube_ref: int):
        super().__init__()
        self.__painted = False
        self.__up = up
        self.__dry = True
        self.idx = idx
        self.cube = cube_ref

    def get_id(self) -> str:
        return f"Cube_{self.cube}_side_{self.idx}"

    def isPainted(self: 'CubeSide'):
        return self.__painted

    def isUp(self: 'CubeSide'):
        return self.__up

    def setUp(self, up):
        self.__up = up

    @PDDLPredicate
    def dry(self: 'CubeSide'):
        return self.isDry()

    def isDry(self):
        return self.__dry

    def setDry(self, d: bool):
        self.__dry = d

    @PDDLPredicate
    def painted(self: 'CubeSide'):
        return self.isPainted()

    @PDDLPredicate
    def up(self: 'CubeSide'):
        return self.isUp()

    @PDDLPrecondition(lambda cube, side, brush: And(
        Not(side.painted()),
        side.up(),
        cube.cube_has_side(side),
        cube.loaded(),
        brush.picked(),
        brush.hasColor()
    ))
    @PDDLEffect(lambda cube, side: side.painted(), True)
    @PDDLEffect(lambda cube, side: side.dry(), False)
    @PDDLEffect(lambda brush: brush.hasColor(), False)
    @PDDLAction
    def paint(side: 'CubeSide', cube: 'Cube', brush: 'Brush'):
        print(
            f"Painting side {side.idx} of cube {side.cube} with brush {brush.idx}")  # (Side was {'up' if side.isUp() else 'down'})
        side.__painted = True
        side.__dry = False

    @PDDLPrecondition(lambda cube, dryer, side: And(
        side.painted(),
        side.up(),
        dryer.picked(),
        dryer.turnedOn(),
        Not(side.dry()),
        cube.cube_has_side(side),
        cube.loaded()))
    @PDDLEffect(lambda cube, side: side.dry(), True)
    @PDDLAction
    def drySide(side: 'CubeSide', cube: 'Cube', dryer: 'Dryer'):
        print(f"Drying side {side.idx} of cube {side.cube} using dryer {dryer.idx}")
        side.__dry = True

    def __str__(self):
        return f"CubeSide:{self.__painted, self.__up}"
