from AIROB.domain import PDDLEnvironment


class __PDDLEffect:
    def __init__(self, func, effect, value):
        self.func = func
        PDDLEnvironment.get_instance().add_action_effect(func, effect, value)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


def PDDLEffect(effect, value):
    def wrap(func):
        return __PDDLEffect(func, effect, value)

    return wrap
