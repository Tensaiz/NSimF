import unittest

from nsimfw.models.Scheme import Scheme
from nsimfw.models.Update import Update

__author__ = "Mathijs Maijer"
__email__ = "m.f.maijer@gmail.com"

class SchemeTest(unittest.TestCase):
    def test_init(self):
        s = Scheme(lambda x: x, {}, lower_bound=0, upper_bound=10, updates=[])
        self.assertEqual(len(s.__dict__.keys()), 5)

    def test_add_update(self):
        s = Scheme(lambda x: x, {}, lower_bound=0, upper_bound=10, updates=[])
        u = Update(lambda x: x)
        s.add_update(u)
        self.assertEqual(len(s.updates), 1)

    def test_set_bounds(self):
        s = Scheme(lambda x: x, {}, lower_bound=0, upper_bound=10, updates=[])
        s.set_bounds(10, 100)
        self.assertEqual(s.lower_bound, 10)
        self.assertEqual(s.upper_bound, 100)

    def test_sample(self):
        s = Scheme(lambda x: x[:-1], {'x': [1,2,3,4]}, lower_bound=0, upper_bound=10, updates=[])
        self.assertEqual(s.sample(), [1,2,3])

if __name__ == '__main__':
    unittest.main()
