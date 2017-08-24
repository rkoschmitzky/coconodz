import logging

import pymel.core as pmc
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from etc.maya.qtutilities import maya_main_window
from etc.maya import applib
from etc.maya import callbacks
from events import SuppressEvents
import _nodegraph
from lib import BaseWindow


LOG = logging.getLogger(name="CocoNodz.maya.nodegraph")
# todo add allowed nodetypes to configuration
NODES = list(set(pmc.listNodeTypes("shader") + pmc.listNodeTypes("texture")))

class MayaBaseWindow(MayaQWidgetDockableMixin, BaseWindow):
    """ getting the DockableMixin class in to provide all
    docking possibilities

    """
    def __init__(self, parent):
        super(MayaBaseWindow, self).__init__(parent)


class Nodzgraph(_nodegraph.Nodegraph):
    """ Maya Nodegraph widget implementation

    """
    def __init__(self, parent=maya_main_window(), creation_items=NODES):
        super(Nodzgraph, self).__init__(parent, creation_items)

        # just providing docking features for Maya 2017 and newer
        if int(pmc.about(api=True)) >= 201700:
            self.window = MayaBaseWindow(parent)

        callbacks.AEHook.open_nodzgraph = self.open

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
                                            "hook": "AETemplateCustomContent",
                                             "owner": "coconodz"
                                            },
                              remover=pmc.callbacks,
                              remover_kwargs={"removeCallback": callbacks.add_template_custom_content,
                                              "hook": "AETemplateCustomContent",
                                              "owner": "coconodz"}
                          )
        self.events.add_event("host_node_name_changed",
                              adder=callbacks.add_node_name_changed_callback,
                              adder_args=(self.on_host_node_renamed, )
                              )
        self.events.attach_remover("host_node_name_changed",
                                   callable=callbacks.remove_callbacks_only,
                                   callable_args=(self.events.data["host_node_name_changed"]["id_list"], )
                                   )
        self.events.add_event("host_node_created",
                              adder=callbacks.add_node_created_callback,
                              adder_args=(self.on_host_node_created, )
                              )
        self.events.attach_remover("host_node_created",
                                   callable=callbacks.remove_callbacks_only,
                                   callable_args=(self.events.data["host_node_created"]["id_list"], )
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

    def on_creation_input_accepted(self, node_type):
        pmc.createNode(node_type)

    def on_after_node_created(self, node):
        node.add_attribute(name="message", socket=False, data_type="message")

    def on_context_request(self, widget):
        _widget = super(Nodzgraph, self).on_context_request(widget)

        if isinstance(widget, _nodegraph.Nodz):
            _widget.available_items = []
        elif isinstance(widget, _nodegraph.NodeItem):
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

    @SuppressEvents("host_node_created")
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
    def on_connection_made(self, node_name1, slot_name1, node_name2, slot_name2):
        """ slot extension

        Args:
            node_name1:
            slot_name1:
            node_name2:
            slot_name2:

        Returns:

        """
        slot1 = pmc.PyNode("{0}.{1}".format(node_name1, slot_name1))
        slot2 = pmc.PyNode("{0}.{1}".format(node_name2, slot_name2))
        slot1 >> slot2

    @SuppressEvents("connection_made")
    def on_host_connection_made(self, plug_name, socket_name):
        """ slot extension

        Args:
            plug_name:
            socket_name:

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


def open_nodzgraph():
    window = Nodzgraph()
    window.open()
