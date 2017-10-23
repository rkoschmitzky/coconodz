import logging

import maya.OpenMaya as om
import pymel.core as pmc

from coconodz.etc.maya.ae.hooks import AEHook

LOG = logging.getLogger(name="CocoNodz.nodegraph")
RELEVANT_BEFORE_SCENE_CALLBACKS = ["before_open", "before_new", "before_import", "before_plugin"]
RELEVANT_AFTER_SCENE_CALLBACKS = ["after_open", "after_new", "after_import", "after_plugin"]



def remove_callback(callback_id):
    try:
        om.MDGMessage.removeCallback(callback_id)
    except RuntimeError:
        LOG.error("Not able to remove callback id {0}.".format(str(callback_id)) +
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
        if prevName and (current_name != prevName):
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


def add_before_scene_open_callback(callable):
    return om.MSceneMessage.addCallback(om.MSceneMessage.kBeforeOpen, callable)


def add_after_scene_open_callback(callable):
    return om.MSceneMessage.addCallback(om.MSceneMessage.kAfterOpen, callable)


def add_before_new_scene_callback(callable):
    return om.MSceneMessage.addCallback(om.MSceneMessage.kBeforeNew, callable)


def add_after_new_scene_callback(callable):
    return om.MSceneMessage.addCallback(om.MSceneMessage.kAfterNew, callable)


def add_before_import_callback(callable):
    return om.MSceneMessage.addCallback(om.MSceneMessage.kBeforeImport, callable)


def add_after_import_callback(callable):
    return om.MSceneMessage.addCallback(om.MSceneMessage.kAfterImport, callable)


def add_before_plugin_load_callback(callable):

    def _get_plugins(strs, *args, **kwargs):
        if not strs[1] == "coconodz_maya":
            return callable()

    return om.MSceneMessage.addStringArrayCallback(om.MSceneMessage.kAfterPluginLoad, _get_plugins)


def add_after_plugin_load_callback(callable):

    def _get_plugins(strs, *args, **kwargs):
        if not strs[1] == "coconodz_maya":
            return callable()

    return om.MSceneMessage.addStringArrayCallback(om.MSceneMessage.kAfterPluginLoad, _get_plugins)


def add_before_scene_callbacks(callable, relevants=RELEVANT_BEFORE_SCENE_CALLBACKS):

    callback_ids = []

    for relevant in relevants:
        if relevant == "before_open":
            callback_ids.append(add_before_scene_open_callback(callable))
        elif relevant == "before_new":
            callback_ids.append(add_before_new_scene_callback(callable))
        elif relevant == "before_import":
            callback_ids.append(add_before_import_callback(callable))
        elif relevant == "before_plugin":
            callback_ids.append(add_before_plugin_load_callback(callable))
        else:
            raise NotImplementedError

    return callback_ids


def add_after_scene_callbacks(callable, relevants=RELEVANT_AFTER_SCENE_CALLBACKS):

    callback_ids = []

    for relevant in relevants:
        if relevant == "after_open":
            callback_ids.append(add_after_scene_open_callback(callable))
        elif relevant == "after_new":
            callback_ids.append(add_after_new_scene_callback(callable))
        elif relevant == "after_import":
            callback_ids.append(add_after_import_callback(callable))
        elif relevant == "after_plugin":
            callback_ids.append(add_after_plugin_load_callback(callable))
        else:
            raise NotImplementedError

    return callback_ids


def add_template_custom_content(node_name):
    AEHook(node_name)
