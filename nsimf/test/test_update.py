import unittest

from nsimf.models.Update import Update

__author__ = "Mathijs Maijer"
__email__ = "m.f.maijer@gmail.com"


class UpdateTest(unittest.TestCase):
    def test_init(self):
        u = Update(lambda x: x, {}, None, False)
        self.assertEqual(len(u.__dict__.keys()), 4)

    def test_execute(self):
        u = Update(lambda x: x, {'x': [1, 2, 3]}, None, False)
        self.assertEqual(u.execute(), [1, 2, 3])

        u = Update(lambda x, y: x + y, {'y': [3, 4, 5]}, None, True)
        self.assertEqual(u.execute([1, 2]), [1, 2, 3, 4, 5])
