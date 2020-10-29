from abc import ABCMeta
import tqdm
import copy
import numpy as np
import networkx as nx

from nsimf.models.Update import Update
from nsimf.models.Update import UpdateType
from nsimf.models.Update import UpdateConfiguration
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
        self.init()
        self.__dict__.update(iterable, **kwargs)
        self.validate()

    def init(self):
        self.utility = False
        self.save_disk = False
        self.state_memory = 0
        self.save_interval = 0
        self.memory_interval = 1
        self.path = './output/'

    def validate(self):
        pass


class Model(object, metaclass=ABCMeta):
    """
    Partial Abstract Class defining a model
    """

    def __init__(self, graph, config=None, seed=None):
        self.graph = graph
        self.config = config if config else ModelConfiguration()
        self.clear()
        self.init()
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

    def init(self):
        self.update_adjacency()
        if self.config.utility:
            self.initialize_utility()

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

    def initialize_utility(self):
        n_nodes = len(self.graph.nodes())
        self.edge_utility = np.zeros((n_nodes, n_nodes))

    def get_utility(self):
        return self.edge_utility

    def get_nodes_utility(self, nodes):
        return self.edge_utility[nodes]

    def set_initial_utility(self, init_function, params=None):
        params = params if params else {}
        self.edge_utility = init_function(*params)

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

    def add_update(self, fun, args=None, condition=None, get_nodes=False, update_type=None):
        arguments = args if args else {}
        if condition and condition.state:
            condition.set_state_index(self.state_map[condition.state])
        update_type = update_type if update_type else UpdateType.STATE
        update = self.create_update((fun, arguments, condition, get_nodes, update_type))
        self.schemes[0].add_update(update)

    def add_state_update(self, fun, args=None, condition=None, get_nodes=False):
        self.add_update(fun, args, condition, get_nodes, UpdateType.STATE)

    def add_utility_update(self, fun, args=None, condition=None, get_nodes=False):
        if self.config.utility == False:
            raise ValueError('Utility has not been set to true in config')
        self.add_update(fun, args, condition, get_nodes, UpdateType.UTILITY)

    def add_network_update(self, fun, args=None, condition=None, get_nodes=False):
        self.add_update(fun, args, condition, get_nodes, UpdateType.NETWORK)

    def create_update(self, update_content):
        fun, arguments, condition, get_nodes, update_type = update_content
        cfg_options = {
            'arguments': arguments,
            'condition': condition,
            'get_nodes': get_nodes,
            'update_type': update_type
        }
        update_cfg = UpdateConfiguration(cfg_options)
        return Update(fun, update_cfg)

    def add_scheme(self, scheme):
        self.schemes.append(scheme)

    def get_adjacency(self):
        return self.adjacency

    def get_nodes_adjacency(self, nodes):
        return self.adjacency[nodes]

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
        new_utility = copy.deepcopy(self.edge_utility)
        new_adjacency = copy.deepcopy(self.adjacency)
        new_graph = copy.deepcopy(self.graph)
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
                self.assign_update((update, update_nodes, updatables, new_states, new_utility, new_adjacency, new_graph))
        self.node_states = new_states
        self.edge_utility = new_utility
        self.adjacency = new_adjacency
        self.graph = new_graph
        self.calculate_properties()
        self.current_iteration += 1
        return self.node_states

    def assign_update(self, update_info):
        update, update_nodes, updatables, new_states, new_utility, new_adjacency, new_graph = update_info
        if update.update_type == UpdateType.STATE:
            new_states = self.update_state(update_nodes, updatables, new_states)
        elif update.update_type == UpdateType.UTILITY:
            new_utility[update_nodes] = updatables
        elif update.update_type == UpdateType.NETWORK:
            self.update_network(update_nodes, updatables, (new_states, new_utility, new_adjacency, new_graph))

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

    def update_network(self, update_nodes, updatables, model_new_values):
        for network_update_type, change in updatables.items():
            self.assign_network_operation(network_update_type, (change, update_nodes, model_new_values))

    def assign_network_operation(self, network_update_type, network_update_info):
        change, update_nodes, model_new_values = network_update_info
        network_update_type_to_function = {
            'remove': self.network_nodes_remove,
            'add': self.network_nodes_add,
            'edge_change': self.network_edges_change
        }
        network_update_type_to_function[network_update_type](change, update_nodes, model_new_values)

    def network_nodes_remove(self, removable_nodes, update_nodes, model_new_values):
        new_states, new_utility, new_adjacency, new_graph = model_new_values
        new_states[:] = np.delete(new_states, removable_nodes)
        new_utility[:] = np.delete(new_utility, removable_nodes)
        new_graph.remove_nodes_from(removable_nodes)
        new_adjacency[:] = nx.convert_matrix.to_numpy_array(new_graph)

    def network_nodes_add(self, new_nodes_config, update_nodes, model_new_values):
        new_states, new_utility, new_adjacency, new_graph = model_new_values
        n_new_nodes = new_nodes_config['n']
        edges = new_nodes_config['edges']
        initial_states = new_nodes_config['initial_states']
        adjacency = new_nodes_config['adjacency']
        utility = new_nodes_config['utility']

        new_graph.add_nodes_from(range(n_new_nodes))
        # new_graph.add_edges_from(edges)

        # Continue here


    def network_edges_change(self, change, update_nodes, model_new_values):
        _, _, new_adjacency, new_graph = model_new_values
        if new_adjacency.shape == change.shape:
            new_adjacency[:] = change
            new_graph[:] = nx.from_numpy_matrix(new_adjacency)
            return

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
        self.edge_utility = np.array([])

    def reset(self):
        self.node_states = np.zeros((len(self.graph.nodes()), len(self.state_names)))
        self.current_iteration = 0
