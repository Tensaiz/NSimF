import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

from nsimfw.models.Model import Model
from nsimfw.models.Scheme import Scheme
from nsimfw.models.Update import Update

################### MODEL SPECIFICATIONS ###################

n = 400

# Network definition
g = nx.watts_strogatz_graph(n, 2, 0.02)
HIOM = Model(g)

constants = {
    'dt': 0.01,
    'A_min': -0.5,
    'A_star': 1,
    's_O': 0.01,
    's_I': 0,
    'd_A': 0,
    'p': 1,
    'r_min': 0,
    't_O': np.inf,
    'N': n
}

def initial_I(constants):
    return np.random.normal(0, 0.3, constants['N'])

def initial_O(constants):
    return np.random.normal(0, 0.2, constants['N'])

initial_state = {
    'I': initial_I,
    'O': initial_O,
    'A': 1
}

def update_I_A(nodes, constants):
    node = nodes[0]
    nb = np.random.choice(HIOM.get_neighbors(node))
    if abs(HIOM.get_node_state(node, 'O') - HIOM.get_node_state(nb, 'O')) > constants['t_O']:
        return {'I': HIOM.get_node_state(node, 'I')}
    else:
        # Update information
        r = constants['r_min'] + (1 - constants['r_min']) / (1 + np.exp(-1 * constants['p'] * (HIOM.get_node_state(node, 'O') - HIOM.get_node_state(nb, 'O'))))
        inf = r * HIOM.get_node_state(node, 'I') + (1-r) * HIOM.get_node_state(nb, 'I') + np.random.normal(0, constants['s_I'])

        # Update attention
        node_A = HIOM.get_node_state(node, 'A') + constants['d_A'] * (2 * constants['A_star'] - HIOM.get_node_state(node, 'A'))
        nb_A = HIOM.get_node_state(nb, 'A') + constants['d_A'] * (2 * constants['A_star'] - HIOM.get_node_state(nb, 'A'))
        return {'I': [inf], 'A': {node: node_A, nb: nb_A}}
    return

def update_A(constants):
    return {'A': HIOM.get_state('A') - 2 * constants['d_A'] * HIOM.get_state('A')/constants['N']}

def update_O(constants):
    noise = np.random.normal(0, constants['s_O'], constants['N'])
    x = HIOM.get_state('O') - constants['dt'] * (HIOM.get_state('O')**3 - (HIOM.get_state('A') + constants['A_min']) * HIOM.get_state('O') - HIOM.get_state('I')) + noise
    return {'O': x}

def shrink_I():
    return {'I': HIOM.get_state('I') * 0.999}

def shrink_A():
    return {'A': HIOM.get_state('A') * 0.999}

def sample_attention_weighted(graph):
    probs = []
    A = HIOM.get_state('A')
    factor = 1.0/sum(A)
    for a in A:
        probs.append(a * factor)
    return np.random.choice(graph.nodes, size=1, replace=False, p=probs)

# Model definition
HIOM.constants = constants
HIOM.set_states(['I', 'A', 'O'])

up_I_A = Update(update_I_A, {'constants': HIOM.constants}, get_nodes=True)
up_A = Update(update_A, {'constants': HIOM.constants})
up_O = Update(update_O, {'constants': HIOM.constants})
s_I = Update(shrink_I)
s_A = Update(shrink_A)

HIOM.add_scheme(Scheme(sample_attention_weighted, {'graph': HIOM.graph}, updates=[up_I_A]))
HIOM.add_scheme(Scheme(lambda graph: graph.nodes, {'graph': HIOM.graph}, lower_bound=5000, updates=[s_I]))
HIOM.add_scheme(Scheme(lambda graph: graph.nodes, {'graph': HIOM.graph}, lower_bound=10000, updates=[s_A]))
HIOM.add_update(update_A, {'constants': HIOM.constants})
HIOM.add_update(update_O, {'constants': HIOM.constants})

HIOM.set_initial_state(initial_state, {'constants': HIOM.constants})

################### SIMULATION ###################

iterations = HIOM.simulate(15000)

################### VISUALIZATION ###################

# Visualization config
visualization_config = {
    'layout': 'fr',
    'plot_interval': 100,
    'plot_variable': 'O',
    'variable_limits': {
        'A': [0, 1],
        'O': [-1, 1],
        'I': [-1, 1]
    },
    'cmin': -1,
    'cmax': 1,
    'color_scale': 'RdBu',
    'show_plot': True,
    # 'plot_output': '../animations/HIOM.gif',
    'plot_title': 'HIERARCHICAL ISING OPINION MODEL',
}

HIOM.configure_visualization(visualization_config, iterations)
HIOM.visualize('animation')
