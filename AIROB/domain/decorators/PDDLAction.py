from AIROB.domain import PDDLEnvironment


class PDDLAction:
    def __init__(self, func):
        self.func = func
        self.env = PDDLEnvironment.get_instance()
        self.env.add_action(func)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


