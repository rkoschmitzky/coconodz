import pymel.core as pmc
from Qt import QtWidgets

import _nodegraph
from etc.maya.qtutilities import maya_main_window

from Qt import QtWidgets

class Nodzgraph(_nodegraph.Nodegraph):

    def __init__(self, parent=maya_main_window()):
        super(Nodzgraph, self).__init__(parent)


def maya_api_version():
    return int(pmc.about(api=True))