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


def add_node_deleted_callback(callable):

    def _get_name(node, clientData):
        node_name = pmc.PyNode(node).name()
        result = callable(node_name)
        return result

    return om.MDGMessage.addNodeRemovedCallback(_get_name)


def add_node_created_callback(callable):

    def _get_name_and_type(node, clientData):
        node = pmc.PyNode(node)
        result = callable(node.name(), node.nodeType())
        return result

    return om.MDGMessage.addNodeAddedCallback(_get_name_and_type)