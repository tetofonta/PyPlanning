from unified_planning.engines import PlanGenerationResultStatus
from unified_planning.environment import get_environment
from unified_planning.shortcuts import OneshotPlanner, And, Not

from domain.PDDLEnvironment import PDDLEnvironment
from domain.cubeotta.Brush import Brush
from domain.cubeotta.Cube import Cube
from domain.cubeotta.Dryer import Dryer
from domain.cubeotta.Robot import Robot

get_environment().credits_stream = None

env = PDDLEnvironment.get_instance()
cube0 = env.add_object(Cube(0))
cube1 = env.add_object(Cube(1))
dryer0 = env.add_object(Dryer(0))
brush0 = env.add_object(Brush(0))
brush1 = env.add_object(Brush(1))
robot = env.add_object(Robot())

problem = env.problem()
problem.add_goal(And(
    cube0.instance.painted(),
    cube1.instance.painted(),
    cube0.instance.dry(),
    Not(dryer0.picked())
))
print(problem)

with OneshotPlanner(problem_kind=problem.kind) as planner:
    result = planner.solve(problem)
    if result.status == PlanGenerationResultStatus.SOLVED_SATISFICING:
        print("Pyperplan returned: %s" % result.plan)
        for action in result.plan.actions:
            env.execute_action(action)
        # print(cube1.isPainted())
        # print(cube2.isPainted())
    else:
        print("No plan found.")
