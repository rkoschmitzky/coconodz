import logging
import os

from Qt import (QtWidgets,
                QtCore,
                QtGui
                )


from lib import (ConfiguationMixin,
                 BaseWindow
                 )

import nodz_main

class Basegraph(object):

    def __init__(self, *args, **kwargs):
        super(Basegraph, self).__init__()

    def reset_configuration(self):
        raise NotImplementedError

    def apply_configuration(self):
        raise NotImplementedError

    def open(self):
        raise NotImplementedError

    def add_network(self, network):
        raise NotImplementedError

    def remove_network(self, network):
        raise NotImplementedError

    def clean_graph(self):
        raise NotImplementedError

    def save_graph(self, filepath):
        raise NotImplementedError

    def load_graph(self, filepath):
        raise NotImplementedError

    def load_configuration(self, configuration_file):
        raise NotImplementedError

    def configuration(self):
        raise NotImplementedError

    def save_configuration(self, filepath):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError


class NodeScene(nodz_main.NodeScene):
    """ This class will let us override or extend behaviour
    for the purpose of better customization

    """

    def __init__(self, parent):
        super(NodeScene, self).__init__(parent)

        pass


class Nodz(ConfiguationMixin, nodz_main.Nodz):
    """ This class will let us override or extend behaviour
    for the purpose of better customization

    """

    def __init__(self, parent):
        super(Nodz, self).__init__(parent)

        self.initialize_configuration()
        # monkey patching original configuration
        # this will replace the global variable config
        # directly in the nodz_main scope
        nodz_main.config = self.configuration_data


class Nodegraph(Basegraph):

    def __init__(self, parent=None):
        super(Nodegraph, self).__init__(parent)

        self._window = BaseWindow(parent)

        # create the graphingscene
        self._graph = Nodz(self._window)

        self._graph.initialize()

        # add the graph to our window
        self.window.central_layout.addWidget(self._graph)

    @property
    def window(self):
        return self._window

    @property
    def graph(self):
        return self._graph

    @property
    def configuration(self):
        return self.graph.configuration

    def open(self):
        self.window.show()

    def save_configuration(self, filepath):
        self.graph.save_configuration(filepath)

    def load_configuration(self, configuration_file):
        self.graph.load_configuration(configuration_file)

    def clear(self):
        self.graph.clearGraph()