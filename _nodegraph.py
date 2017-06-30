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

        self._all_nodes = {}

    # the current Nodz implementation stores the
    # node as tuple, which is not really clear to us
    # why. lets handle node querying bettter by providing
    # some useful properties
    @property
    def nodes_dict(self):
        return self._all_nodes

    @property
    def all_nodes(self):
        return self._all_nodes.items()

    @property
    def all_node_names(self):
        return self._all_nodes.keys()

    @property
    def selected_nodes(self):
        return [_[-1] for _ in self.all_nodes if _[-1].isSelected()]

    @property
    def selected_node_names(self):
        return [_.name for _ in self.selected_nodes if _.isSelected()]

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
    signal_node_plug_created = QtCore.Signal(object)
    signal_node_socket_created = QtCore.Signal(object)

    def __init__(self, parent):
        super(Nodz, self).__init__(parent)

        self.initialize_configuration()
        # monkey patching original configuration
        # this will replace the global variable config
        # directly in the nodz_main scope
        nodz_main.config = self.configuration_data

        self._search_field = SearchField(self)
        self._creation_field = SearchField(self)

    @property
    def search_field(self):
        """ holds the search field widget

        Returns: SearchField

        """
        return self._search_field

    @property
    def creation_field(self):
        """ holds the creation field widgets

        Returns:

        """

        return self._creation_field

    def keyPressEvent(self, event):
        """ overriding the keyPressEvent method

        Args:
            event:

        Returns:

        """

        if event.key() not in self.pressedKeys:
            self.pressedKeys.append(event.key())

        if event.key() == QtCore.Qt.Key_Delete:
            self._deleteSelectedNodes()

        if (event.key() == QtCore.Qt.Key_F and
            event.modifiers() == QtCore.Qt.NoModifier):
            self._focus()

        if (event.key() == QtCore.Qt.Key_S and
            event.modifiers() == QtCore.Qt.NoModifier):
            self._nodeSnap = True

        # show SearchField widget on Tab press
        if event.key() == QtCore.Qt.Key_Tab:
            self.creation_field.open()

        if (event.key() == QtCore.Qt.Key_F and
            event.modifiers() == QtCore.Qt.ControlModifier):
            self.search_field.open()

        # Emit signal.
        self.signal_KeyPressed.emit(event.key())

class Nodegraph(Basegraph):
    """ main Nodegraph that should be accessable without any host application

    """

    def __init__(self, parent=None):
        super(Nodegraph, self).__init__(parent)
        # this can be overriden in subclasses to allow mixing in other classes
        # that are not host agnostic
        self._window = BaseWindow(parent)

        # create the graphingscene
        self._graph = Nodz(self._window)
        self.graph.initialize()

        # to query nodes our own way
        self._all_nodes = self.graph.scene().nodes

        # add the graph to our window
        self.window.central_layout.addWidget(self.graph)

        # set slots
        self.connect_slots()

        # just testing
        self.creation_field.available_items = ["test"]

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

    @property
    def creation_field(self):
        return self.graph.creation_field

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
        # @todo it shall clear the craph without emitting node deleted signals
        self.graph.clearGraph()

    def connect_slots(self):
        """ setup all slots

        Returns:

        """
        self.creation_field.signal_input_accepted.connect(self.on_creation_input_accepted)
        self.search_field.signal_input_accepted.connect(self.on_search_input_accepted)
        self.search_field.signal_opened.connect(self.on_search_field_opened)
        self.graph.signal_host_node_created.connect(self.on_host_node_created)
        self.graph.signal_AttrCreated.connect(self.on_attribute_created)
        self.graph.signal_node_socket_created.connect(self.on_socket_created)
        self.graph.signal_node_plug_created.connect(self.on_plug_created)

    @QtCore.Slot(object)
    def on_creation_input_accepted(self, node_type):
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

    @QtCore.Slot(object)
    def on_search_input_accepted(self, node_name):
        """ selects and focus the node by the given name from the searchfield

        Args:
            node_name: name of an existing node

        Returns:

        """
        if node_name in self.nodes_dict:
            self.nodes_dict[node_name].setSelected(True)
            self.graph._focus()

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

        # create default plug on node
        self.graph.createAttribute(node, socket=False, name="message", dataType="message", index=0)

    @QtCore.Slot(object)
    def on_host_node_deleted(self, node_name):
        pass

    @QtCore.Slot(object)
    def on_search_field_opened(self):
        self.search_field.available_items = self.all_node_names

    @QtCore.Slot(str, int)
    def on_attribute_created(self, node_name, index):
        node = self.nodes_dict[node_name]
        if node.sockets:
            sockets = [socket for socket in node.sockets if node.sockets[socket].index == index]
            if sockets and len(sockets) != 1:
                raise ValueError("Could not find socket to emit signal on creation")
            else:
                socket = sockets[0]
                if socket:
                    self.graph.signal_node_socket_created.emit(socket)
        if node.plugs:
            plugs = [plug for plug in node.plugs if node.plugs[plug].index == index]
            if plugs and len(plugs) != 1:
                raise ValueError("Could not find plug to emit signal on creation")
            else:
                plug = plugs[0]
                if plug:
                    self.graph.signal_node_plug_created.emit(plug)


    @QtCore.Slot(object)
    def on_socket_created(self):
        print "WOHOO SOCKET CREATED"

    @QtCore.Slot(object)
    def on_plug_created(self):
        print "WOHOO PLUG Created"