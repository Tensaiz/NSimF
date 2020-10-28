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

    def get_arguments(self, model_input):
        nodes, _, adjacency_matrix, utility_matrix = model_input
        condition_type_to_arguments_map = {
            ConditionType.STATE: [
                nodes
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
        return condition_type_to_arguments_map[self.condition_type]

    def test_states(self, nodes):
        sampled_probabilities = np.random.random(len(nodes))
        return np.where(sampled_probabilities < self.probability)[0]

    def test_utility(self, nodes, utility_matrix):
        pass

    def test_adjacency(self, nodes, adjacency_matrix):
        pass
