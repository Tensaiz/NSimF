from abc import ABCMeta, abstractmethod
from enum import Enum

__author__ = "Mathijs Maijer"
__email__ = "m.f.maijer@gmail.com"


class ConditionType(Enum):
    STATE = 0
    ADJACENCY = 1
    UTILITY = 2


class Condition(metaclass=ABCMeta):
    """
    Condition base class
    """
    def __init__(self, condition_type, chained_condition=None):
        if not isinstance(condition_type, ConditionType):
            raise ValueError("The provided condition type is not valid")
        self.condition_type = condition_type
        self.chained_condition = chained_condition
        self.validate_condition()

    def validate_condition(self):
        if not isinstance(self.condition_type, ConditionType):
            raise ValueError('Condition type should be a ConditionType enumerated value')
        if self.chained_condition and not issubclass(type(self.chained_condition), Condition):
            raise ValueError('A chained condition must be a Condition subclass')

    @abstractmethod
    def get_valid_nodes(self, nodes, states, adjacency_matrix, utility_matrix=None):
        pass

    @property
    def state(self):
        state = None
        if self.config and self.config.state:
            state = self.config.state
        elif self.state:
            state = self.state
        return state
