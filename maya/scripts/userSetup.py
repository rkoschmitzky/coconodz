import pymel.core as pmc
import maya.cmds as cmds


def add_template_custom_content(nodeName):
    from coconodz.maya.ae.hooks import AEHook

    AEHook(nodeName)


pmc.callbacks(addCallback=add_template_custom_content, hook='AETemplateCustomContent', owner="coconodz")


