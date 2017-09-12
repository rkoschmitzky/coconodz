import coconodz.nodegraph as nodegraph
from coconodz.etc.katana.qtutilities import get_katana_main_window


class Nodzgraph(nodegraph.Nodegraph):

    def __init__(self, parent=get_katana_main_window()):
        super(Nodzgraph, self).__init__(parent)