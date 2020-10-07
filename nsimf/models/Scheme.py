__author__ = "Mathijs Maijer"
__email__ = "m.f.maijer@gmail.com"

from typing import Callable, List
from nsimf.models.Update import Update


class Scheme(object):
    def __init__(self, sample_function: Callable, args: dict = {},
                 lower_bound: int = None, upper_bound: int = None,
                 updates: list = []):
        self.sample_function: Callable = sample_function
        self.args: dict = args
        self.lower_bound: int = lower_bound
        self.upper_bound: int = upper_bound
        self.updates: List[Update] = updates

    def add_update(self, update: Update) -> None:
        self.updates.append(update)

    def set_bounds(self, lower: int, upper: int) -> None:
        self.lower_bound = lower
        self.upper_bound = upper

    def sample(self) -> int:
        return self.sample_function(**self.args)
