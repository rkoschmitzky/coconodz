import maya.OpenMaya as om
import pymel.core as pmc


def remove_callback(callback_id):
    om.MDGMessage.removeCallback(callback_id)


def add_node_name_changed_callback(callable):

    def _get_names(node, prevName, clientData):
        current_name = pmc.PyNode(node).name()
        result = callable(current_name, prevName)
        return result

    return om.MNodeMessage.addNameChangedCallback(om.MObject(), _get_names)

