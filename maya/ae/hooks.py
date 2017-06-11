import pymel.core as pmc
import maya.OpenMayaUI as omui


class BaseTemplate(pmc.ui.AETemplate):

    def addControl(self, control, label=None, **kwargs):
        pmc.ui.AETemplate.addControl(self, control, label=label, **kwargs)

    def beginLayout(self, name, collapse=True):
        pmc.ui.AETemplate.beginLayout(self, name, collapse=collapse)


class AEHook(BaseTemplate):
    def __init__(self, nodeName):
        BaseTemplate.__init__(self, nodeName)
        self.thisNode = None
        self.node = pmc.PyNode(self.nodeName)
        self.buildBody(nodeName)

    def buildBody(self, nodeName):
        node = pmc.PyNode(nodeName)
        if node.type() == "shadingEngine":
            self.thisNode = pmc.PyNode(nodeName)
            self.beginLayout("CoconodZ", collapse=1)
            self.endLayout()
