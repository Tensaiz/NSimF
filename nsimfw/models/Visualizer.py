import numpy as np
import networkx as nx

import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.animation as animation

__author__ = "Mathijs Maijer"
__email__ = "m.f.maijer@gmail.com"

class VisualizationConfiguration(object):
    """
    Configuration for the visualizer
    TODO: Validate attributes
    """
    def __init__(self, iterable=(), **kwargs):
        self.__dict__.update(iterable, **kwargs)

class Visualizer(object):
    """
    Visualizer class handling animations and plotting
    """
    def __init__(self, config, graph, state_map, model_output):
        self.config = config
        self.graph = graph
        self.state_map = state_map
        self.output = model_output

    def visualize(self, vis_type):
        visualizations = {
            'animation': self.animation
        }
        visualizations[vis_type]()

    def animation(self):
        state_names = list(self.state_map.keys())
        n_states = len(state_names)

        fig = plt.figure(figsize=(10,9), constrained_layout=True)
        gs = fig.add_gridspec(6, n_states)

        network = fig.add_subplot(gs[:-1, :])

        axis = []

        for i in range(n_states):
            ax = fig.add_subplot(gs[-1, i])
            ax.set_title(state_names[i])
            ax.get_xaxis().set_ticks([])
            ax.get_yaxis().set_ticks([])
            axis.append(ax)

        n = int(len(self.output)/self.config.plot_interval)

        cm = plt.cm.get_cmap(self.config.color_scale)
        vmin = self.config.variable_limits[self.config.plot_variable][0]
        vmax = self.config.variable_limits[self.config.plot_variable][1]
        colors = cm(np.linspace(0, 1, 25))

        def animate(curr):
            for i, ax in enumerate(axis):
                ax.clear()
                data = self.output[curr][:,i]
                # bc = ax.hist(data, 25)[2]
                bc = ax.hist(data, range=self.config.variable_limits[state_names[i]], density=1, bins=25, edgecolor='black')[2]
                for j, e in enumerate(bc):
                    e.set_facecolor(colors[j])
                ax.set_title(state_names[i])
                # ax.get_xaxis().set_ticks([])
                # ax.get_yaxis().set_ticks([])

            network.set_title('Iteration: ' + str(curr * self.config.plot_interval))

        ani = animation.FuncAnimation(fig, animate, n, repeat=True, blit=False)
        plt.show()