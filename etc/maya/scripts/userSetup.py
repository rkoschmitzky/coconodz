import logging
import os
import sys

import pymel.core as pmc

_PACKAGE_NAME = "coconodz"
_VAR_NAME = "{0}_STARTUP".format(_PACKAGE_NAME.upper())

LOG = logging.getLogger("Coconodz.startup.Maya")

# adding python paths
if _VAR_NAME in os.environ:
    COCONODZ_PARENT = os.path.normpath(os.environ[_VAR_NAME].split(_PACKAGE_NAME, 1)[0].strip(";"))
    sys.path.append(COCONODZ_PARENT)
    sys.path.append(os.path.join(COCONODZ_PARENT, _PACKAGE_NAME))
    sys.path.append(os.path.join(COCONODZ_PARENT, _PACKAGE_NAME, "site-packages"))

from _events import Events
from etc.maya.ae.hooks import AEHook

_EVENTS = Events()
LOG.info("Launching startup Script")


def add_template_custom_content(nodeName):
    AEHook(nodeName)


_EVENTS.add_event("ShadingEngine_template_hook",
                  pmc.callbacks, adder_kwargs={
                  "addCallback":add_template_custom_content,
                  "hook":"AETemplateCustomContent",
                  "owner":"coconodz"})