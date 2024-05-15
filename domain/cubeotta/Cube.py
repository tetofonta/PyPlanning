from unified_planning.model import Variable
from unified_planning.shortcuts import Not, And, Exists
from domain.PDDLEnvironment import PDDLEnvironment
from domain.PDDLObject import PDDLObject
from domain.cubeotta.CubeSide import CubeSide
from domain.decorators.PDDLAction import PDDLAction
from domain.decorators.PDDLEffect import PDDLEffect
from domain.decorators.PDDLPrecondition import PDDLPrecondition
from domain.decorators.PDDLPredicate import PDDLPredicate
from domain.decorators.PDDLType import PDDLType


@PDDLType
class Cube(PDDLObject):
    def __init__(self, idx):
        super().__init__()
        env = PDDLEnvironment.get_instance()
        self.sides = [env.add_object(CubeSide(i == 0, i, idx)) for i in range(6)]
        self.__loaded = False
        self.idx = idx

    @PDDLPredicate
    def cube_has_side(self: 'Cube', side: 'CubeSide'):
        for s in self.sides:
            if s.instance.get_id() == side.get_id(): return True
        return False

    def isPainted(self):
        return all(map(lambda x: x.instance.isPainted(), self.sides))

    def painted(self):
        return And(CubeSide.painted(x) for x in self.sides)

    def isLoaded(self):
        return self.__loaded

    @PDDLPredicate
    def loaded(self: 'Cube'):
        return self.isLoaded()

    @PDDLPrecondition(lambda _self: And(Not(Cube.loaded(_self)), Not(Exists(Cube.loaded(Variable("cube", PDDLEnvironment.get_instance().get_type(Cube))), Variable("cube", PDDLEnvironment.get_instance().get_type(Cube))))))
    @PDDLEffect(lambda _self: Cube.loaded(_self), True)
    @PDDLAction
    def load(self: 'Cube'):
        print(f"Loading cube {self.idx}")
        self.__loaded = True

    @PDDLPrecondition(lambda _self: Cube.loaded(_self))
    @PDDLEffect(lambda _self: Cube.loaded(_self), False)
    @PDDLAction
    def unload(self: 'Cube'):
        print(f"Unloading cube {self.idx}")
        self.__loaded = False

    @PDDLPrecondition(lambda _self, _old_up, _new_up: And(CubeSide.up(_old_up), Not(CubeSide.up(_new_up)), Cube.cube_has_side(_self, _old_up), Cube.cube_has_side(_self, _new_up)))
    @PDDLEffect(lambda _self, _old_up, _new_up: CubeSide.up(_old_up), False)
    @PDDLEffect(lambda _self, _old_up, _new_up: CubeSide.up(_new_up), True)
    @PDDLAction
    def rotate(self: 'Cube', old_up: 'CubeSide', new_up: 'CubeSide'):
        print(f"Rotating cube {self.idx} side {new_up.idx} up")
        old_up.setUp(False)
        new_up.setUp(True)

    @PDDLPrecondition(lambda _self, _side: And(
        Not(CubeSide.painted(_side)),
        CubeSide.up(_side),
        Cube.cube_has_side(_self, _side),
        Cube.loaded(_self)))
    @PDDLEffect(lambda _self, _side: CubeSide.painted(_side), True)
    @PDDLAction
    def paint(self: 'Cube', side: 'CubeSide'):
        print(f"Painting side {side.idx} of cube {side.cube} (Side was {'up' if side.isUp() else 'down'})")
        side.setPainted(True)
