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


LOG = logging.getLogger(name="CocoNodz.nodegraph")


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

    def get_node_by_name(self, node_name):
        if node_name in self.nodes_dict:
            return self.nodes_dict[node_name]

    def get_slot_by_name(self, slot_name, plug_or_socket):
        node = self.get_node_by_name(slot_name.split(".")[0])
        name = slot_name.split(".", 1)[1]
        if node:
            if plug_or_socket == "plug":
                if name in node.plugs:
                    return node.plugs[name]
            elif plug_or_socket == "socket":
                if name in node.sockets:
                    return node.sockets[name]
            else:
                raise NotImplementedError

    def get_plug_by_name(self, plug_name):
        return self.get_slot_by_name(plug_name, "plug")

    def get_socket_by_name(self, socket_name):
        return self.get_slot_by_name(socket_name, "socket")

    def on_node_name_changed(self, old_name, new_name):
        raise NotImplementedError

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
    signal_attr_created = QtCore.Signal(object)
    signal_socket_created = QtCore.Signal(object)
    signal_plug_created = QtCore.Signal(object)

    def __init__(self, name, alternate, preset, config):
        super(NodeItem, self).__init__(name, alternate, preset, config)

        self._node_type = None
        self._plugs_dict = {}
        self._sockets_dict = {}

        # unfortunately the original NodeItem implementation doesn't store the config
        # by default
        self._config = config

    @property
    def node_type(self):
        return self._node_type

    @node_type.setter
    def node_type(self, value):
        assert isinstance(value, basestring)
        self._node_type = value

    def mousePressEvent(self, event):
        if (event.button() == QtCore.Qt.RightButton and
            event.modifiers() == QtCore.Qt.ControlModifier):
            self.signal_context_request.emit(self)
        else:
            super(NodeItem, self).mouseMoveEvent(event)

    def add_attribute(self, name, add_mode=None, plug=True, socket=True, data_type=""):
        """ wrapper around the _createAttribute method that allows better customization of attribute generation

        Args:
            name:
            add_mode:
            preset:
            plug:
            socket:
            data_type:

        Returns:

        """

        # skip process if slot already exists
        if name in self.attrs:
            return

        # closure to avoid redoing preset checking all the time
        def _do_creation():
            if data_type:
                preset = "datatype_{0}".format(data_type)
            else:
                preset = "datatype_default"
            if preset not in self._config:
                LOG.info("Attribute preset for type {0} not configured.".format(data_type))
                self._createAttribute(name, index, "datatype_default", plug, socket, data_type)
            else:
                self._createAttribute(name, index, preset, plug, socket, data_type)

            # emit specific signals
            if plug:
                self.plugs[name].node = self.plugs[name].parentItem()
                self.plugs[name].connections = []
                self.signal_plug_created.emit(self.plugs[name])
            if socket:
                self.sockets[name].node = self.sockets[name].parentItem()
                self.sockets[name].connections = []
                self.signal_socket_created.emit(self.sockets[name])

        # if no add_mode is defined take the order from the config
        if not add_mode:
            add_mode = self._config["attribute_order"]

        _allowed_modes = ["top", "bottom", "alphabetical"]
        assert add_mode in _allowed_modes, "Unknown mode. Choose from: " + "".join("'{0}' ".format(_) for _ in _allowed_modes)

        # create attribute at expected index
        if add_mode == "top":
            index = 0
            _do_creation()
        elif add_mode == "bottom":
            index = -1
            _do_creation()
        elif add_mode == "alphabetical":
            _attrs = list(self.attrs)
            _attrs.append(name)
            _sorted = sorted(_attrs)
            index = _sorted.index(name)
            _do_creation()
        else:
            raise NotImplementedError


class Nodz(ConfiguationMixin, nodz_main.Nodz):
    """ This class will let us override or extend behaviour
    for the purpose of better customization

    """

    signal_node_created = QtCore.Signal(object)
    signal_after_node_created = QtCore.Signal(object)
    signal_node_plug_created = QtCore.Signal(object)
    signal_node_socket_created = QtCore.Signal(object)
    signal_connection_made = QtCore.Signal(str, str, str, str)
    signal_about_attribute_create = QtCore.Signal(str, str)
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

    def create_node(self, name, position=None, alternate=False, node_type="default"):

        _ = "node_{0}".format(node_type)
        if hasattr(self.configuration, _):
            # and create node with included preset
            node = self.createNode(name, _, position, alternate)
        else:
            LOG.info("Node preset for type {0} not configured.".format(node_type))
            node = self.createNode(name, position=position, alternate=alternate)
        node.node_type = node_type

        self.signal_node_created.emit(node)
        return node

    def createNode(self, name="default", preset="node_default", position=None, alternate=True, node_type="default"):
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
        nodeItem.signal_plug_created.connect(self.on_plug_created)
        nodeItem.signal_socket_created.connect(self.on_socket_created)

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

    def connect_attributes(self, plug, socket):
        connection = self.createConnection(plug, socket)
        # storing connections directly on plug and socket
        plug.connections.append(connection)
        socket.connections.append(connection)

    def createConnection(self, plug, socket):
        connection = nodz_main.ConnectionItem(plug.center(), socket.center(), plug, socket)

        connection.plugNode = plug.parentItem().name
        connection.plugAttr = plug.attribute
        connection.socketNode = socket.parentItem().name
        connection.socketAttr = socket.attribute

        plug.connect(socket, connection)
        socket.connect(plug, connection)

        connection.updatePath()

        self.scene().addItem(connection)

        return connection

    def disconnect_attributes(self, plug, socket):
        pass

    def on_context_request(self, node_item):
        """ placeholder method, has to be overriden in Nodegraphclass

        Args:
            node_item:

        Returns:

        """
        pass

    def on_plug_created(self, plug_item):
        pass

    def on_socket_created(self, socket_item):
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
        self._signal_block = False

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
        """ setup events by connecting all signals and slots

        Returns:

        """
        # patching per node slot
        self.graph.on_context_request = self.on_context_request
        self.graph.on_plug_created = self.on_plug_created
        self.graph.on_socket_created = self.on_socket_created

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
        self.events.add_event("node_created",
                              adder=self._connect_slot,
                              adder_args=(self.graph.signal_node_created,
                                          self.on_node_created),
                              remover=self._disconnect_slot,
                              remover_args=(self.graph.signal_node_created,
                                            self.on_node_created)
                              )
        self.events.add_event("after_node_created",
                              adder=self._connect_slot,
                              adder_args=(self.graph.signal_after_node_created,
                                          self.on_after_node_created
                                          ),
                              remover=self._disconnect_slot,
                              remover_args=(self.graph.signal_after_node_created,
                                            self.on_after_node_created
                                            )
                              )
        self.events.add_event("about_attribute_create",
                              adder=self._connect_slot,
                              adder_args=(self.graph.signal_about_attribute_create,
                                          self.on_about_attribute_create),
                              remover=self._disconnect_slot,
                              remover_args=(self.graph.signal_about_attribute_create,
                                            self.on_about_attribute_create
                                            )
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
        self.events.add_event("connection_made",
                              adder=self._connect_slot,
                              adder_args=(self.graph.signal_connection_made,
                                          self.on_connection_made
                                          ),
                              remover=self._disconnect_slot,
                              remover_args=(self.graph.signal_connection_made,
                                              self.on_connection_made
                                            )
                              )
        self.events.add_event("plug_connected",
                              adder=self._connect_slot,
                              adder_args=(self.graph.signal_PlugConnected,
                                          self.on_plug_connected
                                          ),
                              remover=self._disconnect_slot,
                              remover_args=(self.graph.signal_PlugConnected,
                                              self.on_plug_connected
                                            )
                              )
        self.events.add_event("socket_connected",
                              adder=self._connect_slot,
                              adder_args=(self.graph.signal_SocketConnected,
                                          self.on_socket_connected
                                          ),
                              remover=self._disconnect_slot,
                              remover_args=(self.graph.signal_SocketConnected,
                                            self.on_socket_connected
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
            _to_open = self.graph.context
        elif isinstance(widget, NodeItem):
            self.attribute_context.setProperty("node_name", widget.name)
            _to_open = self.attribute_context
        else:
            pass

        if _to_open:
            _to_open.open()

        return _to_open

    def on_creation_input_accepted(self, node_type):
        """ creates a NodeItem of given type and emit additional signals

        This will always emit a host_node_created signal, which behaves like
        some kind of callback, but makes it easier for us to modify and
        reuse them.
        Args:
            node_type: type of the node

        Returns:

        """
        self.graph.create_node(node_type, node_type=node_type)

    def on_search_field_opened(self):
        self.search_field.available_items = self.all_node_names

    def on_search_input_accepted(self, node_name):
        """ selects and focus the node by the given name from the searchfield

        Args:
            node_name: name of an existing node

        Returns:

        """
        if node_name in self.nodes_dict:
            self.nodes_dict[node_name].setSelected(True)
            self.graph._focus()

    def on_attribute_input_accepted(self, node_name, attribute_name):
        self.graph.attribute_context.close()
        self.graph.signal_about_attribute_create.emit(node_name, attribute_name)

    def on_node_created(self, node):
        if node:
            self.graph.signal_after_node_created.emit(node)

    def on_after_node_created(self, node):
        # create default plug on node
        node.add_attribute(name="test", data_type="test")

    def on_about_attribute_create(self, node_name, attribute_name):
        node = self.get_node_by_name(node_name)
        if node:
            node.add_attribute(name=attribute_name)

    def on_plug_created(self, plug_item):
        pass

    def on_socket_created(self, socket_item):
        pass

    def on_connection_made(self, node_name1, slot_name1, node_name2, slot_name2):
        pass

    def on_plug_connected(self, source_node_name, source_plug_name, destination_node_name, destination_socket_name):
        if destination_node_name and destination_socket_name:
            self.graph.signal_connection_made.emit(source_node_name, source_plug_name, destination_node_name, destination_socket_name)

    def on_socket_connected(self, source_node_name, source_plug_name, destination_node_name, destination_socket_name):
        if source_node_name and source_plug_name:
            self.graph.signal_connection_made.emit(source_node_name, source_plug_name, destination_node_name, destination_socket_name)

    def on_host_node_created(self, node_name, node_type):
        node = self.get_node_by_name(node_name)
        if node and node.node_type == node_type:
            self.graph.editNode(node, node_name)
        elif node and node_type != node_type:
            LOG.warning("Host node misstmatch to graph node." +
                        "Expected nodetype '{0}' got '{1}'".format(node.node_type, node_type))
        else:
            self.graph.create_node(name=node_name, node_type=node_type)

    def on_host_node_deleted(self, node_name):
        node = self.get_node_by_name(node_name)
        if node:
            self.graph.deleteNode(node)

    def on_host_node_renamed(self, new_name, old_name):
        node = self.get_node_by_name(old_name)
        if node:
            self.graph.editNode(node, new_name)

    def on_host_nodes_selected(self, node_name):
        node = self.get_node_by_name(node_name)
        node.setSelected(True)

    def on_host_node_deselected(self, node_name):
        node = self.get_node_by_name(node_name)
        node.setSelected(False)

    def __handle_connection(self, plug_name, socket_name, state):

        plug = self.get_plug_by_name(plug_name)
        socket = self.get_socket_by_name(socket_name)
        if plug and socket:
            if state:
                self.graph.connect_attributes(plug, socket)
            else:
                # disconnect
                pass

    def on_host_connection_made(self, plug_name, socket_name):
        self.__handle_connection(plug_name, socket_name, 1)

    def on_host_disconnection_made(self, plug_name, socket_name):
        self.__handle_connection(plug_name, socket_name, 0)
