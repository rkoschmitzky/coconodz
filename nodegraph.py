import logging

from coconodz import Qt

import nodz_main
import nodz_utils

from coconodz.lib import (BaseWindow,
                          GraphContext,
                          BackdropContext,
                          SearchField,
                          RenameField,
                          AttributeContext,
                          Backdrop,
                          ConfiguationMixin)
from coconodz.events import (Events,
                             SuppressEvents
                             )

_COCONODZ_LOG = logging.getLogger(name="CocoNodz")
LOG = logging.getLogger(name="CocoNodz.nodegraph")


class Basegraph(object):
    """ base graph class that should defined all available properties and methods

    """

    def __init__(self, *args, **kwargs):
        super(Basegraph, self).__init__()

        self._all_nodes = {}
        self._all_backdrops = []

    # the current Nodz implementation stores the
    # node as tuple, which is not really clear to us
    # why. lets handle node querying bettter by providing
    # some useful properties
    @property
    def nodes_dict(self):
        return self._all_nodes

    @property
    def all_nodes(self):
        return [_[-1] for _ in self._all_nodes.items()]

    @property
    def all_node_names(self):
        return self._all_nodes.keys()

    @property
    def selected_nodes(self):
        return [_ for _ in self.all_nodes if _.isSelected()]

    @property
    def selected_node_names(self):
        return [_.name for _ in self.selected_nodes if _.isSelected()]

    @property
    def all_backdrops(self):
        return self._all_backdrops

    @property
    def all_backdrop_names(self):
        return [_.name for _ in self.all_backdrops]

    @property
    def selected_backdrops(self):
        return [_ for _ in self.all_backdrops if _.isSelected()]

    @property
    def selected_backdrop_names(self):
        return [_.name for _ in self.selected_backdrops]

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

    def create_backdrop(self):
        raise NotImplementedError

    def on_creation_field_request(self):
        raise NotImplementedError

    def on_search_field_request(self):
        raise NotImplementedError

    def on_layout_request(self):
        raise NotImplementedError

    def on_rename_field_request(self):
        raise NotImplementedError

    def on_rename_input_accepted(self, new_node_name):
        raise NotImplementedError

    def on_context_request(self, widget):
        raise NotImplementedError

    def on_creation_input_accepted(self, node_type):
        raise NotImplementedError

    def on_search_field_opened(self):
        raise NotImplementedError

    def on_search_input_accepted(self, node_name):
        raise NotImplementedError

    def on_attribute_input_accepted(self, node_name, attribute_name):
        raise NotImplementedError

    def on_node_created(self, node):
        raise NotImplementedError

    def on_after_node_created(self, node):
        raise NotImplementedError

    def on_node_name_changed(self, node, old_name, new_name):
        raise NotImplementedError

    def on_node_selected(self):
        raise NotImplementedError

    def on_nodes_deleted(self, nodeitems_list):
        raise NotImplementedError

    def on_about_attribute_create(self, node_name, attribute_name):
        raise NotImplementedError

    def on_plug_created(self, plug_item):
        raise NotImplementedError

    def on_socket_created(self, socket_item):
        raise NotImplementedError

    def on_connection_made(self, connection_item):
        raise NotImplementedError

    def on_disconnection_made(self, connection_item):
        raise NotImplementedError

    def on_plug_connected(self, source_node_name, plug_name, destination_node_name, socket_name):
        raise NotImplementedError

    def on_plug_disconnected(self, source_node_name, plug_name, destination_node_name, socket_name):
        raise NotImplementedError

    def on_socket_connected(self, source_node_name, plug_name, destination_node_name, socket_name):
        raise NotImplementedError

    def on_socket_disconnected(self, source_node_name, plug_name, destination_node_name, socket_name):
        raise NotImplementedError

    def on_host_node_created(self, node_name, node_type):
        raise NotImplementedError

    def on_host_node_deleted(self, node_name):
        raise NotImplementedError

    def on_host_node_name_changed(self, new_name, old_name):
        raise NotImplementedError

    def on_host_nodes_selected(self, node_name):
        raise NotImplementedError

    def on_host_node_deselected(self, node_name):
        raise NotImplementedError

    def on_host_connection_made(self, plug_name, socket_name):
        raise NotImplementedError

    def on_host_disconnection_made(self, plug_name, socket_name):
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

    def clean_active_graph(self):
        raise NotImplementedError

    def save_active_graph(self, filepath):
        raise NotImplementedError

    def load_into_graph(self, filepath):
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


class ItemSignals(Qt.QtCore.QObject):
    """ signals we provide for all items

    Unfortunately we are not able to provide custom
    signals when subclassing QGraphicsItems.
    """

    signal_context_request = Qt.QtCore.Signal(object)
    signal_attr_created = Qt.QtCore.Signal(object)
    signal_socket_created = Qt.QtCore.Signal(object)
    signal_plug_created = Qt.QtCore.Signal(object)
    signal_name_changed = Qt.QtCore.Signal(object)

    def __init__(self):
        Qt.QtCore.QObject.__init__(self)


class BackdropItem(Backdrop):
    """ extends the Backdrop class

    """

    signals = ItemSignals()
    signal_context_request = signals.signal_context_request

    def __init__(self, *args, **kwargs):
        super(BackdropItem, self).__init__(*args, **kwargs)

    def mousePressEvent(self, event):
        """ extend the mousePressEvent

        We are adding a context widget request on RMB click here
        Args:
            event:

        Returns:

        """
        if event.button() == Qt.QtCore.Qt.RightButton:
            self.signal_context_request.emit(self)
        else:
            super(BackdropItem, self).mousePressEvent(event)


class NodeItem(nodz_main.NodeItem):
    """ extends the nodz_main.NodeItem class

    Original implementation customization
    """

    signals = ItemSignals()
    signal_context_request = signals.signal_context_request
    signal_attr_created = signals.signal_attr_created
    signal_socket_created = signals.signal_socket_created
    signal_plug_created = signals.signal_plug_created
    signal_name_changed = signals.signal_name_changed

    def __init__(self, name, alternate, preset, config):
        super(NodeItem, self).__init__(name, alternate, preset, config)

        self._node_type = None
        self._plugs_dict = {}
        self._sockets_dict = {}
        self._connections = []

        # unfortunately the original NodeItem implementation doesn't store the config
        # by default
        self._config = config

    @property
    def node_type(self):
        """ holds the nodes node type

        Returns: string node type

        """
        return self._node_type

    @node_type.setter
    def node_type(self, value):
        """ sets the nodes node type

        Args:
            value: node type string

        Returns:

        """
        assert isinstance(value, basestring)
        self._node_type = value

    @property
    def connections(self):
        """ holds all the connections to the node

        Returns: ConnectionItem list

        """
        return self._connections

    def append_connection(self, connection):
        """ appends the stored node connection to the connections list

        Args:
            connection: ConnectionItem instance

        Returns:

        """
        assert isinstance(connection, ConnectionItem)
        self._connections.append(connection)

    def remove_connection(self, connection):
        """ removes a stored node connection from stored node connections list

        Args:
            connection: ConnectionItem instance

        Returns:

        """
        if connection in self.connections:
            self.connections.remove(connection)

    def mousePressEvent(self, event):
        """ extend the mousePressEvent

        We are adding a context widget request on RMB click here
        Args:
            event:

        Returns:

        """
        if event.button() == Qt.QtCore.Qt.RightButton:
            self.signal_context_request.emit(self)
        else:
            super(NodeItem, self).mousePressEvent(event)

    def add_attribute(self, name, add_mode=None, plug=True, socket=True, data_type=""):
        """ wrapper around the _createAttribute method that allows better customization of attribute generation

        Args:
            name:
            add_mode: defines where on the node the attribute will be placed, "top", "bottom", "alphabetical"
            plug: if True the attribute will be added as plug
            socket: if True the attribute will be added as socket
            data_type: attribute data type

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
                self.signal_plug_created.emit(self.plugs[name])
            if socket:
                self.sockets[name].node = self.sockets[name].parentItem()
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

        # update the connections paths
        for connection in self.connections:
            connection.target_point = connection.target.center()
            connection.source_point = connection.source.center()
            connection.updatePath()


class ConnectionItem(nodz_main.ConnectionItem):
    """ extends the nodz_main.ConnectionItem class

    Original implementation customization
    """

    def __init__(self, source_point, target_point, source, target, mode):
        super(ConnectionItem, self).__init__(source_point, target_point, source, target)
        self._mode = mode
        self.setAcceptHoverEvents(True)
        self.setFlag(Qt.QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setFlag(Qt.QtWidgets.QGraphicsItem.ItemIsSelectable)

    def updatePath(self):
        """ overrides the original method

        We added support for configurable path shapes here

        Returns:

        """
        self.setPen(self._pen)

        path = Qt.QtGui.QPainterPath()
        path.moveTo(self.source_point)
        dx = (self.target_point.x() - self.source_point.x()) * 0.5
        dy = self.target_point.y() - self.source_point.y()
        ctrl1 = Qt.QtCore.QPointF(self.source_point.x() + dx, self.source_point.y() + dy * 0)
        ctrl2 = Qt.QtCore.QPointF(self.source_point.x() + dx, self.source_point.y() + dy * 1)

        if not self._mode:
            # using cubic bezier as default
            path.cubicTo(ctrl1, ctrl2, self.target_point)
        elif self._mode == "line":
            path.lineTo(self.target_point)
        elif self._mode == "bezier":
            path.cubicTo(ctrl1, ctrl2, self.target_point)

        self.setPath(path)


class Nodz(ConfiguationMixin, nodz_main.Nodz):
    """ extends the nodz_main.Nodz class

    Original implementation customization
    """

    signal_node_created = Qt.QtCore.Signal(object)
    signal_nodes_deleted = Qt.QtCore.Signal(object)
    signal_after_node_created = Qt.QtCore.Signal(object)
    signal_node_name_changed = Qt.QtCore.Signal(object, str, str)
    signal_node_plug_created = Qt.QtCore.Signal(object)
    signal_node_socket_created = Qt.QtCore.Signal(object)
    signal_connection_made = Qt.QtCore.Signal(object)
    signal_disconnection_made = Qt.QtCore.Signal(object)
    signal_about_attribute_create = Qt.QtCore.Signal(str, str)
    signal_context_request = Qt.QtCore.Signal(object)
    signal_creation_field_request = Qt.QtCore.Signal()
    signal_search_field_request = Qt.QtCore.Signal()
    signal_rename_field_request = Qt.QtCore.Signal()
    signal_layout_request = Qt.QtCore.Signal()

    def __init__(self, parent):
        # unfortunately nodz_main.Nodz expects a default config file at the same level as the module
        # we pass our default here
        super(Nodz, self).__init__(parent, configPath=self.BASE_CONFIG_PATH)
        self.initialize_configuration()
        self.config = self.configuration_data

        self._rename_field = RenameField(self)
        self._search_field = SearchField(self)
        self._creation_field = SearchField(self)
        self._context = GraphContext(self)
        self._attribute_context = AttributeContext(self)
        self._backdrop_context = BackdropContext(self)

    @property
    def rename_field(self):
        return self._rename_field

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

    @property
    def backdrop_context(self):
        """ holds the backdrop context widget

        Returns: AttributeContext instance

        """

        return self._backdrop_context

    def keyPressEvent(self, event):
        """ overrides the keyPressEvent

        We are adding more key press events here
        Args:
            event:

        Returns:

        """
        if event.key() not in self.pressedKeys:
            self.pressedKeys.append(event.key())
        if event.key() == Qt.QtCore.Qt.Key_Delete:
            self._deleteSelectedNodes()
        if (event.key() == Qt.QtCore.Qt.Key_F and
            event.modifiers() == Qt.QtCore.Qt.NoModifier):
            self._focus()
        if (event.key() == Qt.QtCore.Qt.Key_S and
            event.modifiers() == Qt.QtCore.Qt.NoModifier):
            self._nodeSnap = True
        if event.key() == Qt.QtCore.Qt.Key_Tab:
            self.signal_creation_field_request.emit()
        if (event.key() == Qt.QtCore.Qt.Key_F and
            event.modifiers() == Qt.QtCore.Qt.ControlModifier):
            self.signal_search_field_request.emit()
        if event.key() == Qt.QtCore.Qt.Key_L:
            self.signal_layout_request.emit()
        if event.key() == Qt.QtCore.Qt.Key_R:
            self.signal_rename_field_request.emit()

        # Emit signal.
        self.signal_KeyPressed.emit(event.key())
        super(Nodz, self).keyPressEvent(event)

    def mousePressEvent(self, event):
        """ extends the mousePressEvent

        We are adding a context widget request on RMB click here
        Args:
            event:

        Returns:

        """
        if not self.scene().itemAt(self.mapToScene(event.pos())):
            if (event.button() == Qt.QtCore.Qt.RightButton and
                        event.modifiers() == Qt.QtCore.Qt.NoModifier):
                self.signal_context_request.emit(self.scene().itemAt(self.mapToScene(event.pos())))
        super(Nodz, self).mousePressEvent(event)

    def _deleteSelectedNodes(self):
        """ overrides original method

        Let us emit a signal on nodes deletion
        Returns:

        """
        self.signal_nodes_deleted.emit([_ for _ in self.scene().selectedItems() if isinstance(_, NodeItem)])
        super(Nodz, self)._deleteSelectedNodes()


    def retrieve_creation_position(self):
        """ retrieves the position where something should be created

        Depending on the configuration we define where to place nodes/backdrops/dots etc
        Returns: QPointF

        """
        if self.configuration.node_placement == "cursor":
            position = Qt.QtCore.QPointF(self.mapToScene(self.mapFromGlobal(Qt.QtGui.QCursor.pos())))
        elif self.configuration.node_placement == "creation_field":
            position = Qt.QtCore.QPointF(self.mapToScene(self.mapFromGlobal(self.creation_field.pos())))
        else:
            position = None

        return position

    def create_node(self, name, position=None, alternate=False, node_type="default"):
        """ wrapper around Nodz.createNode() to extend behavior

        Args:
            name: node name
            position: if unset it will calculate the position based on the configuration
            alternate: The attribute color alternate state, if True, every 2 attribute the color will be slightly darker
            node_type: node type

        Returns: NodeItem instance

        """
        if not position:
            position = self.retrieve_creation_position()

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
        """ overrides the createNode method

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

    def delete_node(self, name):
        raise NotImplementedError

    def rename_node(self, node, new_name):
        """ gives specified node a new name

        Args:
            node: NodeItem instance
            new_name: new name

        Returns:

        """
        old_name = node.name
        if old_name != new_name:
            self.editNode(node, new_name)
            self.signal_node_name_changed.emit(node, old_name, new_name)

    def apply_data_type_color_to_connection(self, connection):
        """ takes and applies the data type color to the connection

        Args:
            connection: ConnectionItemInstance

        Returns:

        """
        # set color based on data_type
        if self.configuration.connection_inherit_datatype_color:
            if connection.plugItem:
                expected_config = "datatype_{0}".format(connection.plugItem.dataType)
            else:
                expected_config = "datatype_{0}".format(connection.socketItem.dataType)
            if hasattr(self.configuration, expected_config):
                color = nodz_utils._convertDataToColor(self.configuration_data[expected_config]["plug"])
                connection._pen = color

    def connect_attributes(self, plug, socket):
        """ creates a new ConnectionItem instance that connects plug and socket

        Args:
            plug:
            socket:

        Returns:

        """
        connection = self.createConnection(plug, socket)

        return connection

    def createConnection(self, plug, socket):
        """ extends the createConnection

        We are adding the possibility to apply data type color to the connection here
        Args:
            plug:
            socket:

        Returns:

        """
        connection = ConnectionItem(plug.center(), socket.center(), plug, socket, self.configuration.connection_interpolation)

        connection.plugNode = plug.parentItem().name
        connection.plugAttr = plug.attribute
        connection.plugItem = plug
        connection.socketNode = socket.parentItem().name
        connection.socketAttr = socket.attribute
        connection.socketItem = socket

        plug.connect(socket, connection)
        socket.connect(plug, connection)

        # let us apply the corresponding data type color
        self.apply_data_type_color_to_connection(connection)

        self.scene().addItem(connection)

        connection.updatePath()

        return connection

    def get_shared_connection(self, plug, socket):
        """ finds the shared connection item

        Args:
            plug: PlugItem instance
            socket: SocketItem instance

        Returns: ConnectionItem instance

        """
        all_connections = plug.connections + socket.connections
        shared_connections = list(set(all_connections))
        if shared_connections:
            if len(shared_connections) != 1:
                LOG.error("Multiple shared connections on plug '{0}' and socket '{1}'".format(plug, socket))
            else:
                return shared_connections[0]

    def disconnect_attributes(self, plug, socket):
        """ removes a shared connection

        Args:
            plug: PlugItem instance
            socket: SocketItem instance

        Returns:

        """
        connection = self.get_shared_connection(plug, socket)
        if connection:
            connection._remove()

    def on_context_request(self, node_item):
        """ placeholder method, has to be overriden in Nodegraph class

        Args:
            node_item:

        Returns:

        """
        pass

    def on_plug_created(self, plug_item):
        pass

    def on_socket_created(self, socket_item):
        pass

    def layout_nodes(self, node_names=None):
        """ rearranges node positions

        Notes:
            Adopted from implementation of user https://github.com/glm-ypinczon

        Args:
            node_names: expects a list of node names otherwise it will consider all available nodes

        Returns:

        """
        node_width = 300  # default value, will be replaced by node.baseWidth + margin when iterating on the first node
        margin = self.configuration.layout_margin_size
        scene_nodes = self.scene().nodes.keys()
        if not node_names:
            node_names = scene_nodes
        root_nodes = []
        already_placed_nodes = []

        # root nodes (without connection on the plug)
        for node_name in node_names:
            node = self.scene().nodes[node_name]
            if node is not None:
                node_width = node.baseWidth + margin
                is_root = True
                for plug in node.plugs.values():
                    is_root &= (len(plug.connections) == 0)
                if is_root:
                    root_nodes.append(node)

        max_graph_width = 0
        root_graphs = []
        for root_node in root_nodes:
            root_graph = list()
            root_graph.append([root_node])

            current_graph_level = 0
            do_next_graph_level = True
            while do_next_graph_level:
                do_next_graph_level = False
                for _node in range(len(root_graph[current_graph_level])):
                    node = root_graph[current_graph_level][_node]
                    for attr in node.attrs:
                        if attr in node.sockets:
                            socket = node.sockets[attr]
                            for connection in socket.connections:
                                if len(root_graph) <= current_graph_level + 1:
                                    root_graph.append(list())
                                root_graph[current_graph_level + 1].append(connection.plugItem.parentItem())
                                do_next_graph_level = True
                current_graph_level += 1

            graph_width = len(root_graph) * (node_width + margin)
            max_graph_width = max(graph_width, max_graph_width)
            root_graphs.append(root_graph)

        # update scne rect if needed
        if max_graph_width > self.scene().width():
            scene_rect = self.scene().sceneRect()
            scene_rect.setWidth(max_graph_width)
            self.scene().setSceneRect(scene_rect)

        base_ypos = margin
        for root_graph in root_graphs:
            # set positions...
            # middle of the view
            current_xpos = max(0, 0.5 * (self.scene().width() - max_graph_width)) + max_graph_width - node_width
            next_base_ypos = base_ypos
            for nodes_at_level in root_graph:
                current_ypos = base_ypos
                for node in nodes_at_level:
                    if len(node.plugs) > 0:
                        if len(node.plugs.values()[0].connections) > 0:
                            parent_pos = node.plugs.values()[0].connections[0].socketItem.parentItem().pos()
                            current_xpos = parent_pos.x() - node_width
                    if (node not in already_placed_nodes) and (node.name in node_names):
                        already_placed_nodes.append(node)
                        node_pos = Qt.QtCore.QPointF(current_xpos, current_ypos)
                        node.setPos(node_pos)

                    current_ypos += node.height + margin
                    next_base_ypos = max(next_base_ypos, current_ypos)
                current_xpos -= node_width
            base_ypos = next_base_ypos

        self.scene().updateScene()

    def get_node_by_name(self, node_name):
        """ placeholder method, has to be overriden in Nodegraph class

        Args:
            node_name:

        Returns:

        """
        pass


class Nodegraph(Basegraph):
    """ main Nodegraph that should be accessable without any host application

    """

    def __init__(self, parent=None):
        super(Nodegraph, self).__init__(parent=parent)

        # this can be overriden in subclasses to allow mixing in other classes
        # that are not host agnostic
        self._window = BaseWindow(parent)
        self._events = Events()

        # create the graphingscene
        self._graph = Nodz(self._window)

        # apply logging verbosity
        _COCONODZ_LOG.setLevel(self.configuration.output_verbosity.upper())

        self.graph.initialize()

        # to query nodes our own way
        self._all_nodes = self.graph.scene().nodes

        # add the graph to our window
        self.window.central_layout.addWidget(self.graph)

        # set slots
        self.register_events()

        self.creation_field.available_items = self.configuration.available_node_types + ["backdrop"]

        self.graph.delete_node = self._delete_node
        self.graph.get_node_by_name = self.get_node_by_name

        self._initialized = True

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
    def rename_field(self):
        """ holds the rename field instance

        Returns: RenameField instance

        """
        return self.graph.rename_field

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

    @property
    def backdrop_context(self):
        """holds the backdrop context widget"""
        return self.graph.backdrop_context

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
        LOG.info("Saving configuration to {0}".format(filepath))
        return self.graph.save_configuration(filepath)

    def load_configuration(self, configuration_file):
        """

        Args:
            configuration_file:

        Returns:

        """
        self.graph.load_configuration(configuration_file)
        # @todo update functionality

    def clear(self):
        """ removes all nodes and connections from graph

        This will not emit any deletion signals
        Returns:

        """
        self.graph.clearGraph()
        # clean nodes_dict
        self._all_nodes = {}

    def save_graph(self, filepath):
        self.graph.saveGraph(filepath)

    @SuppressEvents(["after_node_created", "socket_created", "plug_created", "connection_made", "plug_connected", "socket_connected"])
    def display_host_nodes(self, nodes_dict, attributes_dict={}, connections_dict={}):
        """ will add nodes their attributes and connections to nodegraph

        This will not emit any creation signals and is meant to be a display and not a creation utility function
        Args:
            nodes_dict: dictionary that includes the node as key and the node type as value
            attributes_dict: dictionary that holds the attribute as key and a type and data_type description like this
            {"shader1.color": {"node_type": "shader"
                               "type": "plug"
                               "data_type": "color"
                               }
            }
            connections_dict: dictionary that includes a pair of attributes

        Returns:

        """
        # @todo estimate creation position
        for node_name, node_type in nodes_dict.iteritems():
            self.graph.create_node(name=node_name, node_type=node_type)

        self._create_attributes(attributes_dict)
        self._create_connections(connections_dict)

    @SuppressEvents("node_deleted")
    def undisplay_node(self, node_name):
        """ will remove nodes and their connections from nodegraph

        This will not emit any deletion signals and is meant to be an undisplay and not a deletion utilitiy function
        Args:
            node_name: name of the node

        Returns:

        """
        self.graph.delete_node(node_name)

    def _filter_attributes_dict(self):
        pass

    def _delete_node(self, name):
        """ delete a node by given name and emit signal

        Args:
            name: node name

        Returns:

        """
        node = self.get_node_by_name(name)
        if node:
            self.graph.deleteNode(node)

    def _connect_slot(self, signal, slot):
        signal.connect(slot)

    def _disconnect_slot(self, signal, slot):
        signal.disconnect(slot)

    def __assert_attribute(self, attribute):
        """ simple attribute formatting assertion

        Args:
            attribute: attribute using a '.' separator formatting, e.g.: "material.color", "surface.tension"

        Returns:

        """
        _msg = "Unexpected formatting. Expect '.' as node attribute separator."
        assert len(attribute.split(".")) != 1, _msg

    def _create_nodes(self, attributes_dict):
        """ creates nodes in nodegraph if they are not existing

        Args:
            attributes_dict: dictionary that holds the attribute as key and a type and data_type description like this
            {"shader1.color": {"node_type": "shader"
                               "type": "plug"
                               "data_type": "color"
                               }
            }
        Returns:

        """
        for attribute, value in attributes_dict:
            self.__assert_attribute(attribute)
            _msg = "Unexpected formatting. Expected dictionary holding a 'node_type' key."
            assert (isinstance(value, dict) and "node_type" in value), _msg

            node = self.get_node_by_name(attribute.split(".")[0])
            if not node:
                self.graph.create_node(name=self.get_node_by_name(attribute.split(".")[0]),
                                       node_type=value["node_type"])

    def _create_attributes(self, attributes_dict):
        """ creates attributes for availailable nodes in nodegraph

        Args:
            attributes_dict: dictionary that holds the attribute as key and a type and data_type description like this
            {"shader1.color": {"node_type": "shader"
                               "type": "plug"
                               "data_type": "color"
                               }
            }

        Returns:

        """

        def _create_node_attr(name, plug_or_socket, data_type):
            self.__assert_attribute(name)
            node = self.get_node_by_name(name.split(".")[0])
            if node:
                attribute_name = name.split(".")[1]
                if plug_or_socket == "plug":
                    node.add_attribute(attribute_name, plug=True, socket=False, data_type=data_type)
                elif plug_or_socket == "socket":
                    node.add_attribute(attribute_name, plug=False, socket=True, data_type=data_type)
                elif plug_or_socket == "slot":
                    node.add_attribute(attribute_name, plug=True, socket=True, data_type=data_type)
            else:
                LOG.info("Node '{0}' doesn't exist in graph yet.".format(name.split(".")[0]))

        for key, value in attributes_dict.iteritems():
            msg = "Unexpected formatting. Expected dictionary holding a 'type' and 'data_type' key"
            assert (isinstance(value, dict) and "type" in value), msg
            assert (isinstance(value, dict) and "data_type" in value), msg

            _create_node_attr(key, value["type"], value["data_type"])

    def _create_connections(self, connections_dict):
        """ creates connections for available attributes in nodegraph

        Args:
            connections_dict: dictionary that holds the source attribute as key and destination attribute as value like this
            {"lambert1.color": "surfaceShader2.color"}

        Returns:

        """
        for plug, socket in connections_dict.iteritems():
            self.__assert_attribute(plug)
            self.__assert_attribute(socket)
            source_node = self.get_node_by_name(plug.split(".")[0])
            destination_node = self.get_node_by_name(socket.split(".")[0])
            if source_node and destination_node:
                self.__handle_connection(plug, socket, True)

    def _get_shared_connection(self, source_node_name, plug_name, destination_node_name, socket_name):
        """ helper function to get the ConnectionItem based on node-, plug and socket names

        Args:
            source_node_name: source node name
            plug_name: plug name
            destination_node_name: destination name
            socket_name: socket name

        Returns: ConnectionItem instance

        """
        plug = self.get_plug_by_name("{0}.{1}".format(source_node_name, plug_name))
        socket = self.get_socket_by_name("{0}.{1}".format(destination_node_name, socket_name))
        return self.graph.get_shared_connection(plug, socket)

    def register_events(self):
        """ sets up all events that will be needed to run CocoNodz without integration

        Integration doesn't have to re-register certain events, all events here have to be
        generic enough, their callback functions can be extended or overriden in the specific
        integration

        Returns:

        """
        # patching per node slot
        self.graph.on_context_request = self.on_context_request
        self.graph.on_plug_created = self.on_plug_created
        self.graph.on_socket_created = self.on_socket_created

        # @todo use a event factory to remove boilerplate
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
        self.events.add_event("layout_request",
                              adder=self._connect_slot,
                              adder_args=(self.graph.signal_layout_request,
                                          self.on_layout_request
                                          ),
                              remover=self._disconnect_slot,
                              remover_args=(self.graph.signal_layout_request,
                                            self.on_layout_request
                                            )
                              )
        self.events.add_event("rename_field_request",
                              adder=self._connect_slot,
                              adder_args=(self.graph.signal_rename_field_request,
                                          self.on_rename_field_request
                                          ),
                              remover=self._disconnect_slot,
                              remover_args=(self.graph.signal_rename_field_request,
                                            self.on_rename_field_request
                                            )
                              )
        self.events.add_event("rename_field_input_accepted",
                              adder=self._connect_slot,
                              adder_args=(self.rename_field.signal_input_accepted,
                                          self.on_rename_input_accepted
                                          ),
                              remover=self._connect_slot,
                              remover_args=(self.rename_field.signal_input_accepted,
                                            self.on_rename_input_accepted
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
        self.events.add_event("node_deleted",
                              adder=self._connect_slot,
                              adder_args=(self.graph.signal_nodes_deleted,
                                          self.on_nodes_deleted
                                          ),
                              remover=self._disconnect_slot,
                              remover_args=(self.graph.signal_nodes_deleted,
                                            self.on_nodes_deleted
                                            )
                              )
        self.events.add_event("node_name_changed",
                              adder=self._connect_slot,
                              adder_args=(self.graph.signal_node_name_changed,
                                          self.on_node_name_changed
                                          ),
                              remover=self._disconnect_slot,
                              remover_args=(self.graph.signal_node_name_changed,
                                            self.on_node_name_changed
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
        self.events.add_event("disconnection_made",
                              adder=self._connect_slot,
                              adder_args=(self.graph.signal_disconnection_made,
                                          self.on_disconnection_made
                                          ),
                              remover=self._disconnect_slot,
                              remover_args=(self.graph.signal_disconnection_made,
                                              self.on_disconnection_made
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
        self.events.add_event("plug_disconnected",
                              adder=self._connect_slot,
                              adder_args=(self.graph.signal_PlugDisconnected,
                                          self.on_plug_disconnected
                                          ),
                              remover=self._disconnect_slot,
                              remover_args=(self.graph.signal_PlugDisconnected,
                                              self.on_plug_disconnected
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
        self.events.add_event("socket_disconnected",
                              adder=self._connect_slot,
                              adder_args=(self.graph.signal_SocketDisconnected,
                                          self.on_socket_disconnected
                                          ),
                              remover=self._disconnect_slot,
                              remover_args=(self.graph.signal_SocketDisconnected,
                                              self.on_socket_disconnected
                                            )
                              )

    def layout_selected_nodes(self):
        """ rearranges node positions of selected nodes

        Returns:

        """
        if self.selected_nodes:
            self.graph.layout_nodes(self.selected_node_names)

    def create_backdrop(self, use_selection=True):
        """ creates a backdrop

        Args:
            use_selection: if True it will adjust the backdrop bounds to embrace selected nodes

        Returns: BackdropItem instance

        """
        bounds = self.configuration.backdrop_bounds
        color = self.configuration.backdrop_color
        border_color = self.configuration.backdrop_border_color
        font = self.configuration.backdrop_font
        title_font_size = self.configuration.backdrop_title_font_size
        description_font_size = self.configuration.backdrop_description_font_size

        if not use_selection or not self.selected_nodes:
            pos = self.graph.retrieve_creation_position()
            bounds = (pos.x(), pos.y(), bounds[2], bounds[3])
            backdrop = BackdropItem("Backdrop",
                                bounds=bounds,
                                color=color,
                                border_color=border_color,
                                font=font,
                                title_font_size=title_font_size,
                                descriptipn_font_size=description_font_size
                                )
        else:
            selection_bounds = self.graph._getSelectionBoundingbox()
            backdrop = BackdropItem("Backdrop",
                                bounds=(selection_bounds.x() - 50,
                                            selection_bounds.y() - 100,
                                            selection_bounds.width() + 100,
                                            selection_bounds.height() + 200,
                                            ),
                                color=color,
                                border_color=border_color,
                                font=font,
                                title_font_size=title_font_size,
                                descriptipn_font_size=description_font_size
                                )

        backdrop.signal_context_request.connect(self.on_context_request)
        self.graph.scene().addItem(backdrop)
        return backdrop

    def on_creation_field_request(self):
        """ should be called when a creation_field_request signal was emitted

        It will open the creation field widget

        Returns:

        """
        self.creation_field.open()

    def on_search_field_request(self):
        """ should be called when a search_field_request was emitted

        It will open the search field widget

        Returns:

        """
        self.search_field.open()

    def on_layout_request(self):
        """ should be called when a layout_request was emitted

        It will start the layout process

        Returns:

        """
        self.layout_selected_nodes()

    def on_rename_field_request(self):
        """ should be called when a rename_field_request was emitted

        It will open the rename field widget

        Returns:

        """
        self.rename_field.open()

    def on_rename_input_accepted(self, new_node_name):
        """ should be called when a rename_input_accepted signal was emitted

        Args:
            new_node_name: new node name

        Returns:

        """
        for node in self.selected_nodes:
            self.graph.rename_node(node, new_node_name)

    def on_context_request(self, widget):
        """ should be called when a context_request signal was emitted

        Opens the specific field or context widgets based on widget type

        Args:
            widget: Nodz or NodeItem or SocketItem or PlugItem instance

        Returns:

        """

        _to_open = None
        if not widget:
            _to_open = self.graph.context
        elif isinstance(widget, NodeItem):
            self.attribute_context.setProperty("node_name", widget.name)
            _to_open = self.attribute_context
        elif isinstance(widget, BackdropItem):
            _to_open = self.graph.backdrop_context
            self.graph.backdrop_context.backdrop_item = widget
        else:
            pass

        if _to_open:
            _to_open.open()

        return _to_open

    def on_creation_input_accepted(self, node_type):
        """ should be called when a creation field widgets input_accepted signal was emitted

        creates a NodeItem of given type and emit additional signals

        Args:
            node_type: type of the node

        Returns:

        """

        if node_type == "backdrop":
            self.create_backdrop()
        else:
            self.graph.create_node(node_type, node_type=node_type)

    def on_search_field_opened(self):
        """ should be called when a search_fields opened signal was emitted

        Updated the available search field items to represent the available nodes in nodegraph

        Returns:

        """
        self.search_field.available_items = self.all_node_names

    def on_search_input_accepted(self, node_name):
        """ should be called when the search field widgets input_accepted signal was emitted

        Selects and focus the node by the given name from the searchfield

        Args:
            node_name: name of a node (expect an existing one)

        Returns:

        """
        if node_name in self.nodes_dict:
            self.nodes_dict[node_name].setSelected(True)
            self.graph._focus()

    def on_attribute_input_accepted(self, node_name, attribute_name):
        """ should be called when the attribute field widgets input_accepted signal was emitted

        Will close the attribute field widget and emit a different signal that sends the node
        and chosen attribute name

        Args:
            node_name: name of the node
            attribute_name: name of the node that is selected in the widget

        Returns:

        """
        self.graph.attribute_context.close()
        self.graph.signal_about_attribute_create.emit(node_name, attribute_name)

    def on_node_created(self, node):
        """ should be called when the a node_created signal was emitted

        Will add the node to our nodes dict and emit a after_node_created signal
        Args:
            node: NodeItem instance

        Returns:

        """
        self.nodes_dict[node.name] = node
        if node:
            self.graph.signal_after_node_created.emit(node)

    def on_after_node_created(self, node):
        # create default plug on node
        if self.configuration.default_plug or self.configuration.default_socket:
            node.add_attribute(name=self.configuration.default_attribute_name,
                               plug=self.configuration.default_plug,
                               socket=self.configuration.default_socket,
                               data_type=self.configuration.default_attribute_data_type)

    def on_node_name_changed(self, node, old_name, new_name):
        pass

    def on_node_selected(self):
        pass

    def on_nodes_deleted(self, nodeitems_list):
        pass

    def on_about_attribute_create(self, node_name, attribute_name):
        node = self.get_node_by_name(node_name)
        if node:
            node.add_attribute(name=attribute_name)

    def on_plug_created(self, plug_item):
        pass

    def on_socket_created(self, socket_item):
        pass

    def on_connection_made(self, connection_item):
        self.graph.apply_data_type_color_to_connection(connection_item)

        self.get_node_by_name(connection_item.plugNode).append_connection(connection_item)
        self.get_node_by_name(connection_item.socketNode).append_connection(connection_item)

    def on_disconnection_made(self, connection_item):
        self.get_node_by_name(connection_item.plugNode).remove_connection(connection_item)
        self.get_node_by_name(connection_item.socketNode).remove_connection(connection_item)

    def on_plug_connected(self, source_node_name, plug_name, destination_node_name, socket_name):
        if destination_node_name and socket_name:
            connection = self._get_shared_connection(source_node_name, plug_name, destination_node_name,
                                                           socket_name)
            self.graph.signal_connection_made.emit(connection)

    def on_plug_disconnected(self, source_node_name, plug_name, destination_node_name, socket_name):
        if source_node_name and destination_node_name:
            connection = self._get_shared_connection(source_node_name, plug_name, destination_node_name,
                                                           socket_name)
            if connection.socketItem:
                self.graph.signal_disconnection_made.emit(connection)
            connection.plugItem = None

    def on_socket_connected(self, source_node_name, plug_name, destination_node_name, socket_name):
        if source_node_name and plug_name:
            connection = self._get_shared_connection(source_node_name, plug_name, destination_node_name,
                                                           socket_name)
            self.graph.signal_connection_made.emit(connection)

    def on_socket_disconnected(self, source_node_name, plug_name, destination_node_name, socket_name):
        if source_node_name and destination_node_name:
            connection = self._get_shared_connection(source_node_name, plug_name, destination_node_name,
                                                           socket_name)
            if connection.plugItem:
                self.graph.signal_disconnection_made.emit(connection)
            connection.socketItem = None

    def on_host_node_created(self, node_name, node_type):
        if not node_type in self.creation_field.available_items:
            LOG.info("Host node type '{0}' not available to Nodzgraph.".format(node_type))
        else:
            node = self.get_node_by_name(node_name)
            if node and node.node_type == node_type:
                self.graph.rename_node(node, node_name)
            elif node and node_type != node_type:
                LOG.warning("Host node misstmatch to graph node." +
                            "Expected nodetype '{0}' got '{1}'".format(node.node_type, node_type))
            else:
                self.graph.create_node(name=node_name, node_type=node_type)

    def on_host_node_deleted(self, node_name):
        node = self.get_node_by_name(node_name)
        if node:
            self.graph.deleteNode(node)

    def on_host_node_name_changed(self, new_name, old_name):
        if new_name != old_name:
            node = self.get_node_by_name(old_name)
            if node:
                self.graph.rename_node(node, new_name)

    def on_host_nodes_selected(self, node_name):
        node = self.get_node_by_name(node_name)
        node.setSelected(True)

    def on_host_node_deselected(self, node_name):
        node = self.get_node_by_name(node_name)
        node.setSelected(False)

    def __handle_connection(self, plug_name, socket_name, state):
        self.__assert_attribute(plug_name)
        self.__assert_attribute(socket_name)

        _msg = "{0} '{1}' doesn't exist yet. Skipped connecting."

        plug = self.get_plug_by_name(plug_name)
        socket = self.get_socket_by_name(socket_name)
        if plug and socket:
            if state:
                self.graph.connect_attributes(plug, socket)
            else:
                self.graph.disconnect_attributes(plug, socket)
        if not plug:
            LOG.warning(_msg.format("plug", plug_name))
        if not socket:
            LOG.warning(_msg.format("socket", socket_name))

    def on_host_connection_made(self, plug_name, socket_name):
        self.__handle_connection(plug_name, socket_name, 1)

    def on_host_disconnection_made(self, plug_name, socket_name):
        self.__handle_connection(plug_name, socket_name, 0)
