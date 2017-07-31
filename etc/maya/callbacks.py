import maya.OpenMaya as om
import pymel.core as pmc


def add_node_name_changed_callback(callable):

    def _get_names(node, prevName, clientData):
        node = pmc.PyNode(node).name()
        result = callable(node, prevName)
        return result

    return om.MNodeMessage.addNameChangedCallback(om.MObject(), _get_names)

