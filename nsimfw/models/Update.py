class Update(object):
    """
    Update class
    """

    def __init__(self, fun, args={}, condition=None):
        self.function = fun
        self.arguments = args
        self.condition = condition

    def execute(self):
        return self.function(**self.arguments)