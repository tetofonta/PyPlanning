import uuid

from unified_planning.model import Object, Fluent, Problem, InstantaneousAction
from unified_planning.plans import ActionInstance
from unified_planning.shortcuts import UserType, BoolType

from domain.PDDLObject import PDDLObject

class PDDLObjectType(Object):
    def __init__(self, instance, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance

class PDDLEnvironment:
    __PDDL_ENV_INSTANCE = None

    def __init__(self):
        self.objects = {}  # id => (object repr, object instance)
        self.types = {}
        self.hierarchy = {}
        self.predicates = {}
        self.rev_predicates = {}
        self.actions = {}
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
            father = self.types[father.__name__]

        self.types[typ.__name__] = UserType(typ.__name__, father=father)

    def get_type(self, typ):
        assert typ.__name__ in self.types
        return self.types[typ.__name__]

    def add_object(self, instance: PDDLObject):
        assert type(instance).__name__ in self.types
        typ = self.types[type(instance).__name__]
        self.objects[instance.get_id()] = PDDLObjectType(instance, instance.get_id(), typ)
        for t in type(instance).__mro__:
            if t == PDDLObject or t == object:
                break
            if t.__name__ not in self.hierarchy:
                self.hierarchy[t.__name__] = []
            self.hierarchy[t.__name__].append(instance.get_id())
        return self.objects[instance.get_id()]

    def __func_name(self, func):
        return func.__code__.co_qualname.replace('.', '_') if '__code__' in dir(func) else self.__func_name(func.func)

    def __func_to_params(self, func):
        name = self.__func_name(func)
        params = func.__code__.co_varnames[:func.__code__.co_argcount]
        types = func.__annotations__

        kwargs = {}
        for p in params:
            assert p in types
            kwargs[f"_{p}"] = types[p] if type(types[p]) is str else types[p].__name__

        return name, params, kwargs

    def add_predicate(self, func, default: bool):
        name, params, kwargs = self.__func_to_params(func)
        self.predicates[func] = (name, BoolType(), kwargs, default)
        self.rev_predicates[name] = func

    def add_action(self, func):
        name, params, kwargs = self.__func_to_params(func)
        self.actions[name] = (name, kwargs, list(), list(), func)

    def add_action_precondition(self, func, precond):
        name = self.__func_name(func)
        assert name in self.actions.keys()
        self.actions[name][2].append(precond)

    def add_action_effect(self, func, predicate, value: bool):
        name = self.__func_name(func)
        assert name in self.actions.keys()
        self.actions[name][3].append((predicate, value))

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
        act = self.actions[action.action.name][4]
        parameters = list(map(lambda x: self.objects[str(x)].instance, action.actual_parameters))
        act(*parameters)

    def predicate(self, fn):
        return self.predicates_compiled[self.rev_predicates[self.__func_name(fn)]]

    def compile_predicates(self):
        self.predicates_compiled = {}
        for k, v in self.predicates.items():
            name, ret, params, default = v
            types = {k: self.types[v] for k, v in params.items()}
            self.predicates_compiled[k] = Fluent(name, ret, **types)

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
            act = InstantaneousAction(name, **{k: self.types[v] for k, v in args.items()})
            params = {k: act.parameter(k) for k in args.keys()}
            for p in pre:
                act.add_precondition(p(**params))
            for q, v in post:
                act.add_effect(q(**params), v)
            problem.add_action(act)

        return problem
