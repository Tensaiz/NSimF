import unittest

import numpy as np

from nsimf.models.conditions.StochasticCondition import StochasticCondition
from nsimf.models.conditions.ThresholdCondition import ThresholdCondition
from nsimf.models.conditions.ThresholdCondition import ThresholdOperator
from nsimf.models.conditions.ThresholdCondition import ThresholdConfiguration
from nsimf.models.conditions.Condition import ConditionType

__author__ = "Mathijs Maijer"
__email__ = "m.f.maijer@gmail.com"


class ConditionsTest(unittest.TestCase):
    def test_threshold_condition(self):
        states = np.array([[1, 2, 3], [4, 5, 6], [1, 4, 8]])

        t_cfg = ThresholdConfiguration(ThresholdOperator.GE, 4, 'A')
        t = ThresholdCondition(ConditionType.STATE, t_cfg)
        t.set_state_index(1)
        nodes = t.get_valid_nodes(list(range(3)), states, None, None)

        self.assertEqual(list(nodes), [1, 2])

    def test_stochastic_condition(self):
        np.random.seed(1337)
        states = np.ones((20, 3))

        s = StochasticCondition(ConditionType.STATE, 0.25)
        nodes = s.get_valid_nodes(list(range(len(states))), states, None, None)

        self.assertEqual(list(nodes), [1, 9, 12])

    def test_chained_conditions(self):
        np.random.seed(1337)
        states = np.random.random((100, 3))

        t_cfg = ThresholdConfiguration(ThresholdOperator.GE, 0.5, 'A')
        t = ThresholdCondition(ConditionType.STATE, t_cfg)
        t.set_state_index(1)

        c = StochasticCondition(ConditionType.STATE, 0.25, t)
        nodes = c.get_valid_nodes(list(range(len(states))), states, None, None)

        self.assertEqual(list(nodes), [1,2,3,4,9,11,12,15,17,22])
