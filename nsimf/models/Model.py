from abc import ABCMeta
import tqdm
import copy
import numpy as np

from nsimf.models.Update import Update
from nsimf.models.Scheme import Scheme
from nsimf.models.Visualizer import VisualizationConfiguration
from nsimf.models.Visualizer import Visualizer

from typing import List

__author__ = "Mathijs Maijer"
__email__ = "m.f.maijer@gmail.com"


class ConfigurationException(Exception):
    """Configuration Exception"""


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

    def get_node_states(self, node):
        return self.node_states[node]

    def get_node_state(self, node, state):
        return self.node_states[node, self.state_map[state]]

    def add_update(self, fun, args={}, condition=None):
        self.schemes[0].add_update(Update(fun, args, condition))

    def add_scheme(self, scheme):
        self.schemes.append(scheme)

    def get_all_neighbors(self):
        neighbors = []
        for node in list(self.graph.nodes()):
            neighbors.append(self.graph.neighbors(node))
        return neighbors

    def get_neighbors(self, node):
        return list(self.graph.neighbors(node))

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

    def iteration(self):
        # For every scheme
        for scheme in self.schemes:
            if scheme.lower_bound and scheme.lower_bound > self.current_iteration:
                continue
            if scheme.upper_bound and scheme.upper_bound <= self.current_iteration:
                continue
            nodes = scheme.sample()
            # For all the updates in the scheme
            for update in scheme.updates:
                if update.get_nodes:
                     updatables = update.execute(nodes)
                else:
                    updatables = update.execute()
                for state, update_output in updatables.items():
                    if isinstance(update_output, list) or isinstance(update_output, np.ndarray):
                        self.node_states[nodes, self.state_map[state]] = update_output
                    elif isinstance(update_output, dict):
                        for node, values in update_output.items():
                            self.node_states[node, self.state_map[state]] = values
        self.current_iteration += 1
        return self.node_states

    def configure_visualization(self, options, output):
        configuration = VisualizationConfiguration(options)
        self.visualizer = Visualizer(configuration, self.graph, self.state_map, output)

    def visualize(self, vis_type):
        self.visualizer.visualize(vis_type)

    def clear(self):
        self.state_map = {}
        self.state_names = []
        self.node_states = np.array([])
        self.schemes: List[Scheme] = [Scheme(lambda graph: graph.nodes, {'graph': self.graph}, lower_bound=0)]
        self.current_iteration = 0

    def reset(self):
        self.node_states = np.zeros((len(self.graph.nodes()), len(self.state_names)))
        self.current_iteration = 0