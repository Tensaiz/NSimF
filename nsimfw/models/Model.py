from abc import ABCMeta, abstractmethod
import tqdm
import copy
import numpy as np
import networkx as nx

__author__ = "Mathijs Maijer"
__email__ = "m.f.maijer@gmail.com"

class ConfigurationException(Exception):
    """Configuration Exception"""

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

class Model(object, metaclass=ABCMeta):
    """
    Partial Abstract Class defining a model
    """

    def __init__(self, graph, seed=None):
        self.graph = graph
        self.clear()
        np.random.seed(seed)

    @property
    def constants(self):
        return self.__constants

    @constants.setter
    def constants(self, constants):
        self.__constants = constants

    @property
    def nodes(self):
        return list(self.graph.nodes())

    def set_states(self, states):
        self.node_states = np.zeros((len(self.graph.nodes()), len(states)))
        self.state_names = states
        for i, state in enumerate(states):
            self.state_map[state] = i

    def set_initial_state(self, initial_state, arguments={}):
        for state in initial_state.keys():
            val = initial_state[state]
            if hasattr(val, '__call__'):
                self.node_states[:, self.state_map[state]] = val(**arguments)
            else:
                self.node_states[:, self.state_map[state]] = val

    def get_state(self, state):
        return self.node_states[:, self.state_map[state]]

    def add_update(self, fun, args={}, condition=None):
        self.updates.append(Update(fun, args, condition))

    def simulate(self, n, show_tqdm=True):
        simulation_output = []
        if show_tqdm:
            for _ in tqdm.tqdm(range(0, n)):
                iteration_result = self.iteration()
                simulation_output.append(copy.deepcopy(iteration_result))
        else:
            for _ in range(0, n):
                iteration_result = self.iteration()
                simulation_output.append(copy.deepcopy(iteration_result))
        return simulation_output

    @abstractmethod
    def iteration(self):
        pass

    def clear(self):
        self.state_map = {}
        self.state_names = []
        self.node_states = np.array([])
        self.updates = []
        self.current_iteration = 0

    def reset(self):
        self.node_states = np.zeros((len(self.graph.nodes()), len(self.state_names)))
        self.current_iteration = 0
