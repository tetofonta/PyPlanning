import std_msgs.msg
from unified_planning.shortcuts import Not, And
from AIROB.domain import PDDLObject
from AIROB.domain.decorators import PDDLEffect, PDDLPrecondition, PDDLPredicate, PDDLType, PDDLAction
import rospy


@PDDLType
class Robot(PDDLObject):
    def __init__(self):
        super().__init__()
        self.free = True
        # self.free_sub = rospy.Subscriber("cobotta_free", std_msgs.msg.Bool, self.on_cobotta_free)
        # self.pub = rospy.Publisher('pub', std_msgs.msg.String, queue_size=10)

    def get_id(self) -> str:
        return "Cobotta"

    def on_cobotta_free(self, msg):
        self.free = msg

    @PDDLPredicate()
    def free(self: 'Robot'):
        return self.free

    @PDDLPrecondition(lambda brush, robot:
                      And(Not(brush.picked()),
                          Not(brush.hasColor()),
                          brush.loaded(),
                          robot.free()))
    @PDDLEffect(lambda brush: brush.picked(), True)
    @PDDLEffect(lambda robot: robot.free(), False)
    @PDDLAction()
    def pickUpBrush(robot: 'Robot', brush: 'Brush'):
        print(f"Picking up brush {brush.idx}")
        brush.setPicked(True)
        robot.free = False
        # robot.pub.publish(brush.idx)

    @PDDLPrecondition(lambda dryer, robot:
                      And(Not(dryer.picked()),
                          Not(dryer.turnedOn()),
                          dryer.loaded(),
                          robot.free()))
    @PDDLEffect(lambda dryer: dryer.picked(), True)
    @PDDLEffect(lambda robot: robot.free(), False)
    @PDDLAction()
    def pickUpDryer(robot: 'Robot', dryer: 'Dryer'):
        print(f"Picking up dryer {dryer.idx}")
        dryer.setPicked(True)
        robot.free = False

    @PDDLPrecondition(lambda brush, robot:
                      And(brush.picked(),
                          Not(brush.hasColor()),
                          brush.loaded(),
                          Not(robot.free())))
    @PDDLEffect(lambda brush: brush.picked(), False)
    @PDDLEffect(lambda robot: robot.free(), True)
    @PDDLAction()
    def putDownBrush(robot: 'Robot', brush: 'Brush'):
        print(f"Putting down brush {brush.idx}")
        brush.setPicked(False)
        robot.free = True

    @PDDLPrecondition(lambda dryer, robot:
                      And(
                          dryer.picked(),
                          Not(dryer.turnedOn()),
                          dryer.loaded(),
                          Not(robot.free())))
    @PDDLEffect(lambda dryer: dryer.picked(), False)
    @PDDLEffect(lambda robot: robot.free(), True)
    @PDDLAction()
    def putDownDryer(robot: 'Robot', dryer: 'Dryer'):
        print(f"Putting down dryer {dryer.idx}")
        dryer.setPicked(False)
        robot.free = True
