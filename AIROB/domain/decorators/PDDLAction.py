from AIROB.domain import PDDLEnvironment


class __PDDLAction:
    def __init__(self, func, user):
        self.func = func
        self.env = PDDLEnvironment.get_instance()
        self.env.add_action(func, user)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


def PDDLAction(user=False):
    def wrap(func):
        return __PDDLAction(func, user)
    return wrap


class __PDDLActionMessage:
    def __init__(self, func, action):
        self.func = func
        self.env = PDDLEnvironment.get_instance()
        self.env.add_action_message(func, action)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


def PDDLActionMessage(action):
    def wrap(func):
        return __PDDLActionMessage(func, action)
    return wrap
