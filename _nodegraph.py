import logging
import os

from Qt import (QtWidgets,
                QtCore,
                QtGui
                )

from lib import (BaseWindow,
                 SearchField,
                 ConfiguationMixin
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
    """ main Nodegraph that should be accessable without any host application

    """
    def __init__(self, parent=None):
        super(Nodegraph, self).__init__(parent)

        # this can be overriden in subclasses to allow mixing in other classes
        # that are not host agnoistic
        self._window = BaseWindow(parent)

        # create the graphingscene
        self._graph = Nodz(self._window)
        self._graph.initialize()

        # create the search field widget
        self._search_field = SearchField(self._graph)

        # add the graph to our window
        self.window.central_layout.addWidget(self._graph)

    @property
    def window(self):
        """ holds the Window which serves as parent to all other widgets

        Returns:

        """
        return self._window

    @window.setter
    def window(self, window):
        """ holds the Window which serves as parent to all other widgets

        Args:
            window:

        Returns:

        """
        self._window = window
        self.window.central_layout.addWidget(self.graph)

    @property
    def graph(self):
        """ holds the nodegraph widget

        Returns: Nodz

        """
        return self._graph

    @property
    def search_field(self):
        """ holds the search field widget

        Returns: SearchField

        """
        return self._search_field

    @property
    def configuration(self):
        """ holds the configuration

        Returns: ConfigurationMixin

        """
        return self.graph.configuration

    def open(self, *args, **kwargs):
        self.window.show(*args, **kwargs)

    def save_configuration(self, filepath):
        self.graph.save_configuration(filepath)

    def load_configuration(self, configuration_file):
        self.graph.load_configuration(configuration_file)

    def clear(self):
        self.graph.clearGraph()