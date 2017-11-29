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


def on_node_name_changed(callable):

    def _get_names(node, prevName, clientData):
        current_name = pmc.PyNode(node).name()
        if prevName and (current_name != prevName):
            result = callable(current_name, prevName)
            return result

    return om.MNodeMessage.addNameChangedCallback(om.MObject(), _get_names)


def on_node_deleted(callable):

    def _get_name(node, clientData):
        node_name = pmc.PyNode(node).name()
        result = callable(node_name)
        return result

    return om.MDGMessage.addNodeRemovedCallback(_get_name)


def on_node_created(callable):

    def _get_name_and_type(node, clientData):
        node = pmc.PyNode(node)
        result = callable(node.name(), node.nodeType())
        return result

    return om.MDGMessage.addNodeAddedCallback(_get_name_and_type)


def on_connection_made(callable):

    def _get_plug_names(srcPlug, destPlug, made, clientData):
        src_plug = pmc.PyNode(srcPlug)
        dest_plug = pmc.PyNode(destPlug)
        if made:
            result = callable(src_plug.name(), dest_plug.name())
            return result

    return om.MDGMessage.addConnectionCallback(_get_plug_names)


def on_disconnection_made(callable):

    def _get_plug_names(srcPlug, destPlug, made, clientData):
        src_plug = pmc.PyNode(srcPlug)
        dest_plug = pmc.PyNode(destPlug)
        if not made:
            result = callable(src_plug.name(), dest_plug.name())
            return result

    return om.MDGMessage.addConnectionCallback(_get_plug_names)


def on_before_scene_open(callable):
    return om.MSceneMessage.addCallback(om.MSceneMessage.kBeforeOpen, callable)


def on_after_scene_open(callable):
    return om.MSceneMessage.addCallback(om.MSceneMessage.kAfterOpen, callable)


def on_before_new_scene(callable):
    return om.MSceneMessage.addCallback(om.MSceneMessage.kBeforeNew, callable)


def on_after_new_scene(callable):
    return om.MSceneMessage.addCallback(om.MSceneMessage.kAfterNew, callable)


def on_before_import(callable):
    return om.MSceneMessage.addCallback(om.MSceneMessage.kBeforeImport, callable)


def on_after_import(callable):
    return om.MSceneMessage.addCallback(om.MSceneMessage.kAfterImport, callable)


def on_before_plugin_load(callable):

    def _get_plugins(strs, *args, **kwargs):
        if not strs[1] == "coconodz_maya":
            return callable()

    return om.MSceneMessage.addStringArrayCallback(om.MSceneMessage.kAfterPluginLoad, _get_plugins)


def on_after_plugin_load(callable):

    def _get_plugins(strs, *args, **kwargs):
        if not strs[1] == "coconodz_maya":
            return callable()

    return om.MSceneMessage.addStringArrayCallback(om.MSceneMessage.kAfterPluginLoad, _get_plugins)


def on_before_scene_changes(callable, relevants=RELEVANT_BEFORE_SCENE_CALLBACKS):

    callback_ids = []

    for relevant in relevants:
        if relevant == "before_open":
            callback_ids.append(on_before_scene_open(callable))
        elif relevant == "before_new":
            callback_ids.append(on_before_new_scene(callable))
        elif relevant == "before_import":
            callback_ids.append(on_before_import(callable))
        elif relevant == "before_plugin":
            callback_ids.append(on_before_plugin_load(callable))
        else:
            raise NotImplementedError

    return callback_ids


def on_after_scene_changes(callable, relevants=RELEVANT_AFTER_SCENE_CALLBACKS):

    callback_ids = []

    for relevant in relevants:
        if relevant == "after_open":
            callback_ids.append(on_after_scene_open(callable))
        elif relevant == "after_new":
            callback_ids.append(on_after_new_scene(callable))
        elif relevant == "after_import":
            callback_ids.append(on_after_import(callable))
        elif relevant == "after_plugin":
            callback_ids.append(on_after_plugin_load(callable))
        else:
            raise NotImplementedError

    return callback_ids


def add_template_custom_content(node_name):
    AEHook(node_name)
