import pymel.core as pmc
from Qt import QtWidgets

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

    def open(self):
        super(Nodzgraph, self).open(self.configuration.maya.dockable,
                                    self.configuration.maya.area,
                                    self.configuration.maya.floating
                                    )