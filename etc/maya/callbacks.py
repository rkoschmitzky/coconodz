import logging

import maya.OpenMaya as om
import pymel.core as pmc

from etc.maya.ae.hooks import (AEHook,
                               rebuild_attribute_editor
                               )

LOG = logging.getLogger(name="CocoNodz.nodegraph")


def remove_callback(callback_id):
    try:
        om.MDGMessage.removeCallback(callback_id)
    except RuntimeError:
        LOG.error("Not able to remove callback id {0}.".format(callback_id) +
                  "Please check the events class for the corresponding event.", exc_info=True)


def remove_callbacks_only(id_list):
    # expect a list, loop through it and remove all callbacks
    # using the proper callback ids
    for item in id_list:
        if str(type(item)) == "<type 'PyCObject'>":
            remove_callback(item)


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


def add_connection_made_callback(callable):

    def _get_plug_names(srcPlug, destPlug, made, clientData):
        src_plug = pmc.PyNode(srcPlug)
        dest_plug = pmc.PyNode(destPlug)
        if made:
            result = callable(src_plug.name(), dest_plug.name())
            return result

    return om.MDGMessage.addConnectionCallback(_get_plug_names)


def add_disconnection_made_callback(callable):

    def _get_plug_names(srcPlug, destPlug, made, clientData):
        src_plug = pmc.PyNode(srcPlug)
        dest_plug = pmc.PyNode(destPlug)
        if not made:
            result = callable(src_plug.name(), dest_plug.name())
            return result

    return om.MDGMessage.addConnectionCallback(_get_plug_names)


def add_template_custom_content(nodeName):
    AEHook(nodeName)
