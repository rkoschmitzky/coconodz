import logging

import pymel.core as pmc
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from coconodz.etc.maya.ae.hooks import (DESIRED_HOOK,
                                        OWNER,
                                        remove_template_custom_content
                                        )
from coconodz.etc.maya.qtutilities import maya_main_window
from coconodz.etc.maya import (applib,
                               callbacks,
                               decorators
                               )
from coconodz.events import SuppressEvents
import coconodz.nodegraph as nodegraph
from coconodz.lib import BaseWindow


LOG = logging.getLogger(name="CocoNodz.maya.nodegraph")


class MayaBaseWindow(MayaQWidgetDockableMixin, BaseWindow):
    """ getting the DockableMixin class in to provide all
    docking possibilities

    """
    def __init__(self, parent):
        super(MayaBaseWindow, self).__init__(parent)


class Nodzgraph(nodegraph.Nodegraph):
    """ Maya Nodegraph widget implementation

    """
    def __init__(self, parent=maya_main_window()):
        super(Nodzgraph, self).__init__(parent)

        # just providing docking features for Maya 2017 and newer
        if int(pmc.about(api=True)) >= 201700:
            self.window = MayaBaseWindow(parent)

        # patch open_nodzgraph function
        callbacks.AEHook.open_nodzgraph = self.open

        # add node gategories
        self.append_available_node_categories()

        # setting the default attribute
        self.configuration.default_slot = True
        self.configuration.default_plug = True
        self.configuration.default_attribute_name = "message"
        self.configuration.default_attribute_data_type = "message"

    def open(self):
        """ opens the Nodegraph with dockable configuration settings

        Returns:

        """
        super(Nodzgraph, self).open(dockable=self.configuration.maya.docked,
                                    area=self.configuration.maya.dock_area,
                                    allowedArea=self.configuration.maya.allowed_dock_areas,
                                    floating=self.configuration.maya.floating,
                                    width=self.configuration.maya.width,
                                    height=self.configuration.maya.height
                                    )

    def register_events(self):
        super(Nodzgraph, self).register_events()

        # @todo remove boilerplate
        self.events.add_event("ShadingEngine_template_hook",
                              adder=pmc.callbacks,
                              adder_kwargs={"addCallback": callbacks.add_template_custom_content,
                                            "hook": DESIRED_HOOK,
                                            "owner": OWNER
                                            },
                              remover=remove_template_custom_content
                              )
        self.events.add_event("host_node_name_changed",
                              adder=callbacks.add_node_name_changed_callback,
                              adder_args=(self.on_host_node_renamed, )
                              )
        self.events.attach_remover("host_node_name_changed",
                                   callable=callbacks.remove_callbacks_only,
                                   callable_args=(self.events.data["host_node_name_changed"]["id_list"], )
                                   )
        self.events.add_event("host_node_deleted",
                              adder=callbacks.add_node_deleted_callback,
                              adder_args=(self.on_host_node_deleted, )
                              )
        self.events.attach_remover("host_node_deleted",
                                   callable=callbacks.remove_callbacks_only,
                                   callable_args=(self.events.data["host_node_deleted"]["id_list"], )
                                   )
        self.events.add_event("host_connection_made",
                              adder=callbacks.add_connection_made_callback,
                              adder_args=(self.on_host_connection_made, )
                              )
        self.events.attach_remover("host_connection_made",
                                   callable=callbacks.remove_callbacks_only,
                                   callable_args=(self.events.data["host_connection_made"]["id_list"], )
                                   )
        self.events.add_event("host_disconnection_made",
                              adder=callbacks.add_disconnection_made_callback,
                              adder_args=(self.on_host_disconnection_made, )
                              )
        self.events.attach_remover("host_disconnection_made",
                                   callable=callbacks.remove_callbacks_only,
                                   callable_args=(self.events.data["host_disconnection_made"]["id_list"], )
                                   )
        self.events.add_event("before_scene_changes",
                              adder=callbacks.add_before_scene_callbacks,
                              adder_args=(self.on_before_scene_changes, )
                              )
        self.events.attach_remover("before_scene_changes",
                                   callable=callbacks.remove_callbacks_only,
                                   callable_args=(self.events.data["before_scene_changes"]["id_list"], )
                                   )
        self.events.add_event("after_scene_changes",
                              adder=callbacks.add_after_scene_callbacks,
                              adder_args=(self.on_after_scene_changes, )
                              )
        self.events.attach_remover("after_scene_changes",
                                   callable=callbacks.remove_callbacks_only,
                                   callable_args=(self.events.data["after_scene_changes"]["id_list"], )
                                   )

    def append_available_node_categories(self):
        """ appends available node types in categories

        Returns:

        """
        available_node_types = self.graph.creation_field.available_items
        for types in self.configuration.maya.available_node_categories:
            node_types = pmc.listNodeTypes(types)
            for node_type in node_types:
                if not node_type in available_node_types:
                    available_node_types.append(node_type)

        self.graph.creation_field.available_items = available_node_types

    def display_selected_host_nodes(self):
        """ adds selected host nodes and corresponding connections to the graph

        Returns:

        """
        nodes_dict = {node.name(): node.nodeType() for node in pmc.selected()
                      if node.nodeType() in self.creation_field.available_items}
        nodes_attributes = applib.get_connected_attributes_in_node_tree(pmc.selected(),
                                                                        node_types=self.creation_field.available_items)
        node_connections = applib.get_connections(pmc.selected())
        self.display_host_nodes(nodes_dict=nodes_dict,
                                attributes_dict=nodes_attributes,
                                connections_dict=node_connections)

    def on_creation_input_accepted(self, node_type):
        node = pmc.createNode(node_type)
        self.on_host_node_created(node.name(), node_type=node_type)

    def on_context_request(self, widget):
        _widget = super(Nodzgraph, self).on_context_request(widget)

        if isinstance(widget, nodegraph.Nodz):
            _widget.available_items = []
        elif isinstance(widget, nodegraph.NodeItem):
            node = pmc.PyNode(_widget.property("node_name"))
            if node:
                # only update items if the node has changed
                if _widget.property("last_node_name") != node.name():
                    _widget.available_items = applib.get_attribute_tree(node)
                    _widget.setProperty("last_node_name", node.name())
        else:
            pass

    def on_about_attribute_create(self, node_name, attribute_name):
        """ slot override

        Args:
            node_name:
            attribute_name:

        Returns:

        """
        node = self.get_node_by_name(node_name)
        attribute_type = pmc.PyNode("{0}.{1}".format(node_name, attribute_name)).type()
        node.add_attribute(attribute_name, data_type=attribute_type)

    def on_before_scene_changes(self, *args):
        self.events.pause_events(exclude=["before_scene_changes", "after_scene_changes"])

    @decorators.execute_deferred
    def on_after_scene_changes(self, *args):
        self.events.resume_paused_events()

    def on_node_created(self, node):
        """ slot extension

        Args:
            node:

        Returns:

        """
        super(Nodzgraph, self).on_node_created(node)

    def on_host_node_created(self, node_name, node_type):
        """ slot extension

        Args:
            node_name:
            node_type:

        Returns:

        """
        super(Nodzgraph, self).on_host_node_created(node_name, node_type)

    @SuppressEvents("host_connection_made")
    def on_connection_made(self, connection):
        """ slot extension

        Args:
            connection: ConnectionItem instance

        Returns:

        """

        plug_name = "{0}.{1}".format(connection.plugNode, connection.plugAttr)
        socket_name = "{0}.{1}".format(connection.socketNode, connection.socketAttr)

        try:
            slot1 = pmc.PyNode(plug_name)
            slot2 = pmc.PyNode(socket_name)
            slot1 >> slot2

            super(Nodzgraph, self).on_connection_made(connection)
        except:
            LOG.warning("Can not connect {0} to {1}".format(plug_name, socket_name))

    @SuppressEvents("host_disconnection_made")
    def on_disconnection_made(self, connection):

        plug_name = "{0}.{1}".format(connection.plugNode, connection.plugAttr)
        socket_name = "{0}.{1}".format(connection.socketNode, connection.socketAttr)

        try:
            slot1 = pmc.PyNode(plug_name)
            slot2 = pmc.PyNode(socket_name)
            slot1 // slot2

            super(Nodzgraph, self).on_disconnection_made(connection)
        except:
            LOG.warning("Can not disconnect {0} to {1}".format(plug_name, socket_name))

    @SuppressEvents(["connection_made", "plug_connected", "socket_connected"])
    def on_host_connection_made(self, plug_name, socket_name):
        """ slot extension

        Args:
            plug_name: name of the plug
            socket_name: name of the socket

        Returns:

        """
        super(Nodzgraph, self).on_host_connection_made(plug_name, socket_name)

    @SuppressEvents("host_node_deleted")
    def on_nodes_deleted(self, nodeitems_list):
        """ slot override

        Args:
            nodeitems_list:

        Returns:

        """
        for node in nodeitems_list:
            try:
                pmc.delete(node.name)
            except RuntimeWarning:
                LOG.warning("Not able to delete host node '{0}'".format(node.name), exc_info=True)
