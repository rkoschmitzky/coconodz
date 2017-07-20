import logging
import os

from Qt import (QtWidgets,
                QtCore,
                QtGui
                )

import nodz_main

import lib
reload(lib)

from lib import (BaseWindow,
                 GraphContext,
                 SearchField,
                 AttributeContext,
                 ConfiguationMixin,
                 )
from events import Events


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


class NodeItem(nodz_main.NodeItem):

    signal_context_request = QtCore.Signal(object)

    def __init__(self, name, alternate, preset, config):
        super(NodeItem, self).__init__(name, alternate, preset, config)

        self._node_type = None
        self._plugs_dict = {}
        self._sockets_dict = {}

    @property
    def node_type(self):
        return self._node_type

    @node_type.setter
    def node_type(self, value):
        assert isinstance(value, basestring)
        self._node_type = value

    @property
    def plugs_dict(self):
        return self._plugs_dict

    @plugs_dict.setter
    def plugs_dict(self, plugs_dict):
        assert isinstance(plugs_dict, dict)
        self._plugs_dict = plugs_dict

    @property
    def sockets_dict(self):
        return self._sockets_dict

    @sockets_dict.setter
    def sockets_dict(self, sockets_dict):
        assert isinstance(sockets_dict, dict)
        self._sockets_dict = sockets_dict

    def mousePressEvent(self, event):
        if (event.button() == QtCore.Qt.RightButton and
            event.modifiers() == QtCore.Qt.ControlModifier):
            self.signal_context_request.emit(self)
        else:
            super(NodeItem, self).mouseMoveEvent(event)


class Nodz(ConfiguationMixin, nodz_main.Nodz):
    """ This class will let us override or extend behaviour
    for the purpose of better customization

    """

    signal_host_node_created = QtCore.Signal(object, str)
    signal_node_plug_created = QtCore.Signal(object)
    signal_node_socket_created = QtCore.Signal(object)
    signal_context_request = QtCore.Signal(object)
    signal_creation_field_request = QtCore.Signal()
    signal_search_field_request = QtCore.Signal()

    def __init__(self, parent):
        super(Nodz, self).__init__(parent)

        self.initialize_configuration()
        self.config = self.configuration_data

        self._search_field = SearchField(self)
        self._creation_field = SearchField(self)
        self._context = GraphContext(self)
        self._attribute_context = AttributeContext(self)

    @property
    def search_field(self):
        """ holds the search field widget

        Returns: SearchField instance

        """
        return self._search_field

    @property
    def creation_field(self):
        """ holds the creation field widgets

        Returns: SearchField instance

        """

        return self._creation_field

    @property
    def context(self):
        """ holds the creation field widgets

        Returns: GraphContext instance

        """

        return self._context

    @property
    def attribute_context(self):
        """ holds the attribute field widgets

        Returns: AttributeContext instance

        """

        return self._attribute_context

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
        if event.key() == QtCore.Qt.Key_Tab:
            self.signal_creation_field_request.emit()
        if (event.key() == QtCore.Qt.Key_F and
            event.modifiers() == QtCore.Qt.ControlModifier):
            self.signal_search_field_request.emit()

        # Emit signal.
        self.signal_KeyPressed.emit(event.key())

    def mousePressEvent(self, event):
        """ extending the mousePressEvent

        Args:
            event:

        Returns:

        """

        if (event.button() == QtCore.Qt.RightButton and
            event.modifiers() == QtCore.Qt.NoModifier):
            self.signal_context_request.emit(self)

        super(Nodz, self).mousePressEvent(event)

    def createNode(self, name='default', preset='node_default', position=None, alternate=True):
        """ overriding createNode method

        Args:
            name:
            preset:
            position:
            alternate:

        Returns:

        """
        nodeItem = NodeItem(name=name, alternate=alternate, preset=preset,
                            config=self.configuration_data)
        nodeItem.signal_context_request.connect(self.on_context_request)
        # Store node in scene.
        self.scene().nodes[name] = nodeItem

        if not position:
            # Get the center of the view.
            position = self.mapToScene(self.viewport().rect().center())

        # Set node position.
        self.scene().addItem(nodeItem)
        nodeItem.setPos(position - nodeItem.nodeCenter)

        # Emit signal.
        self.signal_NodeCreated.emit(name)

        return nodeItem

    def on_context_request(self, node_item):
        """ placeholder method, has to be overriden in Nodegraphclass

        Args:
            node_item:

        Returns:

        """
        pass


class Nodegraph(Basegraph):
    """ main Nodegraph that should be accessable without any host application

    """

    def __init__(self, parent=None, creation_items=[]):
        super(Nodegraph, self).__init__(parent=parent)
        # this can be overriden in subclasses to allow mixing in other classes
        # that are not host agnostic
        self._window = BaseWindow(parent)
        self._events = Events()

        # create the graphingscene
        self._graph = Nodz(self._window)
        self.graph.initialize()

        # to query nodes our own way
        self._all_nodes = self.graph.scene().nodes

        # add the graph to our window
        self.window.central_layout.addWidget(self.graph)

        # set slots
        self.register_events()

        # just testing
        if creation_items:
            self.creation_field.available_items = creation_items

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
            window: QMainWindow instance

        Returns:

        """
        self._window = window
        self.window.central_layout.addWidget(self.graph)

    @property
    def graph(self):
        """ holds the nodegraph widget

        Returns: Nodz instance

        """
        return self._graph

    @property
    def configuration(self):
        """ holds the configuration

        Returns: ConfigurationMixin instance

        """
        return self.graph.configuration

    @property
    def events(self):
        """ holds the events

        Returns: Events instance

        """
        return self._events

    @property
    def search_field(self):
        """ holds the search field widget

        Returns: SearchField instance

        """
        return self.graph.search_field

    @property
    def creation_field(self):
        """ holds the creation field widget

        Returns: SearchField instance

        """
        return self.graph.creation_field

    @property
    def context(self):
        """ holds the graph context widget

        Returns: GraphContext instance

        """
        return self.graph.context

    @property
    def attribute_context(self):
        """ holds the attribute field widget

        Returns: SearchField instance

        """
        return self.graph.attribute_context

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

    def _connect_slot(self, signal, slot):
        signal.connect(slot)

    def _disconnect_slot(self, signal, slot):
        signal.disconnect(slot)

    def register_events(self):
        """ setup all slots

        Returns:

        """
        # patching per node slot
        self.graph.on_context_request = self.on_context_request

        self.events.add_event("creation_field_request",
                              adder=self._connect_slot,
                              adder_args=(self.graph.signal_creation_field_request,
                                          self.on_creation_field_request
                                          ),
                              remover=self._disconnect_slot,
                              remover_args=(self.graph.signal_creation_field_request,
                                            self.on_creation_field_request
                                            )
                              )
        self.events.add_event("creation_field_input_accepted",
                              adder=self._connect_slot,
                              adder_args=(self.creation_field.signal_input_accepted,
                                          self.on_creation_input_accepted
                                          ),
                              remover=self._disconnect_slot,
                              remover_args=(self.creation_field.signal_input_accepted,
                                            self.on_creation_input_accepted
                                            )
                              )
        self.events.add_event("search_field_request",
                              adder=self._connect_slot,
                              adder_args=(self.graph.signal_search_field_request,
                                          self.on_search_field_request
                                          ),
                              remover=self._disconnect_slot,
                              remover_args=(self.graph.signal_search_field_request,
                                            self.on_search_field_request
                                            )
                              )
        self.events.add_event("search_field_input_accepted",
                              adder=self._connect_slot,
                              adder_args=(self.search_field.signal_input_accepted,
                                          self.on_search_input_accepted
                                          ),
                              remover=self._connect_slot,
                              remover_args=(self.search_field.signal_input_accepted,
                                            self.on_search_input_accepted
                                            )
                              )
        self.events.add_event("search_field_opened",
                              adder=self._connect_slot,
                              adder_args=(self.search_field.signal_opened,
                                          self.on_search_field_opened
                                          ),
                              remover=self._disconnect_slot,
                              remover_args=(self.search_field.signal_opened,
                                            self.on_search_field_opened
                                            )
                              )
        self.events.add_event("context_request",
                              adder=self._connect_slot,
                              adder_args=(self.graph.signal_context_request,
                                          self.on_context_request
                                          ),
                              remover=self._disconnect_slot,
                              remover_args=(self.graph.signal_context_request,
                                            self.on_context_request
                                            )
                              )
        self.events.add_event("attribute_field_input_accepted",
                              adder=self._connect_slot,
                              adder_args=(self.attribute_context.signal_input_accepted,
                                          self.on_attribute_input_accepted),
                              remover=self._disconnect_slot,
                              remover_args=(self.attribute_context.signal_input_accepted,
                                            self.on_attribute_input_accepted
                                            )
                              )
        self.events.add_event("host_node_created",
                              adder=self._connect_slot,
                              adder_args=(self.graph.signal_host_node_created,
                                          self.on_host_node_created
                                          ),
                              remover=self._disconnect_slot,
                              remover_args=(self.graph.signal_host_node_created,
                                            self.on_host_node_created
                                            )
                              )
        self.events.add_event("attribute_created",
                              adder=self._connect_slot,
                              adder_args=(self.graph.signal_AttrCreated,
                                          self.on_attribute_created
                                          ),
                              remover=self._disconnect_slot,
                              remover_args=(self.graph.signal_AttrCreated,
                                            self.on_attribute_created)
                              )
        self.events.add_event("socket_created",
                              adder=self._connect_slot,
                              adder_args=(self.graph.signal_node_socket_created,
                                          self.on_socket_created
                                          ),
                              remover=self._disconnect_slot,
                              remover_args=(self.graph.signal_node_socket_created,
                                            self.on_socket_created
                                            )
                              )
        self.events.add_event("plug_created",
                              adder=self._connect_slot,
                              adder_args=(self.graph.signal_node_plug_created,
                                          self.on_plug_created
                                          ),
                              remover=self._disconnect_slot,
                              remover_args=(self.graph.signal_node_plug_created,
                                            self.on_plug_created
                                            )
                              )

    def on_creation_field_request(self):
        self.creation_field.open()

    def on_search_field_request(self):
        self.search_field.open()

    def on_context_request(self, widget):
        """ opens the field or context widgets based on widget type

        Args:
            widget: Nodz or NodeItem or SocketItem or PlugItem instance

        Returns:

        """
        _to_open = None
        if isinstance(widget, Nodz):
            _to_open = self.context
        elif isinstance(widget, NodeItem):
            _to_open = self.attribute_context
        else:
            pass

        if _to_open:
            _to_open.open()

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

    def on_search_input_accepted(self, node_name):
        """ selects and focus the node by the given name from the searchfield

        Args:
            node_name: name of an existing node

        Returns:

        """
        if node_name in self.nodes_dict:
            self.nodes_dict[node_name].setSelected(True)
            self.graph._focus()

    def on_attribute_input_accepted(self, attribute_name):
        self.graph.attribute_context.close()

    def on_host_node_created(self, node, node_type):
        """ allows us to modify the NodeItem when a corresponding host node was created

        Args:
            node: NodeItem
            node_type: original node type of equally host node object

        Returns:

        """
        print node_type
        # we will store the original node type
        node.node_type = node_type

        # create default plug on node
        self.graph.createAttribute(node, name="message", dataType="message", index=0)

    def on_host_node_deleted(self, node_name):
        pass

    def on_search_field_opened(self):
        self.search_field.available_items = self.all_node_names

    def on_attribute_created(self, node_name, index):
        node = self.nodes_dict[node_name]
        # check if attribute is a socket in graph
        if node.sockets:
            sockets = [socket for socket in node.sockets if node.sockets[socket].index == index]
            if sockets and len(sockets) != 1:
                raise ValueError("Could not find socket to emit signal on creation")
            else:
                socket = sockets[0]
                if socket:
                    self.graph.signal_node_socket_created.emit(node.sockets[socket])
        # and check if it is a plug in graph
        if node.plugs_dict:
            plugs = [plug for plug in node.plugs_dict if node.plugs_dict[plug].index == index]
            if plugs and len(plugs) != 1:
                raise ValueError("Could not find plug to emit signal on creation")
            else:
                plug = plugs[0]
                if plug:
                    self.graph.signal_node_plug_created.emit(node.plugs_dict[plug])

    def on_socket_created(self, socket_item):
        pass

    def on_plug_created(self, plug_item):
        pass