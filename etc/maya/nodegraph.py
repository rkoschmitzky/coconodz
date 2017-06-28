import pymel.core as pmc
from Qt import (QtWidgets,
                QtGui,
                QtCore
                )

from etc.maya.qtutilities import maya_main_window

from _nodegraph import Nodegraph
from lib import BaseWindow

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin


class MayaBaseWindow(MayaQWidgetDockableMixin, BaseWindow):
    """ getting the DockableMixin class in to provide all
    docking possibilities

    """
    def __init__(self, parent):
        super(MayaBaseWindow, self).__init__(parent)


class Nodzgraph(Nodegraph):

    def __init__(self, parent=maya_main_window()):
        super(Nodzgraph, self).__init__(parent)

        # just providing docking features for Maya 2017 and newer
        if int(pmc.about(api=True)) >= 201700:
            self.window = MayaBaseWindow(parent)

        # add shaders to search field widget
        self.search_field.available_items = pmc.listNodeTypes("shader")

    def open(self):
        """ opens the Nodegraph with dockable configuration settings

        Returns:

        """
        super(Nodzgraph, self).open(self.configuration.maya.dockable,
                                    self.configuration.maya.area,
                                    self.configuration.maya.floating
                                    )

    def on_host_node_created(self, node, node_type):

        host_node = pmc.createNode(node_type)
        self.graph.editNode(node, newName=host_node.name())

        super(Nodzgraph, self).on_host_node_created(node, node_type)
