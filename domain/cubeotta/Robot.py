from unified_planning.shortcuts import Not, And, Exists
from domain.PDDLObject import PDDLObject
from domain.cubeotta.Dryer import Dryer
from domain.decorators.PDDLAction import PDDLAction
from domain.decorators.PDDLEffect import PDDLEffect
from domain.decorators.PDDLPrecondition import PDDLPrecondition
from domain.decorators.PDDLPredicate import PDDLPredicate
from domain.decorators.PDDLType import PDDLType


@PDDLType
class Robot(PDDLObject):
    def __init__(self):
        super().__init__()
        self.__free = True

    @PDDLPredicate
    def free(self: 'Robot'):
        return self.__free

    @PDDLPrecondition(lambda brush, robot:
                      And(Not(brush.picked()),
                          Not(brush.hasColor()),
                          brush.loaded(),
                          robot.free()))
    @PDDLEffect(lambda brush: brush.picked(), True)
    @PDDLEffect(lambda robot: robot.free(), False)
    @PDDLAction
    def pickUpBrush(robot: 'Robot', brush: 'Brush'):
        print(f"Picking up brush {brush.idx}")
        brush.setPicked(True)
        robot.__free = False

    @PDDLPrecondition(lambda dryer, robot:
                      And(Not(dryer.picked()),
                          Not(dryer.turnedOn()),
                          dryer.loaded(),
                          robot.free()))
    @PDDLEffect(lambda dryer: dryer.picked(), True)
    @PDDLEffect(lambda robot: robot.free(), False)
    @PDDLAction
    def pickUpDryer(robot: 'Robot', dryer: 'Dryer'):
        print(f"Picking up dryer {dryer.idx}")
        dryer.setPicked(True)
        robot.__free = False

    @PDDLPrecondition(lambda brush, robot:
                      And(brush.picked(),
                          Not(brush.hasColor()),
                          brush.loaded(),
                          Not(robot.free())))
    @PDDLEffect(lambda brush: brush.picked(), False)
    @PDDLEffect(lambda robot: robot.free(), True)
    @PDDLAction
    def putDownBrush(robot: 'Robot', brush: 'Brush'):
        print(f"Putting down brush {brush.idx}")
        brush.setPicked(False)
        robot.__free = True

    @PDDLPrecondition(lambda dryer, robot:
                      And(
                          dryer.picked(),
                          Not(dryer.turnedOn()),
                          dryer.loaded(),
                          Not(robot.free())))
    @PDDLEffect(lambda dryer: dryer.picked(), False)
    @PDDLEffect(lambda robot: robot.free(), True)
    @PDDLAction
    def putDownDryer(robot: 'Robot', dryer: 'Dryer'):
        print(f"Putting down dryer {dryer.idx}")
        dryer.setPicked(False)
        robot.__free = True