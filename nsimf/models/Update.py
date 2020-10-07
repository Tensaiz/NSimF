__author__ = "Mathijs Maijer"
__email__ = "m.f.maijer@gmail.com"


class Update(object):
    """
    Update class
    """

    def __init__(self, fun, args={}, condition=None, get_nodes=False):
        self.function = fun
        self.arguments = args
        self.condition = condition
        self.get_nodes = get_nodes

    def execute(self, nodes=None):
        if self.get_nodes:
            output = self.function(nodes, **self.arguments)
        else:
            output = self.function(**self.arguments)
        return output
