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

        event_name_prefix = {callbacks: "host_"}
        events_data = {callbacks: ["node_created",
                                   "node_name_changed",
                                   "node_deleted",
                                   "connection_made",
                                   "disconnection_made",
                                   "before_scene_changes",
                                   "after_scene_changes"]
                       }
        # events factory to avoid unnecessary boilerplate
        for obj, obj_events in events_data.iteritems():
            for event in obj_events:
                event_name = event_name_prefix[obj] + event
                self.events.add_event(event_name,
                                      adder=obj.__getattribute__("on_" + event),
                                      adder_args=(self.__getattribute__("on_" + event_name),
                                                  )
                                      )
                self.events.attach_remover(event_name,
                                           callable=callbacks.remove_callbacks_only,
                                           callable_args=(self.events.data[event_name]["id_list"],
                                                          )
                                           )

        # behaves too differently to be part of the factory easily
        self.events.add_event("ShadingEngine_template_hook",
                              adder=pmc.callbacks,
                              adder_kwargs={"addCallback": callbacks.add_template_custom_content,
                                            "hook": DESIRED_HOOK,
                                            "owner": OWNER
                                            },
                              remover=remove_template_custom_content
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

    def on_host_before_scene_changes(self, *args):
        self.events.pause_events(exclude=["before_scene_changes", "after_scene_changes"])

    @decorators.execute_deferred
    def on_host_after_scene_changes(self, *args):
        self.events.resume_paused_events()

    @SuppressEvents("node_created")
    def on_host_node_created(self, node_name, node_type):
        """ slot extension

        Args:
            node_name:
            node_type:

        Returns:

        """
        super(Nodzgraph, self).on_host_node_created(node_name, node_type)

    @SuppressEvents("host_node_created")
    def on_node_created(self, node):
        host_node = pmc.createNode(node.node_type)
        self.graph.rename_node(node, host_node.name())
        super(Nodzgraph, self).on_node_created(node)

    @SuppressEvents("host_node_name_changed")
    def on_node_name_changed(self, node, old_name, new_name):
        try:
            host_node = pmc.PyNode(old_name)
        except:
            LOG.warning("Node {} doesn't exist.".format(old_name))

        try:
            host_node.rename(new_name)
        except:
            LOG.warning("Not able to rename {}'".format(old_name))
        super(Nodzgraph, self).on_node_name_changed(node, old_name, new_name)

    @SuppressEvents("node_name_changed")
    def on_host_node_name_changed(self, new_name, old_name):
        super(Nodzgraph, self).on_host_node_name_changed(new_name, old_name)

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

    def on_nodes_selected(self, nodes_list):
        selection = [_.name for _ in nodes_list if not _.node_type in self.RESERVED_NODETYPES]
        pmc.select(selection)