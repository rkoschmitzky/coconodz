import pymel.core as pmc
import maya.cmds as cmds


def add_template_custom_content(nodeName):
    from coconodz.maya.ae.hooks import AEHook

    #layout = pmc.setParent(q=True)
    AEHook(nodeName)#, layout)


pmc.callbacks(addCallback=add_template_custom_content, hook='AETemplateCustomContent', owner="coconodz")


