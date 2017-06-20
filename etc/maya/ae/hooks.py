import pymel.core as pmc
import maya.OpenMayaUI as omui

from Qt import QtCore, QtWidgets

from etc.maya.qtutilities import wrapinstance

class AEHook(pmc.ui.AETemplate):
    """ AETemplateCustomContent

    This adds our custom stuff to the AETemplate and can be used to hook
    different nodetype templates. It stores custom ui elements as qt widgets
    and let us modify them when needed.
    """
    def __init__(self, nodeName):
        super(AEHook, self).__init__(nodeName)

        self.node = pmc.PyNode(nodeName)
        self.nodegraph_button = None
        self.layout_title = "CocoNodz"
        self.nodegraph_button_title = "Open Nodegraph"

        # hooking shading engines
        self.hook_shading_engine()

    def _add_layout(self):
        """ predefine layout and content

        """
        self.beginLayout(self.layout_title, collapse=False)
        self.beginScrollLayout()
        self.callCustom(self.initialize_nodegraph_button, self.update_nodegraph_button, self.layout_title)
        self.endScrollLayout()
        self.endLayout()

    def initialize_nodegraph_button(self, attr):
        """ adds our custom widgets

        """
        pmc.setUITemplate('attributeEditorTemplate', pushTemplate=True)

        pmc.cmds.columnLayout(adj=True)
        maya_button = pmc.button("nodegraph_eval", label=self.nodegraph_button_title)
        ptr = omui.MQtUtil.findControl(maya_button)
        self.button = wrapinstance(long(ptr), QtWidgets.QPushButton)

        pmc.setUITemplate('attributeEditorTemplate', popTemplate=True)

    def update_nodegraph_button(self, attr):
        pass

    def hook_shading_engine(self):
        """ checks if layout belongs to shadingEngine and adds our layout

        """
        if self.node and self.node.type() == "shadingEngine":
            self._add_layout()