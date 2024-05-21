import uuid
from collections import namedtuple, OrderedDict
from typing import Optional

from unified_planning import Environment
import unified_planning as up
from unified_planning.model import Object, Fluent, Problem, InstantaneousAction, Variable, Parameter
from unified_planning.plans import ActionInstance
from unified_planning.shortcuts import UserType, BoolType

from domain.PDDLObject import PDDLObject

Action = namedtuple("Action", ["name", "kwargs", "preconditions", "effects", "func"])
Type = namedtuple("Type", ["type", "cls"])


def gen_instance_functions(instance):
    for method_or_attr in dir(instance):
        if method_or_attr.startswith('__') or method_or_attr.endswith('__'):
            continue
        attr = getattr(instance, method_or_attr)
        yield method_or_attr, attr


def get_instance_predicates(instance, env):
    data = {}
    for k, v in gen_instance_functions(instance):
        if env.func_name(v) in env.rev_predicates.keys():
            data[k] = v
    return data


class PDDLObjectType(Object):
    def __init__(self, instance, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance
        self.data = {}
        for k, v in gen_instance_functions(instance):
            self.data[k] = v

    def __getattr__(self, item):
        return lambda *args, **kwargs: self.data[item](self, *args, **kwargs)


class PDDLParameter(Parameter):
    def __init__(self, name: str, typename: Type, *args, **kwargs):
        super().__init__(name, typename.type, *args, **kwargs)
        self.env = PDDLEnvironment.get_instance()
        self.data = get_instance_predicates(typename.cls, self.env)

    def __getattr__(self, item):
        return lambda *args, **kwargs: self.data[item](self, *args, **kwargs)


class PDDLAction(InstantaneousAction):
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
        self.objects[instance.get_id()] = PDDLObjectType(instance, instance.get_id(), typ)
        for t in type(instance).__mro__:
            if t == PDDLObject or t == object:
                break
            if t.__name__ not in self.hierarchy:
                self.hierarchy[t.__name__] = []
            self.hierarchy[t.__name__].append(instance.get_id())
        return self.objects[instance.get_id()]

    @staticmethod
    def __root_func(func):
        return func if '__code__' in dir(func) else PDDLEnvironment.__root_func(func.func)

    @staticmethod
    def func_name(func):
        rf = PDDLEnvironment.__root_func(func)
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

    def add_predicate(self, func, default: bool):
        name, params, kwargs = self.__func_to_params(func)
        self.predicates[func] = (name, BoolType(), kwargs, default)
        self.rev_predicates[name] = func

    def add_action(self, func):
        name, params, kwargs = self.__func_to_params(func)
        self.actions[name] = Action(name, kwargs, list(), list(), func)

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

    def get_object_instance(self, instance):
        return self.objects[instance.name].instance

    def execute_action(self, action: ActionInstance):
        act = self.actions[action.action.name].func
        parameters = list(map(lambda x: self.objects[str(x)].instance, action.actual_parameters))
        act(*parameters)

    def predicate(self, fn):
        return self.predicates_compiled[self.rev_predicates[self.func_name(fn)]]

    def compile_predicates(self):
        self.predicates_compiled = {}
        for k, v in self.predicates.items():
            name, ret, params, default = v
            types = {k: self.types[v].type for k, v in params.items()}
            self.predicates_compiled[k] = Fluent(name, ret, **types)

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
            _, _, params, default = v
            problem.add_fluent(self.predicates_compiled[k], default_initial_value=default)

            for values in self.__for_all((), *map(lambda t: self.hierarchy[t], params.values())):
                problem.set_initial_value(
                    self.predicates_compiled[k](*map(lambda x: self.objects[x], values)),
                    k(*map(lambda x: self.objects[x].instance, values))
                )

        # Actions
        for name, args, pre, post, _ in self.actions.values():
            act = PDDLAction(name, **{k: self.types[v] for k, v in args.items()})
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

