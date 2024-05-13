from unified_planning.engines import PlanGenerationResultStatus
from unified_planning.shortcuts import OneshotPlanner, And

from domain.PDDLEnvironment import PDDLEnvironment
from domain.cubeotta.CubeSide import CubeSide

env = PDDLEnvironment.get_instance()

AA = CubeSide(0)
BB = CubeSide(1)
CC = CubeSide(2)
A = env.add_object(AA)
B = env.add_object(BB)
C = env.add_object(CC)

problem = env.problem()
problem.add_goal(And(CubeSide.painted(A), CubeSide.painted(B), CubeSide.painted(C)))
print(problem)

with OneshotPlanner(problem_kind=problem.kind) as planner:
    result = planner.solve(problem)
    if result.status == PlanGenerationResultStatus.SOLVED_SATISFICING:
        print("Pyperplan returned: %s" % result.plan)
        for action in result.plan.actions:
            env.execute_action(action)
        print(AA, BB, CC)
    else:
        print("No plan found.")
