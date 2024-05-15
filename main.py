from unified_planning.engines import PlanGenerationResultStatus
from unified_planning.shortcuts import OneshotPlanner, And

from domain.PDDLEnvironment import PDDLEnvironment
from domain.cubeotta.Cube import Cube

env = PDDLEnvironment.get_instance()

cube1 = env.add_object(Cube(0))
cube2 = env.add_object(Cube(1))

problem = env.problem()
problem.add_goal(And(cube1.instance.painted(), cube2.instance.painted()))
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
