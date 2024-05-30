from unified_planning.shortcuts import Not, And, Exists, Forall
from .CubeSide import CubeSide
from AIROB.domain import PDDLObject
from AIROB.domain.decorators import PDDLEffect, PDDLPrecondition, PDDLPredicate, PDDLType, PDDLAction, PDDLEnvironment, \
    PDDLActionMessage


@PDDLType
class Cube(PDDLObject):
    def __init__(self, idx):
        super().__init__()
        env = PDDLEnvironment.get_instance()
        self.sides = [env.add_object(CubeSide(i == 0, i, idx)) for i in range(6)]
        self.loaded = False
        self.idx = idx
        self.dry = True

    def get_id(self) -> str:
        return f"Cube_{self.idx}"

    @PDDLPredicate()
    def cube_has_side(self: 'Cube', side: 'CubeSide'):
        for s in self.sides:
            if s.instance.get_id() == side.get_id(): return True
        return False

    def isPainted(self):
        return all(map(lambda x: x.instance.isPainted(), self.sides))

    @PDDLPredicate(derived=True)
    def painted(self: 'Cube'):
        return And(x.painted() for x in self.sides)

    @PDDLPredicate(derived=True)
    def dry(self: 'Cube'):
        return And(x.dry() for x in self.sides)

    def isLoaded(self):
        return self.loaded

    @PDDLPredicate()
    def loaded(self: 'Cube'):
        return self.isLoaded()

    @PDDLPrecondition(lambda cube, env:
                      And(Not(cube.loaded()),
                          Not(Exists(Cube.loaded(env.var(Cube)), env.var(Cube)))))
    @PDDLEffect(lambda cube: cube.loaded(), True)
    @PDDLAction(True)
    def load(cube: 'Cube'):
        print(f"Loading cube {cube.idx}")
        cube.loaded = True

    @PDDLActionMessage("Cube_load")
    def load_message(cube: 'Cube'):
        return f"Please load the cube {cube.idx}"

    @PDDLPrecondition(lambda cube, env: And(cube.loaded(),
                                            Forall(CubeSide.dry(env.var(CubeSide)), env.var(CubeSide))))
    @PDDLEffect(lambda cube: cube.loaded(), False)
    @PDDLAction()
    def unload(cube: 'Cube'):
        print(f"Unloading cube {cube.idx}")
        cube.loaded = False

    @PDDLActionMessage("Cube_unload")
    def unload_message(cube: 'Cube'):
        return f"Please unload the cube {cube.idx}"

    @PDDLPrecondition(lambda cube, old_up, new_up: And(old_up.up(),
                                                       Not(new_up.up()),
                                                       cube.cube_has_side(old_up),
                                                       cube.cube_has_side(new_up),
                                                       old_up.dry()))
    @PDDLEffect(lambda old_up: old_up.up(), False)
    @PDDLEffect(lambda new_up: new_up.up(), True)
    @PDDLAction(True)
    def rotate(cube: 'Cube', old_up: 'CubeSide', new_up: 'CubeSide'):
        print(f"Rotating cube {cube.idx} side {new_up.idx} up")
        old_up.setUp(False)
        new_up.setUp(True)

    @PDDLActionMessage("Cube_rotate")
    def rotate_message(cube: 'Cube', old_up: 'CubeSide', new_up: 'CubeSide'):
        return f"Please rotate the cube from side {old_up.idx} to side {new_up.idx}"
