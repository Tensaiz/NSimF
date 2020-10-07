import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

from nsimfw.models.Model import Model

################### MODEL CONFIGURATION ###################

# Network definition
# g = nx.random_geometric_graph(2000, 0.035)
g = nx.random_geometric_graph(200, 0.125)
craving_control_model = Model(g)

################### MODEL SPECIFICATIONS ###################

constants = {
    'q': 0.8,
    'b': 0.5,
    'd': 0.2,
    'h': 0.2,
    'k': 0.25,
    'S+': 0.5,
}
constants['p'] = 2*constants['d']

def initial_v(constants):
    return np.minimum(1, np.maximum(0, craving_control_model.get_state('C') - craving_control_model.get_state('S') - craving_control_model.get_state('E')))

def initial_a(constants):
    return constants['q'] * craving_control_model.get_state('V') + (np.random.poisson(craving_control_model.get_state('lambda'))/7)

initial_state = {
    'C': 0,
    'S': constants['S+'],
    'E': 1,
    'V': initial_v,
    'lambda': 0.5,
    'A': initial_a
}

def update_C(constants):
    c = craving_control_model.get_state('C') + constants['b'] * craving_control_model.get_state('A') * np.minimum(1, 1-craving_control_model.get_state('C')) - constants['d'] * craving_control_model.get_state('C')
    return {'C': c}

def update_S(constants):
    return {'S': craving_control_model.get_state('S') + constants['p'] * np.maximum(0, constants['S+'] - craving_control_model.get_state('S')) - constants['h'] * craving_control_model.get_state('C') - constants['k'] * craving_control_model.get_state('A')}

def update_E(constants):
    # return {'E': craving_control_model.get_state('E') - 0.015}
    e = np.zeros(len(craving_control_model.nodes))
    for i, node in enumerate(craving_control_model.nodes):
        neighbor_addiction = 0
        for neighbor in craving_control_model.get_neighbors(node):
            neighbor_addiction += craving_control_model.get_node_state(neighbor, 'A')
        e[i] = neighbor_addiction / 50
    return {'E': np.maximum(-1.5, craving_control_model.get_state('E') - e)} # Custom calculation

def update_V(constants):
    return {'V': np.minimum(1, np.maximum(0, craving_control_model.get_state('C')-craving_control_model.get_state('S')-craving_control_model.get_state('E')))}

def update_lambda(constants):
    return {'lambda': craving_control_model.get_state('lambda') + 0.01}

def update_A(constants):
    return {'A': constants['q'] * craving_control_model.get_state('V') + np.minimum((np.random.poisson(craving_control_model.get_state('lambda'))/7), constants['q']*(1 - craving_control_model.get_state('V')))}

# Model definition
craving_control_model.constants = constants
craving_control_model.set_states(['C', 'S', 'E', 'V', 'lambda', 'A'])
craving_control_model.add_update(update_C, {'constants': craving_control_model.constants})
craving_control_model.add_update(update_S, {'constants': craving_control_model.constants})
craving_control_model.add_update(update_E, {'constants': craving_control_model.constants})
craving_control_model.add_update(update_V, {'constants': craving_control_model.constants})
craving_control_model.add_update(update_lambda, {'constants': craving_control_model.constants})
craving_control_model.add_update(update_A, {'constants': craving_control_model.constants})
craving_control_model.set_initial_state(initial_state, {'constants': craving_control_model.constants})

################### SIMULATION ###################

# Simulation
iterations = craving_control_model.simulate(100)

################### Custom plot ###################

A = [np.mean(it[:, 5]) for it in iterations]
C = [np.mean(it[:, 0]) for it in iterations]

E = [np.mean(it[:, 2]) for it in iterations]
lmd = [np.mean(it[:, 4]) for it in iterations]

S = [np.mean(it[:, 1]) for it in iterations]
V = [np.mean(it[:, 3]) for it in iterations]

x = np.arange(0, len(iterations))
plt.figure()

plt.subplot(221)
plt.plot(x, E, label='E')
plt.plot(x, lmd, label='lambda')
plt.legend()

plt.subplot(222)
plt.plot(x, A, label='A')
plt.plot(x, C, label='C')
plt.legend()

plt.subplot(223)
plt.plot(x, S, label='S')
plt.plot(x, V, label='V')
plt.legend()

plt.show()

################### VISUALIZATION ###################

visualization_config = {
    'plot_interval': 2,
    'plot_variable': 'A',
    'color_scale': 'RdBu',
    'variable_limits': {
        'A': [0, 0.8],
        'lambda': [0.5, 1.5],
        'C': [-1, 1],
        'V': [-1, 1],
        'E': [-1, 1],
        'S': [-1, 1]
    },
    'show_plot': True,
    # 'plot_output': './animations/c_vs_s.gif',
    'plot_title': 'Self control vs craving simulation',
}

craving_control_model.configure_visualization(visualization_config, iterations)
craving_control_model.visualize('animation')
