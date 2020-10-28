import operator
from enum import Enum

import numpy as np

from nsimf.models.conditions.Condition import Condition
from nsimf.models.conditions.Condition import ConditionType

__author__ = "Mathijs Maijer"
__email__ = "m.f.maijer@gmail.com"


class ThresholdOperator(Enum):
    GT = operator.__gt__
    LT = operator.__lt__
    GE = operator.__ge__
    LE = operator.__le__


class ThresholdConfiguration(object):
    def __init__(self, threshold_operator, threshold, state=None):
        self.threshold_operator = threshold_operator
        self.threshold = threshold
        self.state = state
        self.state_index = None
        self.validate()

    def validate(self):
        """
        Validate whether the state and threshold are in correct formats
        """
        if not isinstance(self.threshold_operator, ThresholdOperator):
            raise ValueError('Invalid threshold type')


class ThresholdCondition(Condition):
    def __init__(self, condition_type, config, chained_condition=None):
        super(ThresholdCondition, self).__init__(condition_type, chained_condition)
        self.config = config
        self.validate()

    def validate(self):
        """
        Validate whether the state and threshold are in correct formats
        """
        if not isinstance(self.config, ThresholdConfiguration):
            raise ValueError('Configuration object should be of class ThresholdConfiguration')
        if self.condition_type == ConditionType.STATE and not self.config.state:
            raise ValueError('A state should be provided when using state type')

    def set_state_index(self, index):
        self.config.state_index = index

    def get_valid_nodes(self, nodes, states, adjacency_matrix, utility_matrix=None):
        condition_type_to_function_map = {
            ConditionType.STATE: self.test_states,
            ConditionType.UTILITY: self.test_utility,
            ConditionType.ADJACENCY: self.test_adjacency
        }
        condition_type_to_arguments_map = {
            ConditionType.STATE: [
                nodes,
                states
            ],
            ConditionType.UTILITY: [
                nodes,
                utility_matrix
            ],
            ConditionType.ADJACENCY: [
                nodes,
                adjacency_matrix
            ]
        }
        selected_nodes = \
            condition_type_to_function_map[self.condition_type](*condition_type_to_arguments_map[self.condition_type])

        return selected_nodes \
            if not self.chained_condition \
            else self.chained_condition.get_valid_nodes(selected_nodes, states, adjacency_matrix, utility_matrix)

    def test_states(self, nodes, states):
        if not self.config.state_index:
            raise ValueError('State index has not been set')
        return np.where(self.config.threshold_operator.value(states[nodes, self.config.state_index], self.config.threshold))[0]

    def test_utility(self, nodes, utility_matrix):
        pass

    def test_adjacency(self, nodes, adjacency_matrix):
        pass
