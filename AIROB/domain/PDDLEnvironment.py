import uuid
from collections import namedtuple, OrderedDict
from typing import Optional
from .PDDLObject import PDDLObject

from unified_planning import Environment
from unified_planning.model import Object, Fluent, Problem, InstantaneousAction, Variable, Parameter
from unified_planning.plans import ActionInstance
from unified_planning.shortcuts import UserType, BoolType

Action = namedtuple("Action", ["name", "kwargs", "preconditions", "effects", "func"])
Type = namedtuple("Type", ["type", "cls"])


def gen_instance_functions(instance):
    for method_or_attr in dir(instance):
        if method_or_attr.startswith('__') or method_or_attr.endswith('__'):
            continue
        attr = getattr(instance, method_or_attr)
        yield method_or_attr, attr


def get_type_predicates(instance, env):
    data = {}
    for k, v in gen_instance_functions(instance):
        if env.func_name(v) in env.rev_predicates.keys():
            data[k] = v
    return data


def get_type_predicate_descriptors(instance, env):
    data = {}
    for k, v in gen_instance_functions(instance):
        if env.func_name(v) in env.rev_predicates.keys() and not env.predicateHidden(
                env.rev_predicates[env.func_name(v)]):
            data[k] = {"name": k, "params": PDDLEnvironment.root_func(v).__annotations__}
    return data


def get_type_predicate_args(instance, pred, env):
    f = getattr(instance, pred)
    if not env.func_name(f) in env.rev_predicates.keys():
        return {}, 404
    return {k: v for k, v in PDDLEnvironment.root_func(f).__annotations__.items() if k != 'self'}


class PDDLObjectType(Object):
    def __init__(self, instance, type_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance
        self.__predicates = {}
        self.__env = PDDLEnvironment.get_instance()
        self.type_name = type_name
        for k, v in gen_instance_functions(instance.__class__):
            if self.__env.func_name(v) in self.__env.rev_predicates.keys():
                self.__predicates[k] = v

    def __getattr__(self, item):
        if item in self.__predicates:
            return lambda *args, **kwargs: self.__predicates[item](self, *args, **kwargs)
        return getattr(self.instance, item)


class PDDLParameter(Parameter):
    def __init__(self, name: str, typename: Type, *args, **kwargs):
        super().__init__(name, typename.type, *args, **kwargs)
        self.env = PDDLEnvironment.get_instance()
        self.data = get_type_predicates(typename.cls, self.env)

    def __getattr__(self, item):
        return lambda *args, **kwargs: self.data[item](self, *args, **kwargs)


class PDDLActionType(InstantaneousAction):
    def __init__(self,
                 _name: str,
                 _parameters=None,
                 _env: Optional[Environment] = None,
                 **kwargs
                 ):
        super().__init__(_name, OrderedDict(), _env)
        self._parameters = OrderedDict()
        if _parameters is not None:
            assert len(kwargs) == 0
            for n, t in _parameters.items():
                assert self._environment.type_manager.has_type(
                    t.type
                ), "type of parameter does not belong to the same environment of the action"
                self._parameters[n] = PDDLParameter(
                    n, t, self._environment
                )
        else:
            for n, t in kwargs.items():
                assert self._environment.type_manager.has_type(
                    t.type
                ), "type of parameter does not belong to the same environment of the action"
                self._parameters[n] = PDDLParameter(
                    n, t, self._environment
                )


class PDDLEnvironment:
    __PDDL_ENV_INSTANCE = None

    def __init__(self):
        self.objects = {}  # id => (object repr, object instance)
        self.types = {}
        self.hierarchy = {}
        self.predicates = {}
        self.rev_predicates = {}
        self.actions = {}
        self.type_action = {}
        self.predicates_compiled = {}
        self.user_actions = {}

    def get_objects_hierarchy(self, type_str):
        return self.hierarchy[type_str]

    def predicateHidden(self, func):
        return self.predicates[func][4]

    def predicateDerived(self, func):
        return self.predicates[func][1] is None

    @staticmethod
    def get_instance():
        if PDDLEnvironment.__PDDL_ENV_INSTANCE is None:
            PDDLEnvironment.__PDDL_ENV_INSTANCE = PDDLEnvironment()
        return PDDLEnvironment.__PDDL_ENV_INSTANCE

    def set_type(self, typ):
        assert typ.__name__ not in self.types
        father = typ.__mro__[1]
        if father == PDDLObject:
            father = None
        if father is not None:
            assert father.__name__ in self.types
            father = self.types[father.__name__].type

        self.types[typ.__name__] = Type(UserType(typ.__name__, father=father), typ)

    def get_type(self, typ):
        assert typ.__name__ in self.types
        return self.types[typ.__name__].type

    def add_object(self, instance: PDDLObject):
        assert type(instance).__name__ in self.types
        typ = self.types[type(instance).__name__].type
        self.objects[instance.get_id()] = PDDLObjectType(instance, type(instance).__name__, instance.get_id(), typ)
        for t in type(instance).__mro__:
            if t == PDDLObject or t == object:
                break
            if t.__name__ not in self.hierarchy:
                self.hierarchy[t.__name__] = []
            self.hierarchy[t.__name__].append(instance.get_id())
        return self.objects[instance.get_id()]

    @staticmethod
    def root_func(func):
        return func if '__code__' in dir(func) else PDDLEnvironment.root_func(func.func)

    @staticmethod
    def func_name(func):
        rf = PDDLEnvironment.root_func(func)
        if rf is None:
            return None
        return rf.__code__.co_qualname.replace('.', '_')

    def __func_to_params(self, func):
        name = self.func_name(func)
        params = func.__code__.co_varnames[:func.__code__.co_argcount]
        types = func.__annotations__

        kwargs = {}
        for p in params:
            assert p in types
            var_name = p
            if p == 'self':
                var_name = f"_{p}"
            kwargs[var_name] = types[p] if type(types[p]) is str else types[p].__name__

        return name, params, kwargs

    def add_predicate(self, func, default: bool, derived: bool, hidden: bool):
        name, params, kwargs = self.__func_to_params(func)
        self.predicates[func] = (name, BoolType() if not derived else None, kwargs, default, hidden)
        self.rev_predicates[name] = func

    def add_action(self, func, user=False):
        name, params, kwargs = self.__func_to_params(func)
        self.actions[name] = Action(name, kwargs, list(), list(), func)
        if user and name not in self.user_actions:
            self.user_actions[name] = None

    def add_action_message(self, func, action):
        self.user_actions[action] = func

    def add_action_precondition(self, func, precond):
        name = self.func_name(func)
        assert name in self.actions.keys()
        self.actions[name].preconditions.append(precond)

    def add_action_effect(self, func, predicate, value: bool):
        name = self.func_name(func)
        assert name in self.actions.keys()
        self.actions[name].effects.append((predicate, value))

    def __for_all(self, tup, *lists):
        if len(lists) == 0:
            yield tup
        else:
            for o in lists[0]:
                yield from self.__for_all((*tup, o), *lists[1:])

    def get_predicate_fn(self, predicate):
        if 'func' in dir(predicate):
            return self.get_predicate_fn(predicate.func)
        return predicate

    def get_object(self, instance):
        assert isinstance(instance, PDDLObject)
        assert instance.get_id() in self.objects
        return self.objects[instance.get_id()]

    def get_object_by_id(self, id):
        return self.objects[id]

    def get_object_instance(self, instance):
        return self.objects[instance.name].instance

    def execute_action(self, action: ActionInstance):
        self.execute_action_raw(action.action.name, action.actual_parameters)

    def execute_action_raw(self, name, parameters):
        if name not in self.actions:
            return
        act = self.actions[name].func
        parameters = list(map(lambda x: self.objects[str(x)].instance, parameters))
        act(*parameters)

    def user_message(self, action: ActionInstance):
        if action.action.name not in self.user_actions or self.user_actions[action.action.name] is None:
            return "No Message"
        act = self.user_actions[action.action.name]
        parameters = list(map(lambda x: self.objects[str(x)].instance, action.actual_parameters))
        return act(*parameters)

    def serialize_action(self, action: ActionInstance):
        return {"action": action.action.name, "params": list(map(lambda x: str(x), action.actual_parameters))}

    def predicate(self, fn):
        key_or_function = self.rev_predicates[self.func_name(fn)]
        if key_or_function in self.predicates_compiled:
            return self.predicates_compiled[key_or_function]
        else:
            return key_or_function

    def compile_predicates(self):
        self.predicates_compiled = {}
        for k, v in self.predicates.items():
            name, ret, params, default, _ = v
            if ret is None:
                continue
            types = {k: self.types[v].type for k, v in params.items()}
            self.predicates_compiled[k] = Fluent(name, ret, **types)

    def get_current_state(self):
        self.compile_predicates()
        ret = {}
        for k, v in self.predicates.items():
            _, ret, params, default, _ = v
            for values in self.__for_all((), *map(lambda t: self.hierarchy[t], params.values())):
                ret[f"{k}({', '.join(list(map(str, params.values())))})"] = k(
                    *map(lambda x: self.objects[x].instance, values))

    @staticmethod
    def __get_func_params(func, *dicts):
        param_dict = {}
        merged = {}
        for d in dicts:
            merged = merged | d

        for arg_name in func.__code__.co_varnames:
            assert arg_name in merged
            param_dict[arg_name] = merged[arg_name]
        return param_dict

    def problem(self, name=None):
        problem = Problem(name if name is not None else str(uuid.uuid1()))

        for obj in self.objects.values():
            problem.add_object(obj)

        # create predicates
        self.compile_predicates()
        for k, v in self.predicates.items():
            _, ret, params, default, _ = v
            if ret is None:
                continue
            problem.add_fluent(self.predicates_compiled[k], default_initial_value=default)

            for values in self.__for_all((), *map(lambda t: self.hierarchy[t], params.values())):
                problem.set_initial_value(
                    self.predicates_compiled[k](*map(lambda x: self.objects[x], values)),
                    k(*map(lambda x: self.objects[x].instance, values))
                )

        # Actions
        for name, args, pre, post, _ in self.actions.values():
            act = PDDLActionType(name, **{k: self.types[v] for k, v in args.items()})
            params = {k: act.parameter(k) for k, v in args.items()}
            # vars = {f"var_{k}": Variable(k, self.types[v].type) for k, v in args.items()}

            for p in pre:
                act.add_precondition(p(**PDDLEnvironment.__get_func_params(p, {"env": self.get_instance()}, params)))
            for q, v in post:
                act.add_effect(q(**PDDLEnvironment.__get_func_params(q, {"env": self.get_instance()}, params)), v)
            problem.add_action(act)

        return problem

    def var(self, typ):
        assert typ.__name__ in self.types
        return Variable(typ.__name__, self.types[typ.__name__].type)
