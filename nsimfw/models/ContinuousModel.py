from abc import ABCMeta, abstractmethod
from nsimfw.models.Model import Model
import tqdm
import numpy as np
import networkx as nx

__author__ = "Mathijs Maijer"
__email__ = "m.f.maijer@gmail.com"

class ContinuousModel(Model):

    def iteration(self):
        for update in self.updates:
            updatables = update.execute()
            for status, values in updatables.items():
                self.node_states[:, self.state_map[status]] = values
        self.current_iteration += 1
        return self.node_states
