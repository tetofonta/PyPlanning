from AIROB.domain import PDDLEnvironment


class PDDLPredicate:
    def __init__(self, func, default=False):
        self.func = func
        self.env = PDDLEnvironment.get_instance()
        self.env.add_predicate(func, default)

    def __call__(self, *args,  **kwargs):
        return self.env.predicate(self.func)(*args, **kwargs)


def PDDLPredicateDefault(default):
    def wrap(func):
        return PDDLPredicate(func, default)
    return wrap