import argparse
import json

from unified_planning.engines import PlanGenerationResultStatus
from unified_planning.environment import get_environment
from flask import Flask, request
from unified_planning.shortcuts import Not, And, OneshotPlanner

from AIROB.domain import PDDLEnvironment, get_type_predicates, get_type_predicate_descriptors, get_type_predicate_args

app = Flask(__name__)


@app.route("/api/objects")
def objects():
    return {k: v.type_name for k, v in PDDLEnvironment.get_instance().objects.items()}


@app.route("/api/predicates/<typ>")
def predicates(typ):
    if typ not in PDDLEnvironment.get_instance().types:
        return {}, 404
    typ = PDDLEnvironment.get_instance().types[typ]
    preds = get_type_predicate_descriptors(typ.cls, PDDLEnvironment.get_instance())
    return list(preds.keys())


@app.route("/api/params/<typ>/<pred>")
def predicates_params(typ, pred):
    if typ not in PDDLEnvironment.get_instance().types:
        return {}, 404
    typ = PDDLEnvironment.get_instance().types[typ]
    params = get_type_predicate_args(typ.cls, pred, PDDLEnvironment.get_instance())
    for k, v in params.items():
        params[k] = PDDLEnvironment.get_instance().get_objects_hierarchy(v)
    return params


@app.route("/api/plan", methods=["POST"])
def plan():
    prob = PDDLEnvironment.get_instance().problem("problem")

    goal_predicates = []
    for p in json.loads(request.data.decode()):
        obj = PDDLEnvironment.get_instance().get_object_by_id(p['object'])
        predicate_fn = getattr(obj, p['predicate'])
        raw = predicate_fn(**{k: PDDLEnvironment.get_instance().get_object_by_id(v) for k, v in p['params'].items()})
        goal_predicates.append(
            raw if p['value'] else Not(raw)
        )

    prob.add_goal(And(*goal_predicates))
    actions = []
    with OneshotPlanner(problem_kind=prob.kind) as planner:
        result = planner.solve(prob)
        if result.status == PlanGenerationResultStatus.SOLVED_SATISFICING:
            print("Pyperplan returned: %s" % result.plan)
            for action in result.plan.actions:
                actions.append({
                    "action": action.action.name,
                    "params": list(map(lambda x: str(x), action.actual_parameters)),
                    "user": action.action.name in PDDLEnvironment.get_instance().user_actions,
                    "user_message": PDDLEnvironment.get_instance().user_message(action)
                })
        else:
            print("No plan found.")

    return actions


@app.route("/api/execute/<action>", methods=["POST"])
def execute(action):
    params = json.loads(request.data.decode())
    PDDLEnvironment.get_instance().execute_action_raw(action, params)
    return {}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='AIROB')
    parser.add_argument('-d', '--domain', type=str, required=True, help='Domain package')

    get_environment().credits_stream = None
    args, domain_args = parser.parse_known_args()
    domain = __import__(args.domain)
    domain_parser = domain.args()
    domain_args, _ = domain_parser.parse_known_args(args=domain_args)
    env = domain.create_env(PDDLEnvironment.get_instance(), domain_args)
    app.run(debug=True, host='0.0.0.0', port=5000)
