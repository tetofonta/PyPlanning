from AIROB.domain import PDDLEnvironment


class __PDDLPredicate:
    def __init__(self, func, default=False, hidden=False, derived=False):
        self.func = func
        self.env = PDDLEnvironment.get_instance()
        self.env.add_predicate(func, default, derived, hidden)

    def __call__(self, *args,  **kwargs):
        return self.env.predicate(self.func)(*args, **kwargs)


def PDDLPredicate(default=False, hidden=False, derived=False):
    def wrap(func):
        return __PDDLPredicate(func, default, hidden, derived)
    return wrap