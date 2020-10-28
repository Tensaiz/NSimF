from abc import ABCMeta
import tqdm
import copy
import numpy as np
import networkx as nx

from nsimf.models.Update import Update
from nsimf.models.Scheme import Scheme
from nsimf.models.Visualizer import VisualizationConfiguration
from nsimf.models.Visualizer import Visualizer

from typing import List

__author__ = "Mathijs Maijer"
__email__ = "m.f.maijer@gmail.com"


class ConfigurationException(Exception):
    """Configuration Exception"""


class ModelConfiguration(object):
    """
    Configuration for the visualizer
    TODO: Validate attributes
    """
    def __init__(self, iterable=(), **kwargs):
        self.__dict__.update(iterable, **kwargs)
        self.validate()

    def validate(self):
        pass


class Model(object, metaclass=ABCMeta):
    """
    Partial Abstract Class defining a model
    """

    def __init__(self, graph, config=None, seed=None):
        self.graph = graph
        self.config = config
        self.update_adjacency()
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

    def add_property_function(self, fun):
        self.property_functions.append(fun)

    def set_states(self, states):
        self.node_states = np.zeros((len(self.graph.nodes()), len(states)))
        self.state_names = states
        for i, state in enumerate(states):
            self.state_map[state] = i

    def set_initial_state(self, initial_state, args=None):
        arguments = args if args else {}
        for state in initial_state.keys():
            val = initial_state[state]
            if hasattr(val, '__call__'):
                self.node_states[:, self.state_map[state]] = val(**arguments)
            else:
                self.node_states[:, self.state_map[state]] = val

    def get_state_index(self, state):
        return self.state_map[state]

    def get_state(self, state):
        return self.node_states[:, self.state_map[state]]

    def get_node_states(self, node):
        return self.node_states[node]

    def get_node_state(self, node, state):
        return self.node_states[node, self.state_map[state]]

    def get_nodes_state(self, nodes, state):
        return self.node_states[nodes, self.state_map[state]]

    def get_nodes_states(self):
        return self.node_states

    def get_previous_nodes_states(self, n):
        """
        Get all the nodes' states from the n'th previous saved iteration
        """
        return self.simulation_output[-n - 1]

    def add_update(self, fun, args=None, condition=None, get_nodes=False):
        arguments = args if args else {}
        if condition and condition.state:
            condition.set_state_index(self.state_map[condition.state])
        update = Update(fun, arguments, condition, get_nodes)
        self.schemes[0].add_update(update)

    def add_scheme(self, scheme):
        self.schemes.append(scheme)

    def get_adjacency(self):
        return self.adjacency

    def update_adjacency(self):
        self.adjacency = nx.convert_matrix.to_numpy_array(self.graph)

    def get_all_neighbors(self):
        neighbors = []
        for node in list(self.graph.nodes()):
            neighbors.append(self.get_neighbors(node))
        return neighbors

    def get_neighbors(self, node):
        return list(self.graph.neighbors(node))

    def simulate(self, n, show_tqdm=True):
        self.simulation_output = []
        if self.config.save_disk:
            with open(self.config.path, 'w') as f:
                f.write('# Output array shape:\n#({0}, {1}, {2})\n'.format(int(n / self.config.save_interval), len(self.nodes), len(self.state_names)))
                self.simulation_steps(n, show_tqdm, f)
        else:
            self.simulation_steps(n, show_tqdm)
        return self.simulation_output

    def simulation_steps(self, n, show_tqdm, f=None):
        if show_tqdm:
            for _ in tqdm.tqdm(range(0, n)):
                self.simulation_step(f)
        else:
            for _ in range(0, n):
                self.simulation_step(f)

    def simulation_step(self, f):
        iteration_result = self.iteration()
        if f and self.current_iteration % self.config.save_interval == 0:
            np.savetxt(f, iteration_result)
            f.write('# Iteration {0}\n'.format(self.current_iteration))
        if self.config.state_memory != -1 and self.current_iteration % self.config.memory_interval == 0:
            self.simulation_output.append(copy.deepcopy(iteration_result))
        if self.config.state_memory > 0 and len(self.simulation_output) > self.config.state_memory:
            self.simulation_output = []

    def iteration(self):
        new_states = copy.deepcopy(self.node_states)
        # For every scheme
        for scheme in self.schemes:
            if self.inactive_scheme(scheme):
                continue
            scheme_nodes = scheme.sample()
            # For all the updates in the scheme
            for update in scheme.updates:
                update_nodes = self.valid_update_condition_nodes(update, scheme_nodes)
                if (len(update_nodes) == 0):
                    continue
                if update.get_nodes:
                    updatables = update.execute(update_nodes)
                else:
                    updatables = update.execute()
                new_states = self.update_state(update_nodes, updatables, new_states)
        self.node_states = new_states
        self.calculate_properties()
        self.current_iteration += 1
        return self.node_states

    def valid_update_condition_nodes(self, update, scheme_nodes):
        if not update.condition:
            return scheme_nodes
        return update.condition.get_valid_nodes((scheme_nodes, self.node_states, self.adjacency, None))

    def calculate_properties(self):
        for prop in self.property_functions:
            if self.current_iteration % prop.iteration_interval == 0:
                property_outputs = self.properties.get(prop.name, [])
                property_outputs.append(prop.execute())
                self.properties[prop.name] = property_outputs

    def get_properties(self):
        return self.properties

    def update_state(self, nodes, updatables, node_states):
        for state, update_output in updatables.items():
            if isinstance(update_output, list) or isinstance(update_output, np.ndarray):
                node_states[nodes, self.state_map[state]] = update_output
            elif isinstance(update_output, dict):
                # Add a 2d array implementation instead of for loop
                for node, values in update_output.items():
                    node_states[node, self.state_map[state]] = values
        return node_states

    def inactive_scheme(self, scheme):
        if scheme.lower_bound and scheme.lower_bound > self.current_iteration:
            return True
        elif scheme.upper_bound and scheme.upper_bound <= self.current_iteration:
            return True
        return False

    def configure_visualization(self, options, output):
        configuration = VisualizationConfiguration(options)
        self.visualizer = Visualizer(configuration, self.graph, self.state_map, output)

    def visualize(self, vis_type):
        self.visualizer.visualize(vis_type)

    def clear(self):
        self.state_map = {}
        self.state_names = []
        self.node_states = np.array([])
        self.property_functions = []
        self.properties = {}
        self.schemes: List[Scheme] = [Scheme(lambda graph: graph.nodes, {'graph': self.graph}, lower_bound=0)]
        self.current_iteration = 0

    def reset(self):
        self.node_states = np.zeros((len(self.graph.nodes()), len(self.state_names)))
        self.current_iteration = 0
