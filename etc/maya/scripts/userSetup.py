import pymel.core as pmc

def add_template_custom_content(nodeName):
    from ..ae import AEHook

    AEHook(nodeName)


pmc.callbacks(addCallback=add_template_custom_content,
              hook='AETemplateCustomContent',
              owner="coconodz")


