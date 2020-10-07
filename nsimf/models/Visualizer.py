import os

import numpy as np
import networkx as nx

import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.animation as animation

__author__ = "Mathijs Maijer"
__email__ = "m.f.maijer@gmail.com"


class VisualizationConfigurationException(Exception):
    """Configuration Exception"""


class VisualizationConfiguration(object):
    """
    Configuration for the visualizer
    TODO: Validate attributes
    """
    def __init__(self, iterable=(), **kwargs):
        self.__dict__.update(iterable, **kwargs)
        self.validate()

    def validate(self):
        pass


class Visualizer(object):
    """
    Visualizer class handling animations and plotting
    """
    def __init__(self, config, graph, state_map, model_output):
        self.config = config
        self.graph = graph
        self.state_map = state_map
        self.output = model_output
        self.check_layout()

    def check_layout(self):
        if 'pos' in self.graph.nodes[0].keys():
            return
        if 'layout' in self.config.__dict__:
            if self.config.layout == 'fr':
                import pyintergraph
                Graph = pyintergraph.InterGraph.from_networkx(self.graph)
                G = Graph.to_igraph()
                layout = G.layout_fruchterman_reingold(niter=500)
                positions = \
                    {node: {'pos': location}
                        for node, location in enumerate(layout)}
            else:
                if 'layout_params' in self.config.__dict__:
                    pos = self.config.layout(self.graph,
                                             **self.config.layout_params)
                else:
                    pos = self.config.layout(self.graph)
                positions = {key: {'pos': location}
                             for key, location in pos.items()}
        else:
            pos = nx.drawing.spring_layout(self.graph)
            positions = {key: {'pos': location}
                         for key, location in pos.items()}

        nx.set_node_attributes(self.graph, positions)

    def visualize(self, vis_type):
        visualizations = {
            'animation': self.animation
        }
        visualizations[vis_type]()

    def setup_animation(self):
        state_names = list(self.state_map.keys())
        n_states = len(state_names)

        node_colors = self.get_node_colors()

        fig = plt.figure(figsize=(10, 9), constrained_layout=True)
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
        return state_names, n_states, node_colors, fig, gs, network, axis, n, cm, vmin, vmax, colors

    def animation(self):
        state_names, n_states, node_colors, fig, gs, network, axis, n, cm, vmin, vmax, colors = \
            self.setup_animation()

        def animate(curr):
            index = curr * self.config.plot_interval

            network.clear()
            for i, ax in enumerate(axis):
                ax.clear()
                data = self.output[index][:, i]
                bc = ax.hist(data,
                             range=self.config.variable_limits[state_names[i]],
                             density=1, bins=25, edgecolor='black')[2]
                for j, e in enumerate(bc):
                    e.set_facecolor(colors[j])
                ax.set_title(state_names[i])

            pos = nx.get_node_attributes(self.graph, 'pos')
            nx.draw_networkx_edges(self.graph, pos,
                                   alpha=0.2, ax=network)
            nc = nx.draw_networkx_nodes(self.graph, pos,
                                        nodelist=self.graph.nodes,
                                        node_color=node_colors[curr],
                                        vmin=vmin, vmax=vmax,
                                        cmap=cm, node_size=50,
                                        ax=network)
            nc.set_edgecolor('black')
            network.get_xaxis().set_ticks([])
            network.get_yaxis().set_ticks([])
            network.set_title('Iteration: ' + str(index))

        ani = animation.FuncAnimation(fig, animate, n, interval=200, 
                                      repeat=True, blit=False)

        norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
        sm = plt.cm.ScalarMappable(cmap=cm, norm=norm)
        sm.set_array([])
        fig.colorbar(sm, ax=network)
        fig.suptitle(self.config.plot_title, fontsize=16)

        if self.config.show_plot:
            plt.show()

        if 'plot_output' in self.config.__dict__:
            self.save_plot(ani)

    def save_plot(self, simulation):
        """
        Save the plot to a file,
        specified in plot_output in the visualization configuration
        The file is generated using the writer from the pillow library

        :param simulation: Output of matplotlib animation.FuncAnimation
        """
        print('Saving plot at: ' + self.config.plot_output + ' ...')
        split = self.config.plot_output.split('/')
        file_name = split[-1]
        file_path = self.config.plot_output.replace(file_name, '')
        if not os.path.exists(file_path):
            os.makedirs(file_path)

        from PIL import Image
        writergif = animation.PillowWriter(fps=5)
        simulation.save(self.config.plot_output, writer=writergif)
        print('Saved: ' + self.config.plot_output)

    def get_node_colors(self):
        node_colors = []
        for i in range(len(self.output)):
            if i % self.config.plot_interval == 0:
                node_colors.append(
                    [self.output[i][node, self.state_map[self.config.plot_variable]]
                    for node in self.graph.nodes]
                )
        return node_colors
