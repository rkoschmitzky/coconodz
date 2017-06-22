import logging
import os
import sys

import pymel.core as pmc

PACKAGE_NAME = "coconodz"
VAR_NAME = "{0}_STARTUP".format(PACKAGE_NAME.upper())

_LOG = logging.getLogger("Coconodz.Startup")

# adding python paths
if VAR_NAME in os.environ:
    COCONODZ_PARENT = os.path.normpath(os.environ[VAR_NAME].split(PACKAGE_NAME, 1)[0].strip(";"))
    sys.path.append(COCONODZ_PARENT)
    sys.path.append(os.path.join(COCONODZ_PARENT, PACKAGE_NAME))
    sys.path.append(os.path.join(COCONODZ_PARENT, PACKAGE_NAME, "site-packages"))

from etc.maya.ae.hooks import AEHook

_LOG.info("Launching Startup Script")


def add_template_custom_content(nodeName):
    AEHook(nodeName)


pmc.callbacks(addCallback=add_template_custom_content,
              hook='AETemplateCustomContent',
              owner="coconodz")