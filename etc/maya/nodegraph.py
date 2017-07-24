import pymel.core as pmc
from Qt import (QtWidgets,
                QtGui,
                QtCore
                )

from etc.maya.qtutilities import maya_main_window
from etc.maya import applib

import _nodegraph
from lib import BaseWindow

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin


class MayaBaseWindow(MayaQWidgetDockableMixin, BaseWindow):
    """ getting the DockableMixin class in to provide all
    docking possibilities

    """
    def __init__(self, parent):
        super(MayaBaseWindow, self).__init__(parent)


class Nodzgraph(_nodegraph.Nodegraph):
    """ Maya Nodegraph widget implementation

    """
    def __init__(self, parent=maya_main_window(), creation_items=pmc.listNodeTypes("shader")):
        super(Nodzgraph, self).__init__(parent, creation_items)

        # just providing docking features for Maya 2017 and newer
        if int(pmc.about(api=True)) >= 201700:
            self.window = MayaBaseWindow(parent)

    def open(self):
        """ opens the Nodegraph with dockable configuration settings

        Returns:

        """
        super(Nodzgraph, self).open(self.configuration.maya.dockable,
                                    self.configuration.maya.area,
                                    self.configuration.maya.floating
                                    )

    def on_host_node_created(self, node, node_type):
        """ slot override

        This adds a maya node of the given node type and renames the
        corresponding nodegraph node

        Args:
            node: NodeItem
            node_type: maya node type

        Returns:

        """
        host_node = pmc.createNode(node_type)
        self.graph.editNode(node, newName=host_node.name())

        super(Nodzgraph, self).on_host_node_created(node, node_type)

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
