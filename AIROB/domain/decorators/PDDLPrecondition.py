from AIROB.domain import PDDLEnvironment


class __PDDLPrecondition:
    def __init__(self, func, precondition):
        self.func = func
        PDDLEnvironment.get_instance().add_action_precondition(func, precondition)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


def PDDLPrecondition(precond):
    def wrap(func):
        return __PDDLPrecondition(func, precond)

    return wrap
