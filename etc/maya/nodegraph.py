import pymel.core as pmc
from Qt import (QtWidgets,
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

        # register slots
        self._setup_slots()

    def open(self):
        """ opens the Nodegraph with dockable configuration settings

        Returns:

        """
        super(Nodzgraph, self).open(self.configuration.maya.dockable,
                                    self.configuration.maya.area,
                                    self.configuration.maya.floating
                                    )

    @QtCore.Slot(object)
    def create_node(self, node_type):
        """ creates shading node in Maya and in graph

        Args:
            node_type: type of the node

        Returns:

        """
        node = pmc.createNode(node_type)
        self.graph.createNode(name=node.name(), preset='node_preset_1')

    def _setup_slots(self):
        """ connects the available slots

        Returns:

        """
        self.search_field.signal_input_accepted.connect(self.create_node)

