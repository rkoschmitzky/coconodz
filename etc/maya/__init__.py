from nodegraph import Nodegraph

from nodz_main import Nodz
from Qt import QtWidgets


class Nodzgraph(Nodz, Nodegraph):

    def __init__(self, parent=None):
        super(Nodzgraph, self).__init__(parent)
        self.initialize()

    def open(self):
        self.show()


