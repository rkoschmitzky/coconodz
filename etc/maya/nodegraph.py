from ...nodegraph import Nodegraph

from Qt import QtWidgets

from etc.maya.qtutilities import maya_main_window

class Nodzgraph(Nodegraph):

    def __init__(self, parent=maya_main_window()):
        super(Nodzgraph, self).__init__(parent)