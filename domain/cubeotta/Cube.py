from unified_planning.shortcuts import Not, And, Exists, Forall
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
        self.__dry = True

    @PDDLPredicate
    def cube_has_side(self: 'Cube', side: 'CubeSide'):
        for s in self.sides:
            if s.instance.get_id() == side.get_id(): return True
        return False

    def isPainted(self):
        return all(map(lambda x: x.instance.isPainted(), self.sides))

    def painted(self: 'Cube'):
        return And(x.painted() for x in self.sides)

    def dry(self: 'Cube'):
        return And(x.dry() for x in self.sides)

    def isLoaded(self):
        return self.__loaded

    @PDDLPredicate
    def loaded(self: 'Cube'):
        return self.isLoaded()

    @PDDLPrecondition(lambda cube, env:
                      And(Not(cube.loaded()),
                          Not(Exists(Cube.loaded(env.var(Cube)), env.var(Cube)))))
    @PDDLEffect(lambda cube: cube.loaded(), True)
    @PDDLAction
    def load(cube: 'Cube'):
        print(f"Loading cube {cube.idx}")
        cube.__loaded = True

    @PDDLPrecondition(lambda cube, env: And(cube.loaded(),
                                            Forall(CubeSide.dry(env.var(CubeSide)), env.var(CubeSide))))
    @PDDLEffect(lambda cube: cube.loaded(), False)
    @PDDLAction
    def unload(cube: 'Cube'):
        print(f"Unloading cube {cube.idx}")
        cube.__loaded = False

    @PDDLPrecondition(lambda cube, old_up, new_up: And(old_up.up(),
                                                       Not(new_up.up()),
                                                       cube.cube_has_side(old_up),
                                                       cube.cube_has_side(new_up),
                                                       old_up.dry()))
    @PDDLEffect(lambda old_up: old_up.up(), False)
    @PDDLEffect(lambda new_up: new_up.up(), True)
    @PDDLAction
    def rotate(cube: 'Cube', old_up: 'CubeSide', new_up: 'CubeSide'):
        print(f"Rotating cube {cube.idx} side {new_up.idx} up")
        old_up.setUp(False)
        new_up.setUp(True)
