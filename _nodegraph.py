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

    def update(self):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError


class Nodz(ConfiguationMixin, nodz_main.Nodz):
    """ This class will let us override or extend behaviour
    for the purpose of better customization

    """

    signal_host_node_created = QtCore.Signal(object, str)

    def __init__(self, parent):
        super(Nodz, self).__init__(parent)

        self.initialize_configuration()
        # monkey patching original configuration
        # this will replace the global variable config
        # directly in the nodz_main scope
        nodz_main.config = self.configuration_data

        self._search_field = SearchField(self)

    @property
    def search_field(self):
        """ holds the search field widget

        Returns: SearchField

        """
        return self._search_field

    def keyPressEvent(self, event):
        """ extending the keyPressEvent

        Args:
            event:

        Returns:

        """
        super(Nodz, self).keyPressEvent(event)

        # show SearchField widget on Tab press
        if event.key() == QtCore.Qt.Key_Tab:
            self.search_field.open()


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
        self.graph.initialize()

        # add the graph to our window
        self.window.central_layout.addWidget(self.graph)

        # set slots
        self.connect_slots()

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
            window: QMainWindow

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
    def configuration(self):
        """ holds the configuration

        Returns: ConfigurationMixin

        """
        return self.graph.configuration

    @property
    def search_field(self):
        return self.graph.search_field

    def open(self, *args, **kwargs):
        """ opens the Nodegraph

        Args:
            *args:
            **kwargs:

        Returns:

        """
        self.window.show(*args, **kwargs)

    def save_configuration(self, filepath):
        """ saves the current configuration in json schema

        Args:
            filepath: path to file

        Returns:

        """
        self.graph.save_configuration(filepath)

    def load_configuration(self, configuration_file):
        """

        Args:
            configuration_file:

        Returns:

        """
        self.graph.load_configuration(configuration_file)
        # @todo update functionality

    def clear(self):
        self.graph.clearGraph()

    @QtCore.Slot(object)
    def on_input_accepted(self, node_type):
        """ creates a NodeItem of given type and emit additional signals

        This will always emit a host_node_created signal, which behaves like
        some kind of callback, but makes it easier for us to modify and
        reuse them.
        Args:
            node_type: type of the node

        Returns:

        """
        # find out if there is a configuration for this node type
        _ = "node_{0}".format(node_type)
        if hasattr(self.graph.configuration, _):
            # and create node with included preset
            node = self.graph.createNode(preset=_)
        else:
            node = self.graph.createNode()
        self.graph.signal_host_node_created.emit(node, node_type)

    def connect_slots(self):
        """ setup all slots

        Returns:

        """
        self.search_field.signal_input_accepted.connect(self.on_input_accepted)
        self.graph.signal_host_node_created.connect(self.on_host_node_created)

    @QtCore.Slot(object)
    def on_host_node_created(self, node, node_type):
        """ allows us to modify the NodeItem when a corresponding host node was created

        Args:
            node: NodeItem
            node_type: original node type of equally host node object

        Returns:

        """
        # we will store the original node type
        setattr(node, "node_type", node_type)