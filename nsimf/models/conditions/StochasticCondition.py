import numpy as np

from nsimf.models.conditions.Condition import Condition
from nsimf.models.conditions.Condition import ConditionType

__author__ = "Mathijs Maijer"
__email__ = "m.f.maijer@gmail.com"


class StochasticCondition(Condition):
    def __init__(self, condition_type, p, chained_condition=None):
        super(StochasticCondition, self).__init__(condition_type, chained_condition)
        self.probability = p
        self.validate()

    def validate(self):
        """
        Validate whether the state and threshold are in correct formats
        """
        if not (isinstance(self.probability, int) or isinstance(self.probability, float)):
            raise ValueError('Probability should be an integer or float')

    def get_valid_nodes(self, nodes, states, adjacency_matrix, utility_matrix=None):
        f = self.get_function()
        args = self.get_arguments((nodes, states, adjacency_matrix, utility_matrix))

        selected_nodes = f(*args)

        return selected_nodes \
            if not self.chained_condition \
            else self.chained_condition.get_valid_nodes(selected_nodes, states, adjacency_matrix, utility_matrix)

    def get_function(self):
        condition_type_to_function_map = {
            ConditionType.STATE: self.test_states,
            ConditionType.UTILITY: self.test_utility,
            ConditionType.ADJACENCY: self.test_adjacency
        }
        return condition_type_to_function_map[self.condition_type]

    def get_arguments(self, args):
        condition_type_to_arguments_map = {
            ConditionType.STATE: [
                args[0]
            ],
            ConditionType.UTILITY: [
                args[0],
                args[3]
            ],
            ConditionType.ADJACENCY: [
                args[0],
                args[2]
            ]
        }
        return condition_type_to_arguments_map[self.condition_type]

    def test_states(self, nodes):
        sampled_probabilities = np.random.random(len(nodes))
        return np.where(sampled_probabilities < self.probability)[0]

    def test_utility(self, nodes, utility_matrix):
        pass

    def test_adjacency(self, nodes, adjacency_matrix):
        pass
