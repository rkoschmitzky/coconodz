import pymel.core as pmc
import maya.OpenMayaUI as omui

from coconodz import Qt


DESIRED_HOOK = "AETemplateCustomContent"
OWNER = "CocoNodz"


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
        self.callCustom(self.initialize_nodzgraph_button, self.update_nodegraph_button, self.layout_title)
        self.endScrollLayout()
        self.endLayout()

    def initialize_nodzgraph_button(self, attr):
        """ adds our custom widgets

        """
        pmc.setUITemplate('attributeEditorTemplate', pushTemplate=True)

        pmc.cmds.columnLayout(adj=True)
        maya_button = pmc.button("nodegraph_eval", label=self.nodegraph_button_title)
        ptr = omui.MQtUtil.findControl(maya_button)
        button = Qt.QtCompat.wrapInstance(long(ptr), Qt.QtWidgets.QPushButton)
        button.clicked.connect(self.open_nodzgraph)

        pmc.setUITemplate('attributeEditorTemplate', popTemplate=True)

    def update_nodegraph_button(self, attr):
        pass

    def hook_shading_engine(self):
        """ checks if layout belongs to shadingEngine and adds our layout

        """
        if self.node and self.node.type() == "shadingEngine":
            self._add_layout()

    def open_nodzgraph(self):
        """ to patch in the Nodzgraph class

        Returns:

        """
        pass


def remove_template_custom_content():
    """ removes all callbacks for the DESIRED_HOOK

    Returns:

    """
    pmc.callbacks(clearCallbacks=True, hook=DESIRED_HOOK, owner=OWNER)
    rebuild_attribute_editor()


def rebuild_attribute_editor():
    """ rebuilds the attribute editor

    This should be called after removing a AETemplateCustomContent callback

    Returns:

    """
    edForm = pmc.melGlobals['gAttributeEditorForm']
    if pmc.layout(edForm, query=True, exists=True):
        children = pmc.layout(edForm, query=True, childArray=True)
        if children:
            pmc.deleteUI(children[0])
            pmc.mel.attributeEditorVisibilityStateChange(1, "")